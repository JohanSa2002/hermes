import hashlib
import hmac

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.business.models import Business
from app.modules.whatsapp.schemas import ConnectRequest, WebhookPayload


def verify_signature(payload_bytes: bytes, signature_header: str) -> None:
    """Valida X-Hub-Signature-256 enviado por Meta."""
    if not signature_header or not signature_header.startswith("sha256="):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Firma ausente")

    expected = hmac.new(
        settings.META_APP_SECRET.encode(),
        payload_bytes,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected, signature_header[len("sha256="):]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Firma inválida")


async def get_business_by_phone_number_id(
    db: AsyncSession, phone_number_id: str
) -> Business | None:
    result = await db.execute(
        select(Business).where(Business.whatsapp_phone_number_id == phone_number_id)
    )
    return result.scalar_one_or_none()


async def connect_whatsapp(
    db: AsyncSession, business_id: int, data: ConnectRequest
) -> Business:
    result = await db.execute(select(Business).where(Business.id == business_id))
    business = result.scalar_one_or_none()
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negocio no encontrado")

    business.whatsapp_access_token = data.access_token
    business.whatsapp_phone_number_id = data.phone_number_id
    business.meta_business_id = data.meta_business_id
    await db.commit()
    await db.refresh(business)
    return business


async def disconnect_whatsapp(db: AsyncSession, business_id: int) -> None:
    result = await db.execute(select(Business).where(Business.id == business_id))
    business = result.scalar_one_or_none()
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negocio no encontrado")

    business.whatsapp_access_token = None
    business.whatsapp_phone_number_id = None
    business.meta_business_id = None
    await db.commit()


async def dispatch_webhook(db: AsyncSession, payload: WebhookPayload) -> None:
    """Procesa cada mensaje entrante y lo envía al bot engine."""
    from app.modules.bot_engine.service import process_message

    for entry in payload.entry:
        for change in entry.changes:
            if change.field != "messages" or not change.value.messages:
                continue

            phone_number_id = change.value.metadata.get("phone_number_id")
            business = await get_business_by_phone_number_id(db, phone_number_id)
            if not business:
                continue

            for message in change.value.messages:
                if message.type != "text" or not message.text:
                    continue
                await process_message(
                    db=db,
                    phone=message.from_,
                    text=message.text.body,
                    business=business,
                )
