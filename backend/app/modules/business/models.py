from datetime import date, time

from sqlalchemy import (
    Column,
    Date,
    Enum,
    ForeignKey,
    Integer,
    String,
    Time,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from app.core.database import Base


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    timezone = Column(String, nullable=False, default="UTC")
    status = Column(
        Enum("trial", "active", "suspended", name="business_status"),
        nullable=False,
        default="trial",
    )
    plan = Column(
        Enum("free", "basic", "pro", name="business_plan"),
        nullable=False,
        default="free",
    )
    meta_business_id = Column(String, nullable=True)
    whatsapp_phone_number_id = Column(String, nullable=True, unique=True)
    whatsapp_access_token = Column(String, nullable=True)
    created_at = Column(Date, server_default=func.current_date())

    users = relationship("User", back_populates="business", cascade="all, delete-orphan")
    config = relationship("BusinessConfig", back_populates="business", uselist=False)
    reservations = relationship("Reservation", back_populates="business")


class BusinessConfig(Base):
    __tablename__ = "business_configs"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(
        Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    open_days = Column(ARRAY(Integer), nullable=False, default=list)
    open_time = Column(Time, nullable=False, default=time(9, 0))
    close_time = Column(Time, nullable=False, default=time(18, 0))
    slot_duration = Column(Integer, nullable=False, default=60)
    max_per_slot = Column(Integer, nullable=False, default=1)
    blocked_dates = Column(ARRAY(Date), nullable=False, default=list)
    assistant_name = Column(String, nullable=False, default="Hermes")
    tone = Column(
        Enum("formal", "casual", name="assistant_tone"), nullable=False, default="formal"
    )
    welcome_message = Column(String, nullable=True)

    business = relationship("Business", back_populates="config")
