from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, String, Time, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    client_name = Column(String, nullable=False)
    client_phone = Column(String, nullable=False)
    date = Column(Date, nullable=False, index=True)
    time_start = Column(Time, nullable=False)
    time_end = Column(Time, nullable=False)
    party_size = Column(Integer, nullable=False, default=1)
    status = Column(
        Enum("pending", "confirmed", "cancelled", "no_show", name="reservation_status"),
        nullable=False,
        default="pending",
    )
    source = Column(
        Enum("whatsapp", "manual", name="reservation_source"),
        nullable=False,
        default="manual",
    )
    notes = Column(String, nullable=True)
    created_at = Column(Date, server_default=func.current_date())

    business = relationship("Business", back_populates="reservations")
