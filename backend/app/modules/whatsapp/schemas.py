from pydantic import BaseModel


class ConnectRequest(BaseModel):
    access_token: str
    phone_number_id: str
    meta_business_id: str


class WhatsAppStatusRead(BaseModel):
    connected: bool
    phone_number_id: str | None
    meta_business_id: str | None


# --- Estructuras del payload de Meta ---

class WhatsAppTextMessage(BaseModel):
    body: str


class WhatsAppMessage(BaseModel):
    from_: str
    id: str
    type: str
    text: WhatsAppTextMessage | None = None

    model_config = {"populate_by_name": True}


class WhatsAppValue(BaseModel):
    messaging_product: str
    metadata: dict
    messages: list[WhatsAppMessage] | None = None


class WhatsAppChange(BaseModel):
    value: WhatsAppValue
    field: str


class WhatsAppEntry(BaseModel):
    id: str
    changes: list[WhatsAppChange]


class WebhookPayload(BaseModel):
    object: str
    entry: list[WhatsAppEntry]
