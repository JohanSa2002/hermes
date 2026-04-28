from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_business, get_current_user
from app.modules.business import schemas, service

router = APIRouter()


@router.get("/me", response_model=schemas.BusinessRead)
async def get_my_business(
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_business(db, business_id)


@router.put("/me", response_model=schemas.BusinessRead)
async def update_my_business(
    body: schemas.BusinessUpdate,
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    return await service.update_business(db, business_id, body)


@router.get("/me/config", response_model=schemas.BusinessConfigRead)
async def get_my_config(
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_business_config(db, business_id)


@router.put("/me/config", response_model=schemas.BusinessConfigRead)
async def update_my_config(
    body: schemas.BusinessConfigUpdate,
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    return await service.update_business_config(db, business_id, body)
