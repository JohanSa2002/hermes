from pydantic import BaseModel


class CollectedData(BaseModel):
    client_name: str | None = None
    date: str | None = None        # YYYY-MM-DD
    time_start: str | None = None  # HH:MM
    party_size: int | None = None


class ConversationContext(BaseModel):
    phone: str
    business_id: int
    collected_data: CollectedData = CollectedData()
    messages: list[dict] = []      # historial {role, content} para Claude


class BotResponse(BaseModel):
    message: str
    action: str   # "collect_more" | "create_reservation" | "cancel"
    collected_data: CollectedData
