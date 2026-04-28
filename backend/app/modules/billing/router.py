from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_business
from app.modules.billing import schemas, service

router = APIRouter()


@router.get("/plan", response_model=schemas.PlanRead)
async def get_plan(
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_plan(db, business_id)


@router.post("/upgrade", response_model=schemas.PlanRead)
async def upgrade_plan(
    body: schemas.UpgradeRequest,
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    return await service.upgrade_plan(db, business_id, body.plan)


@router.get("/usage", response_model=schemas.UsageRead)
async def get_usage(
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_usage(db, business_id)
