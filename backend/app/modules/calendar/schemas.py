from datetime import date as Date, time as Time
from typing import Optional

from pydantic import BaseModel


class SlotRead(BaseModel):
    time_start: Time
    time_end: Time
    available: int
    max_per_slot: int


class DayAvailability(BaseModel):
    date: Date
    is_open: bool
    slots: list[SlotRead]


class BlockedDateRequest(BaseModel):
    date: Date
