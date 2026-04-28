from app.modules.bot_engine.schemas import CollectedData, ConversationContext
from app.modules.business.models import Business, BusinessConfig
from app.modules.calendar.schemas import DayAvailability

DAYS_ES = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def _format_open_days(open_days: list[int]) -> str:
    return ", ".join(DAYS_ES[d] for d in sorted(open_days))


def _format_slots(availability: DayAvailability | None) -> str:
    if not availability or not availability.is_open:
        return "No hay disponibilidad para esa fecha."
    available = [s for s in availability.slots if s.available > 0]
    if not available:
        return "No quedan slots disponibles para esa fecha."
    return ", ".join(s.time_start.strftime("%H:%M") for s in available)


def build_system_prompt(
    business: Business,
    config: BusinessConfig,
    availability: DayAvailability | None,
    context: ConversationContext,
) -> str:
    tone_instruction = (
        "Usa un tono formal y profesional."
        if config.tone == "formal"
        else "Usa un tono amigable y cercano."
    )

    collected = context.collected_data
    collected_summary = "\n".join([
        f"- Nombre: {collected.client_name or 'pendiente'}",
        f"- Fecha: {collected.date or 'pendiente'}",
        f"- Hora: {collected.time_start or 'pendiente'}",
        f"- Personas: {collected.party_size or 'pendiente'}",
    ])

    slots_info = _format_slots(availability)

    return f"""Eres {config.assistant_name}, asistente virtual de {business.name}.
{tone_instruction}
Responde SIEMPRE en el idioma del cliente.

HORARIO DEL NEGOCIO:
- Días de atención: {_format_open_days(config.open_days or [])}
- Horario: {config.open_time.strftime("%H:%M")} a {config.close_time.strftime("%H:%M")}
- Duración de cada turno: {config.slot_duration} minutos
- Capacidad por turno: {config.max_per_slot} persona(s)

SLOTS DISPONIBLES PARA LA FECHA SOLICITADA: {slots_info}

DATOS YA RECOPILADOS DEL CLIENTE:
{collected_summary}

OBJETIVO: Recopilar nombre, fecha, hora y número de personas para crear la reserva.
Si ya tienes todos los datos, acción = "create_reservation".
Si el cliente quiere cancelar, acción = "cancel".
En cualquier otro caso, acción = "collect_more".

Responde ÚNICAMENTE con JSON válido siguiendo este esquema exacto (sin markdown, sin explicaciones):
{{
  "message": "<texto para enviar al cliente>",
  "action": "collect_more" | "create_reservation" | "cancel",
  "collected_data": {{
    "client_name": null | "<nombre>",
    "date": null | "<YYYY-MM-DD>",
    "time_start": null | "<HH:MM>",
    "party_size": null | <número>
  }}
}}"""
