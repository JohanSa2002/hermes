from datetime import date, datetime, timedelta

import redis.asyncio as aioredis
from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import func

from app.modules.business.service import get_business_config, list_table_types
from app.modules.calendar.service import find_best_table_for_party, invalidate_slots_cache
from app.modules.reservations.models import Reservation
from app.modules.reservations.schemas import ReservationCreate, ReservationUpdate

VALID_STATUSES = {"pending", "confirmed", "cancelled", "no_show"}


async def _get_or_404(db: AsyncSession, business_id: int, reservation_id: int) -> Reservation:
    result = await db.execute(
        select(Reservation).where(
            and_(Reservation.id == reservation_id, Reservation.business_id == business_id)
        )
    )
    reservation = result.scalar_one_or_none()
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")
    return reservation


def _compute_time_end(time_start, slot_duration: int):
    base = datetime.combine(date.today(), time_start)
    return (base + timedelta(minutes=slot_duration)).time()


async def list_reservations(
    db: AsyncSession,
    business_id: int,
    filter_date: date | None = None,
    filter_status: str | None = None,
) -> list[Reservation]:
    query = select(Reservation).where(Reservation.business_id == business_id)
    if filter_date:
        query = query.where(Reservation.date == filter_date)
    if filter_status:
        query = query.where(Reservation.status == filter_status)
    query = query.order_by(Reservation.date, Reservation.time_start)
    result = await db.execute(query)
    return result.scalars().all()


async def create_reservation(
    db: AsyncSession,
    redis: aioredis.Redis,
    business_id: int,
    data: ReservationCreate,
) -> Reservation:
    config = await get_business_config(db, business_id)
    time_end = _compute_time_end(data.time_start, config.slot_duration)

    # Asignar mesa automáticamente si el negocio tiene tipos de mesa configurados
    table_type_id = None
    table_types = await list_table_types(db, business_id)
    if table_types:
        # Contar reservas por table_type en ese slot
        result = await db.execute(
            select(Reservation.table_type_id, func.count(Reservation.id))
            .where(
                and_(
                    Reservation.business_id == business_id,
                    Reservation.date == data.date,
                    Reservation.time_start == data.time_start,
                    Reservation.status.in_(["pending", "confirmed"]),
                    Reservation.table_type_id.isnot(None),
                )
            )
            .group_by(Reservation.table_type_id)
        )
        slot_table_counts = {row[0]: row[1] for row in result.all()}

        best_table = await find_best_table_for_party(table_types, slot_table_counts, data.party_size)
        if best_table is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No hay mesas disponibles para ese número de personas en ese horario.",
            )
        table_type_id = best_table.id

    reservation = Reservation(
        business_id=business_id,
        client_name=data.client_name,
        client_phone=data.client_phone,
        date=data.date,
        time_start=data.time_start,
        time_end=time_end,
        party_size=data.party_size,
        source=data.source,
        notes=data.notes,
        status="pending",
        table_type_id=table_type_id,
    )
    db.add(reservation)
    await db.commit()
    await db.refresh(reservation)
    await invalidate_slots_cache(redis, business_id, data.date)
    return reservation


async def get_reservation(
    db: AsyncSession, business_id: int, reservation_id: int
) -> Reservation:
    return await _get_or_404(db, business_id, reservation_id)


async def update_reservation(
    db: AsyncSession,
    redis: aioredis.Redis,
    business_id: int,
    reservation_id: int,
    data: ReservationUpdate,
) -> Reservation:
    reservation = await _get_or_404(db, business_id, reservation_id)
    old_date = reservation.date

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(reservation, field, value)

    if data.time_start or data.date:
        config = await get_business_config(db, business_id)
        reservation.time_end = _compute_time_end(reservation.time_start, config.slot_duration)

    await db.commit()
    await db.refresh(reservation)

    await invalidate_slots_cache(redis, business_id, old_date)
    if reservation.date != old_date:
        await invalidate_slots_cache(redis, business_id, reservation.date)

    return reservation


async def delete_reservation(
    db: AsyncSession, redis: aioredis.Redis, business_id: int, reservation_id: int
) -> None:
    reservation = await _get_or_404(db, business_id, reservation_id)
    target_date = reservation.date
    await db.delete(reservation)
    await db.commit()
    await invalidate_slots_cache(redis, business_id, target_date)


async def update_status(
    db: AsyncSession,
    redis: aioredis.Redis,
    business_id: int,
    reservation_id: int,
    new_status: str,
) -> Reservation:
    if new_status not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Estado inválido. Valores permitidos: {', '.join(VALID_STATUSES)}",
        )
    reservation = await _get_or_404(db, business_id, reservation_id)
    reservation.status = new_status
    await db.commit()
    await db.refresh(reservation)

    if new_status in ("cancelled", "no_show"):
        await invalidate_slots_cache(redis, business_id, reservation.date)

    return reservation
