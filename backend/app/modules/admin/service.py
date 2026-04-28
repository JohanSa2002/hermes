from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.admin.schemas import BusinessSummary, PlatformStats
from app.modules.business.models import Business
from app.modules.reservations.models import Reservation

VALID_STATUSES = {"trial", "active", "suspended"}


async def list_businesses(db: AsyncSession) -> list[Business]:
    result = await db.execute(select(Business).order_by(Business.created_at.desc()))
    return result.scalars().all()


async def get_business(db: AsyncSession, business_id: int) -> Business:
    result = await db.execute(select(Business).where(Business.id == business_id))
    business = result.scalar_one_or_none()
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negocio no encontrado")
    return business


async def update_business_status(db: AsyncSession, business_id: int, new_status: str) -> Business:
    if new_status not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Estado inválido. Opciones: {', '.join(VALID_STATUSES)}",
        )
    business = await get_business(db, business_id)
    business.status = new_status
    await db.commit()
    await db.refresh(business)
    return business


async def get_platform_stats(db: AsyncSession) -> PlatformStats:
    total = (await db.execute(select(func.count(Business.id)))).scalar_one()
    active = (
        await db.execute(
            select(func.count(Business.id)).where(Business.status == "active")
        )
    ).scalar_one()
    reservations = (await db.execute(select(func.count(Reservation.id)))).scalar_one()

    return PlatformStats(
        total_businesses=total,
        active_businesses=active,
        total_reservations=reservations,
    )
