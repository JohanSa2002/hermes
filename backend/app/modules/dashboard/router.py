from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_business
from app.modules.dashboard import schemas, service

router = APIRouter()


@router.get("/stats", response_model=schemas.ReservationStats)
async def get_stats(
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_stats(db, business_id)


@router.get("/agenda", response_model=list[schemas.AgendaItem])
async def get_agenda(
    date: date,
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_agenda(db, business_id, date)


@router.get("/peak-hours", response_model=list[schemas.PeakHour])
async def get_peak_hours(
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_peak_hours(db, business_id)
