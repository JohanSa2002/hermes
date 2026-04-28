import asyncio

from fastapi import APIRouter, BackgroundTasks, Depends, Header, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_business
from app.modules.whatsapp import schemas, service

router = APIRouter()


@router.post("/connect", response_model=dict)
async def connect(
    body: schemas.ConnectRequest,
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    await service.connect_whatsapp(db, business_id, body)
    return {"detail": "WhatsApp conectado correctamente"}


@router.get("/status", response_model=schemas.WhatsAppStatusRead)
async def get_status(
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    from app.modules.business.models import Business

    result = await db.execute(select(Business).where(Business.id == business_id))
    business = result.scalar_one_or_none()
    return schemas.WhatsAppStatusRead(
        connected=bool(business and business.whatsapp_phone_number_id),
        phone_number_id=business.whatsapp_phone_number_id if business else None,
        meta_business_id=business.meta_business_id if business else None,
    )


@router.post("/disconnect", status_code=204)
async def disconnect(
    business_id: int = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    await service.disconnect_whatsapp(db, business_id)
    return Response(status_code=204)


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
):
    """Verificación inicial del webhook por parte de Meta."""
    if hub_mode == "subscribe" and hub_verify_token == settings.META_WEBHOOK_VERIFY_TOKEN:
        return Response(content=hub_challenge, media_type="text/plain")
    return Response(status_code=403)


@router.post("/webhook", status_code=200)
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Recibe mensajes de Meta, valida firma y despacha al bot de forma asíncrona."""
    body_bytes = await request.body()
    service.verify_signature(body_bytes, x_hub_signature_256 or "")

    payload = schemas.WebhookPayload.model_validate_json(body_bytes)
    background_tasks.add_task(service.dispatch_webhook, db, payload)

    return {"status": "ok"}
