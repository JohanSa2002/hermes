from pydantic import BaseModel

PLAN_LIMITS = {
    "free": 50,
    "basic": 500,
    "pro": -1,  # ilimitado
}


class PlanRead(BaseModel):
    plan: str
    status: str
    monthly_limit: int
    is_unlimited: bool


class UpgradeRequest(BaseModel):
    plan: str


class UsageRead(BaseModel):
    plan: str
    reservations_this_month: int
    monthly_limit: int
    is_unlimited: bool
