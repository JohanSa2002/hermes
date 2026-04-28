import json
from datetime import date, datetime, time, timedelta

import redis.asyncio as aioredis
from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.business.models import BusinessConfig
from app.modules.business.service import get_business_config
from app.modules.calendar.schemas import DayAvailability, SlotRead
from app.modules.reservations.models import Reservation

SLOTS_CACHE_TTL = 300  # 5 minutos


def _cache_key(business_id: int, target_date: date) -> str:
    return f"slots:{business_id}:{target_date.isoformat()}"


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


async def get_available_slots(
    db: AsyncSession,
    redis: aioredis.Redis,
    business_id: int,
    target_date: date,
) -> DayAvailability:
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
    await redis.delete(_cache_key(business_id, target_date))


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
