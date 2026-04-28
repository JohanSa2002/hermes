from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.business.models import Business, BusinessConfig
from app.modules.business.schemas import BusinessConfigUpdate, BusinessUpdate


async def get_business(db: AsyncSession, business_id: int) -> Business:
    result = await db.execute(select(Business).where(Business.id == business_id))
    business = result.scalar_one_or_none()
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negocio no encontrado")
    return business


async def update_business(
    db: AsyncSession, business_id: int, data: BusinessUpdate
) -> Business:
    business = await get_business(db, business_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(business, field, value)
    await db.commit()
    await db.refresh(business)
    return business


async def get_business_config(db: AsyncSession, business_id: int) -> BusinessConfig:
    result = await db.execute(
        select(BusinessConfig).where(BusinessConfig.business_id == business_id)
    )
    config = result.scalar_one_or_none()
    if not config:
        config = BusinessConfig(business_id=business_id)
        db.add(config)
        await db.commit()
        await db.refresh(config)
    return config


async def update_business_config(
    db: AsyncSession, business_id: int, data: BusinessConfigUpdate
) -> BusinessConfig:
    config = await get_business_config(db, business_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(config, field, value)
    await db.commit()
    await db.refresh(config)
    return config
