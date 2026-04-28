from datetime import date as Date, time as Time
from typing import Optional

from pydantic import BaseModel


class ReservationCreate(BaseModel):
    client_name: str
    client_phone: str
    date: Date
    time_start: Time
    party_size: int = 1
    notes: Optional[str] = None
    source: str = "manual"


class ReservationUpdate(BaseModel):
    client_name: Optional[str] = None
    client_phone: Optional[str] = None
    date: Optional[Date] = None
    time_start: Optional[Time] = None
    party_size: Optional[int] = None
    notes: Optional[str] = None


class StatusUpdate(BaseModel):
    status: str


class ReservationRead(BaseModel):
    id: int
    business_id: int
    client_name: str
    client_phone: str
    date: Date
    time_start: Time
    time_end: Time
    party_size: int
    status: str
    source: str
    notes: Optional[str]
    created_at: Date

    model_config = {"from_attributes": True}
