from datetime import date, time

from pydantic import BaseModel


class BusinessRead(BaseModel):
    id: int
    name: str
    type: str
    timezone: str
    status: str
    plan: str
    meta_business_id: str | None
    whatsapp_phone_number_id: str | None

    model_config = {"from_attributes": True}


class BusinessUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    timezone: str | None = None


class BusinessConfigRead(BaseModel):
    open_days: list[int]
    open_time: time
    close_time: time
    slot_duration: int
    max_per_slot: int
    blocked_dates: list[date]
    assistant_name: str
    tone: str
    welcome_message: str | None

    model_config = {"from_attributes": True}


class BusinessConfigUpdate(BaseModel):
    open_days: list[int] | None = None
    open_time: time | None = None
    close_time: time | None = None
    slot_duration: int | None = None
    max_per_slot: int | None = None
    blocked_dates: list[date] | None = None
    assistant_name: str | None = None
    tone: str | None = None
    welcome_message: str | None = None
