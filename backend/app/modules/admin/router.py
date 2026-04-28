from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.modules.admin import schemas, service

router = APIRouter()


@router.get("/businesses", response_model=list[schemas.BusinessSummary])
async def list_businesses(
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await service.list_businesses(db)


@router.get("/businesses/{business_id}", response_model=schemas.BusinessSummary)
async def get_business(
    business_id: int,
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_business(db, business_id)


@router.patch("/businesses/{business_id}/status", response_model=schemas.BusinessSummary)
async def update_status(
    business_id: int,
    body: schemas.StatusPatch,
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await service.update_business_status(db, business_id, body.status)


@router.get("/stats", response_model=schemas.PlatformStats)
async def get_stats(
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_platform_stats(db)
