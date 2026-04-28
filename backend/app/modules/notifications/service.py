import logging

from app.modules.whatsapp.client import send_text_message

logger = logging.getLogger(__name__)


async def send_reservation_confirmation(
    phone_number_id: str,
    access_token: str,
    client_phone: str,
    client_name: str,
    reservation_date: str,
    time_start: str,
    business_name: str,
) -> None:
    message = (
        f"✅ Reserva confirmada, {client_name}!\n\n"
        f"📅 Fecha: {reservation_date}\n"
        f"🕐 Hora: {time_start}\n"
        f"📍 {business_name}\n\n"
        "Te esperamos. Si necesitas cancelar, contáctanos."
    )
    try:
        await send_text_message(phone_number_id, access_token, client_phone, message)
    except Exception as exc:
        logger.warning("No se pudo enviar confirmación a %s: %s", client_phone, exc)


async def send_reservation_reminder(
    phone_number_id: str,
    access_token: str,
    client_phone: str,
    client_name: str,
    reservation_date: str,
    time_start: str,
    business_name: str,
) -> None:
    message = (
        f"👋 Hola {client_name}, te recordamos tu reserva en {business_name}.\n\n"
        f"📅 {reservation_date} a las {time_start}\n\n"
        "¡Te esperamos!"
    )
    try:
        await send_text_message(phone_number_id, access_token, client_phone, message)
    except Exception as exc:
        logger.warning("No se pudo enviar recordatorio a %s: %s", client_phone, exc)
