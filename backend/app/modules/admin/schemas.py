from pydantic import BaseModel


class BusinessSummary(BaseModel):
    id: int
    name: str
    type: str
    status: str
    plan: str

    model_config = {"from_attributes": True}


class StatusPatch(BaseModel):
    status: str


class PlatformStats(BaseModel):
    total_businesses: int
    active_businesses: int
    total_reservations: int
