import json
from datetime import date, datetime, time, timedelta

import redis.asyncio as aioredis
from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.business.models import BusinessConfig, TableType
from app.modules.business.service import get_business_config, list_table_types
from app.modules.calendar.schemas import DayAvailability, SlotRead
from app.modules.reservations.models import Reservation

SLOTS_CACHE_TTL = 300  # 5 minutos


def _cache_key(business_id: int, target_date: date) -> str:
    return f"slots:{business_id}:{target_date.isoformat()}"


def _cache_key_party(business_id: int, target_date: date, party_size: int) -> str:
    return f"slots:{business_id}:{target_date.isoformat()}:p{party_size}"


def _generate_slots(open_time: time, close_time: time, slot_duration: int) -> list[tuple[time, time]]:
    slots = []
    base = date.today()
    current = datetime.combine(base, open_time)
    end = datetime.combine(base, close_time)
    delta = timedelta(minutes=slot_duration)
    while current + delta <= end:
        slots.append((current.time(), (current + delta).time()))
        current += delta
    return slots


async def _count_reservations_per_slot(
    db: AsyncSession,
    business_id: int,
    target_date: date,
    slots: list[tuple[time, time]],
) -> dict[tuple[time, time], int]:
    result = await db.execute(
        select(Reservation.time_start, func.count(Reservation.id))
        .where(
            and_(
                Reservation.business_id == business_id,
                Reservation.date == target_date,
                Reservation.status.in_(["pending", "confirmed"]),
            )
        )
        .group_by(Reservation.time_start)
    )
    counts = {row[0]: row[1] for row in result.all()}
    return {slot: counts.get(slot[0], 0) for slot in slots}


async def _count_reservations_by_table_type(
    db: AsyncSession,
    business_id: int,
    target_date: date,
    slots: list[tuple[time, time]],
) -> dict[tuple[time, time], dict[int, int]]:
    """Devuelve {slot: {table_type_id: count}} para slots con table_type_id asignado."""
    result = await db.execute(
        select(Reservation.time_start, Reservation.table_type_id, func.count(Reservation.id))
        .where(
            and_(
                Reservation.business_id == business_id,
                Reservation.date == target_date,
                Reservation.status.in_(["pending", "confirmed"]),
                Reservation.table_type_id.isnot(None),
            )
        )
        .group_by(Reservation.time_start, Reservation.table_type_id)
    )
    slot_counts: dict[tuple[time, time], dict[int, int]] = {s: {} for s in slots}
    for time_start, table_type_id, count in result.all():
        for slot in slots:
            if slot[0] == time_start:
                slot_counts[slot][table_type_id] = count
    return slot_counts


async def get_available_slots(
    db: AsyncSession,
    redis: aioredis.Redis,
    business_id: int,
    target_date: date,
) -> DayAvailability:
    """Disponibilidad genérica (sin filtro de party_size). Usada por el panel de control."""
    cache_key = _cache_key(business_id, target_date)
    cached = await redis.get(cache_key)
    if cached:
        return DayAvailability.model_validate_json(cached)

    config = await get_business_config(db, business_id)
    is_open = (
        target_date.weekday() in (config.open_days or [])
        and target_date not in (config.blocked_dates or [])
    )

    if not is_open:
        result = DayAvailability(date=target_date, is_open=False, slots=[])
        await redis.setex(cache_key, SLOTS_CACHE_TTL, result.model_dump_json())
        return result

    raw_slots = _generate_slots(config.open_time, config.close_time, config.slot_duration)

    # Restaurantes con mesas configuradas: mostrar disponibilidad agregada
    table_types = await list_table_types(db, business_id)
    if table_types:
        slot_table_counts = await _count_reservations_by_table_type(db, business_id, target_date, raw_slots)
        total_tables = sum(t.quantity for t in table_types)
        slots = []
        for s in raw_slots:
            used = sum(slot_table_counts[s].values())
            slots.append(SlotRead(
                time_start=s[0],
                time_end=s[1],
                available=max(0, total_tables - used),
                max_per_slot=total_tables,
            ))
    else:
        counts = await _count_reservations_per_slot(db, business_id, target_date, raw_slots)
        slots = [
            SlotRead(
                time_start=s[0],
                time_end=s[1],
                available=max(0, config.max_per_slot - counts[s]),
                max_per_slot=config.max_per_slot,
            )
            for s in raw_slots
        ]

    result = DayAvailability(date=target_date, is_open=True, slots=slots)
    await redis.setex(cache_key, SLOTS_CACHE_TTL, result.model_dump_json())
    return result


