from datetime import date, timedelta

from sqlalchemy import and_, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dashboard.schemas import AgendaItem, PeakHour, ReservationStats
from app.modules.reservations.models import Reservation


async def get_stats(db: AsyncSession, business_id: int) -> ReservationStats:
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    async def count(start: date, end: date) -> int:
        result = await db.execute(
            select(func.count(Reservation.id)).where(
                and_(
                    Reservation.business_id == business_id,
                    Reservation.date >= start,
                    Reservation.date <= end,
                    Reservation.status.in_(["pending", "confirmed"]),
                )
            )
        )
        return result.scalar_one()

    return ReservationStats(
        today=await count(today, today),
        this_week=await count(week_start, today),
        this_month=await count(month_start, today),
    )


async def get_agenda(db: AsyncSession, business_id: int, target_date: date) -> list[AgendaItem]:
    result = await db.execute(
        select(Reservation)
        .where(
            and_(
                Reservation.business_id == business_id,
                Reservation.date == target_date,
                Reservation.status.in_(["pending", "confirmed"]),
            )
        )
        .order_by(Reservation.time_start)
    )
    return result.scalars().all()


async def get_peak_hours(db: AsyncSession, business_id: int) -> list[PeakHour]:
    result = await db.execute(
        select(
            extract("hour", Reservation.time_start).label("hour"),
            func.count(Reservation.id).label("total"),
        )
        .where(
            and_(
                Reservation.business_id == business_id,
                Reservation.status.in_(["confirmed", "no_show"]),
            )
        )
        .group_by("hour")
        .order_by("hour")
    )
    return [PeakHour(hour=int(row.hour), total=row.total) for row in result.all()]
