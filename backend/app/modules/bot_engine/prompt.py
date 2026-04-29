from app.modules.bot_engine.schemas import ConversationContext
from app.modules.business.models import Business, BusinessConfig, Service, TableType
from app.modules.calendar.schemas import DayAvailability

DAYS_ES = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

# Contexto general por tipo de negocio
BUSINESS_TYPE_CONTEXT: dict[str, dict] = {
    "restaurant": {
        "description": (
            "Eres el asistente de reservas de un restaurante. Tu misión es ayudar a los "
            "clientes a reservar una mesa. Siempre pregunta cuántas personas son antes de "
            "mostrar disponibilidad, ya que los horarios dependen del tamaño del grupo. "
            "Puedes informar sobre el menú o servicios disponibles si el cliente pregunta."
        ),
        "party_term": "comensales",
        "reservation_term": "reserva de mesa",
        "ask_party_first": True,
    },
    "clinic": {
        "description": (
            "Eres el asistente de citas de una clínica o consultorio. Tu misión es ayudar "
            "a los pacientes a agendar su cita médica. Trata a los pacientes con respeto y "
            "empatía. Puedes informar sobre los servicios o especialidades disponibles si "
            "el paciente pregunta. Pregunta el motivo de la consulta solo si es necesario "
            "para determinar el servicio correcto."
        ),
        "party_term": "pacientes",
        "reservation_term": "cita médica",
        "ask_party_first": False,
    },
    "salon": {
        "description": (
            "Eres el asistente de reservas de un salón de belleza. Tu misión es ayudar a "
            "los clientes a reservar su cita. Puedes informar sobre los servicios y precios "
            "disponibles si el cliente pregunta. Pregunta qué servicio desean para asignar "
            "el tiempo correcto."
        ),
        "party_term": "personas",
        "reservation_term": "cita",
        "ask_party_first": False,
    },
    "spa": {
        "description": (
            "Eres el asistente de reservas de un spa o centro de bienestar. Tu misión es "
            "ayudar a los clientes a reservar sus tratamientos. Usa un tono relajante y "
            "acogedor. Puedes informar sobre los tratamientos y precios disponibles si el "
            "cliente pregunta."
        ),
        "party_term": "personas",
        "reservation_term": "reserva de tratamiento",
        "ask_party_first": False,
    },
    "barbershop": {
        "description": (
            "Eres el asistente de reservas de una barbería. Tu misión es ayudar a los "
            "clientes a reservar su turno. Puedes informar sobre los servicios y precios "
            "disponibles si el cliente pregunta."
        ),
        "party_term": "personas",
        "reservation_term": "turno",
        "ask_party_first": False,
    },
    "gym": {
        "description": (
            "Eres el asistente de reservas de un gimnasio o entrenador personal. Tu misión "
            "es ayudar a los clientes a reservar sus sesiones de entrenamiento. Puedes "
            "informar sobre los servicios y planes disponibles si el cliente pregunta."
        ),
        "party_term": "personas",
        "reservation_term": "sesión",
        "ask_party_first": False,
    },
    "other": {
        "description": (
            "Eres el asistente de reservas de un negocio de servicios. Tu misión es ayudar "
            "a los clientes a agendar su reserva. Puedes informar sobre los servicios "
            "disponibles si el cliente pregunta."
        ),
        "party_term": "personas",
        "reservation_term": "reserva",
        "ask_party_first": False,
    },
}


def _format_open_days(open_days: list[int]) -> str:
    return ", ".join(DAYS_ES[d] for d in sorted(open_days))


def _format_slots(availability: DayAvailability | None) -> str:
    if not availability or not availability.is_open:
        return "No hay disponibilidad para esa fecha."
    available = [s for s in availability.slots if s.available > 0]
    if not available:
        return "No quedan lugares disponibles para esa fecha."
    return ", ".join(s.time_start.strftime("%H:%M") for s in available)


def _format_table_types(table_types: list[TableType]) -> str:
    lines = []
    for t in sorted(table_types, key=lambda x: x.capacity):
        label = f" ({t.label})" if t.label else ""
        lines.append(f"  - {t.quantity} mesa(s) para {t.capacity} persona(s){label}")
    return "\n".join(lines)


def _format_services(services: list[Service]) -> str:
    if not services:
        return ""
    lines = []
    for s in services:
        if not s.is_active:
            continue
        parts = [f"• {s.name}"]
        if s.description:
            parts.append(f": {s.description}")
        extras = []
        if s.price is not None:
            extras.append(f"${float(s.price):,.0f}")
        if s.duration_minutes:
            extras.append(f"{s.duration_minutes} min")
        if extras:
            parts.append(f" ({', '.join(extras)})")
        lines.append("".join(parts))
    return "\n".join(lines) if lines else ""


def build_system_prompt(
    business: Business,
    config: BusinessConfig,
    availability: DayAvailability | None,
    context: ConversationContext,
    table_types: list[TableType] | None = None,
    services: list[Service] | None = None,
) -> str:
    btype = business.type or "other"
    type_ctx = BUSINESS_TYPE_CONTEXT.get(btype, BUSINESS_TYPE_CONTEXT["other"])

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

    # Bloque de mesas (solo restaurantes con mesas configuradas)
    tables_block = ""
    if table_types:
        tables_block = f"""
CONFIGURACIÓN DE MESAS:
{_format_table_types(table_types)}
Los horarios disponibles ya están filtrados según el tamaño del grupo indicado.
Si no hay mesas disponibles para ese grupo, informa amablemente y sugiere otros horarios o fechas.
"""

    # Bloque de servicios
    services_block = ""
    if services:
        formatted = _format_services(services)
        if formatted:
            services_block = f"""
SERVICIOS DISPONIBLES:
{formatted}
Puedes informar sobre estos servicios si el cliente pregunta. No es obligatorio elegir uno para reservar a menos que sea necesario para determinar la duración.
"""

    # Indicación de preguntar comensales primero (restaurantes)
    party_first_hint = ""
    if type_ctx["ask_party_first"] and not collected.party_size:
        party_first_hint = f"\nIMPORTANTE: Pregunta primero cuántos {type_ctx['party_term']} serán antes de mostrar disponibilidad.\n"

    return f"""Eres {config.assistant_name}, asistente virtual de {business.name}.
{type_ctx['description']}
{tone_instruction}
Responde SIEMPRE en el idioma del cliente.
{party_first_hint}{tables_block}{services_block}
HORARIO DEL NEGOCIO:
- Días de atención: {_format_open_days(config.open_days or [])}
- Horario: {config.open_time.strftime("%H:%M")} a {config.close_time.strftime("%H:%M")}
- Duración de cada turno: {config.slot_duration} minutos

SLOTS DISPONIBLES: {_format_slots(availability)}

DATOS YA RECOPILADOS DEL CLIENTE:
{collected_summary}

OBJETIVO: Recopilar nombre, fecha, hora y número de {type_ctx['party_term']} para crear la {type_ctx['reservation_term']}.
Si ya tienes todos los datos confirmados por el cliente, acción = "create_reservation".
Si el cliente quiere cancelar o no desea continuar, acción = "cancel".
En cualquier otro caso, acción = "collect_more".

Responde ÚNICAMENTE con JSON válido (sin markdown, sin explicaciones):
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