async def get_available_slots_for_party(
    db: AsyncSession,
    redis: aioredis.Redis,
    business_id: int,
    target_date: date,
    party_size: int,
) -> DayAvailability:
    """Disponibilidad filtrada por tamaño de grupo. Usada por el bot para restaurantes."""
    cache_key = _cache_key_party(business_id, target_date, party_size)
    cached = await redis.get(cache_key)
    if cached:
        return DayAvailability.model_validate_json(cached)

    config = await get_business_config(db, business_id)
    is_open = (
        target_date.weekday() in (config.open_days or [])
        and target_date not in (config.blocked_dates or [])
    )

    if not is_open:
        result = DayAvailability(date=target_date, is_open=False, slots=[])
        await redis.setex(cache_key, SLOTS_CACHE_TTL, result.model_dump_json())
        return result

    raw_slots = _generate_slots(config.open_time, config.close_time, config.slot_duration)
    table_types = await list_table_types(db, business_id)

    if not table_types:
        # Negocio sin mesas configuradas → usa max_per_slot genérico
        counts = await _count_reservations_per_slot(db, business_id, target_date, raw_slots)
        slots = [
            SlotRead(
                time_start=s[0],
                time_end=s[1],
                available=max(0, config.max_per_slot - counts[s]),
                max_per_slot=config.max_per_slot,
            )
            for s in raw_slots
        ]
    else:
        # Mesas configuradas: buscar tipos con capacidad >= party_size
        fitting_types = [t for t in table_types if t.capacity >= party_size]
        slot_table_counts = await _count_reservations_by_table_type(db, business_id, target_date, raw_slots)
        slots = []
        for s in raw_slots:
            available_tables = 0
            total_fitting = 0
            for t in fitting_types:
                used = slot_table_counts[s].get(t.id, 0)
                free = max(0, t.quantity - used)
                available_tables += free
                total_fitting += t.quantity
            slots.append(SlotRead(
                time_start=s[0],
                time_end=s[1],
                available=available_tables,
                max_per_slot=total_fitting,
            ))

    result = DayAvailability(date=target_date, is_open=True, slots=slots)
    await redis.setex(cache_key, SLOTS_CACHE_TTL, result.model_dump_json())
    return result


async def find_best_table_for_party(
    table_types: list[TableType],
    slot_table_counts: dict[int, int],
    party_size: int,
) -> TableType | None:
    """Devuelve la mesa más pequeña que cabe el grupo y que tiene disponibilidad."""
    fitting = sorted(
        [t for t in table_types if t.capacity >= party_size],
        key=lambda t: t.capacity,
    )
    for t in fitting:
        used = slot_table_counts.get(t.id, 0)
        if used < t.quantity:
            return t
    return None


async def get_availability_range(
    db: AsyncSession,
    redis: aioredis.Redis,
    business_id: int,
    start: date,
    end: date,
) -> list[DayAvailability]:
    if (end - start).days > 31:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El rango máximo es 31 días",
        )
    days = []
    current = start
    while current <= end:
        days.append(await get_available_slots(db, redis, business_id, current))
        current += timedelta(days=1)
    return days


async def invalidate_slots_cache(redis: aioredis.Redis, business_id: int, target_date: date) -> None:
    # Invalida cache genérico y cualquier cache por party_size (patrón)
    await redis.delete(_cache_key(business_id, target_date))
    # Borra claves con party_size para esa fecha
    pattern = f"slots:{business_id}:{target_date.isoformat()}:p*"
    keys = await redis.keys(pattern)
    if keys:
        await redis.delete(*keys)


async def add_blocked_date(db: AsyncSession, business_id: int, target_date: date) -> None:
    config = await get_business_config(db, business_id)
    blocked = list(config.blocked_dates or [])
    if target_date not in blocked:
        blocked.append(target_date)
        config.blocked_dates = blocked
        await db.commit()


async def remove_blocked_date(db: AsyncSession, business_id: int, target_date: date) -> None:
    config = await get_business_config(db, business_id)
    blocked = list(config.blocked_dates or [])
    if target_date not in blocked:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fecha no bloqueada")
    blocked.remove(target_date)
    config.blocked_dates = blocked
    await db.commit()
