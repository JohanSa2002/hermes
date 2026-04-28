from datetime import date as Date, time as Time

from pydantic import BaseModel


class ReservationStats(BaseModel):
    today: int
    this_week: int
    this_month: int


class AgendaItem(BaseModel):
    id: int
    client_name: str
    client_phone: str
    time_start: Time
    time_end: Time
    party_size: int
    status: str

    model_config = {"from_attributes": True}


class PeakHour(BaseModel):
    hour: int
    total: int
