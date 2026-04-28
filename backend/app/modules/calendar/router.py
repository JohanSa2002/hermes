from datetime import date

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_business
from app.core.redis import get_redis
from app.modules.calendar import schemas, service

router = APIRouter()


@router.get("/availability", response_model=schemas.DayAvailability)
async def get_availability(
    date: date,
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    return await service.get_available_slots(db, redis, business_id, date)


@router.get("/availability/range", response_model=list[schemas.DayAvailability])
async def get_availability_range(
    start: date,
    end: date,
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    return await service.get_availability_range(db, redis, business_id, start, end)


@router.post("/blocked-dates", status_code=201)
async def add_blocked_date(
    body: schemas.BlockedDateRequest,
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    await service.add_blocked_date(db, business_id, body.date)
    await service.invalidate_slots_cache(redis, business_id, body.date)
    return {"detail": "Fecha bloqueada"}


@router.delete("/blocked-dates/{target_date}", status_code=204)
async def remove_blocked_date(
    target_date: date,
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    await service.remove_blocked_date(db, business_id, target_date)
    await service.invalidate_slots_cache(redis, business_id, target_date)
    return Response(status_code=204)
