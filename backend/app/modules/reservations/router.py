from datetime import date

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_business
from app.core.redis import get_redis
from app.modules.reservations import schemas, service

router = APIRouter()


@router.get("/", response_model=list[schemas.ReservationRead])
async def list_reservations(
    date: date | None = None,
    status: str | None = None,
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    return await service.list_reservations(db, business_id, date, status)


@router.post("/", response_model=schemas.ReservationRead, status_code=201)
async def create_reservation(
    body: schemas.ReservationCreate,
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    return await service.create_reservation(db, redis, business_id, body)


@router.get("/{reservation_id}", response_model=schemas.ReservationRead)
async def get_reservation(
    reservation_id: int,
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_reservation(db, business_id, reservation_id)


@router.put("/{reservation_id}", response_model=schemas.ReservationRead)
async def update_reservation(
    reservation_id: int,
    body: schemas.ReservationUpdate,
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    return await service.update_reservation(db, redis, business_id, reservation_id, body)


@router.delete("/{reservation_id}", status_code=204)
async def delete_reservation(
    reservation_id: int,
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    await service.delete_reservation(db, redis, business_id, reservation_id)
    return Response(status_code=204)


@router.patch("/{reservation_id}/status", response_model=schemas.ReservationRead)
async def update_status(
    reservation_id: int,
    body: schemas.StatusUpdate,
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    return await service.update_status(db, redis, business_id, reservation_id, body.status)
