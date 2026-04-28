from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.billing.schemas import PLAN_LIMITS, PlanRead, UsageRead
from app.modules.business.models import Business
from app.modules.business.service import get_business
from app.modules.reservations.models import Reservation

VALID_PLANS = set(PLAN_LIMITS.keys())


async def get_plan(db: AsyncSession, business_id: int) -> PlanRead:
    business = await get_business(db, business_id)
    limit = PLAN_LIMITS[business.plan]
    return PlanRead(
        plan=business.plan,
        status=business.status,
        monthly_limit=limit,
        is_unlimited=limit == -1,
    )


async def upgrade_plan(db: AsyncSession, business_id: int, new_plan: str) -> PlanRead:
    if new_plan not in VALID_PLANS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Plan inválido. Opciones: {', '.join(VALID_PLANS)}",
        )
    business = await get_business(db, business_id)
    business.plan = new_plan
    await db.commit()
    await db.refresh(business)
    return await get_plan(db, business_id)


async def get_usage(db: AsyncSession, business_id: int) -> UsageRead:
    business = await get_business(db, business_id)
    month_start = date.today().replace(day=1)

    result = await db.execute(
        select(func.count(Reservation.id)).where(
            and_(
                Reservation.business_id == business_id,
                Reservation.date >= month_start,
            )
        )
    )
    count = result.scalar_one()
    limit = PLAN_LIMITS[business.plan]

    return UsageRead(
        plan=business.plan,
        reservations_this_month=count,
        monthly_limit=limit,
        is_unlimited=limit == -1,
    )
