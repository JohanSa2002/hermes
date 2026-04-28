import json
import logging
from datetime import date, time

import anthropic
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.bot_engine.prompt import build_system_prompt
from app.modules.bot_engine.schemas import BotResponse, CollectedData, ConversationContext
from app.modules.business.models import Business
from app.modules.business.service import get_business_config
from app.modules.calendar.service import get_available_slots
from app.modules.reservations.schemas import ReservationCreate
from app.modules.reservations.service import create_reservation
from app.modules.whatsapp.client import send_text_message

logger = logging.getLogger(__name__)

CONTEXT_TTL = 1800  # 30 minutos
MODEL = "claude-sonnet-4-20250514"

_anthropic = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)


def _context_key(business_id: int, phone: str) -> str:
    return f"conv:{business_id}:{phone}"


async def _load_context(redis: aioredis.Redis, business_id: int, phone: str) -> ConversationContext:
    raw = await redis.get(_context_key(business_id, phone))
    if raw:
        return ConversationContext.model_validate_json(raw)
    return ConversationContext(phone=phone, business_id=business_id)


async def _save_context(redis: aioredis.Redis, context: ConversationContext) -> None:
    await redis.setex(
        _context_key(context.business_id, context.phone),
        CONTEXT_TTL,
        context.model_dump_json(),
    )


async def _clear_context(redis: aioredis.Redis, business_id: int, phone: str) -> None:
    await redis.delete(_context_key(business_id, phone))


async def _call_claude(system_prompt: str, messages: list[dict]) -> BotResponse:
    response = await _anthropic.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )
    raw_text = response.content[0].text.strip()

    try:
        data = json.loads(raw_text)
        return BotResponse.model_validate(data)
    except Exception:
        logger.warning("Claude devolvió JSON inválido: %s", raw_text)
        return BotResponse(
            message=raw_text,
            action="collect_more",
            collected_data=CollectedData(),
        )


async def _handle_create_reservation(
    db: AsyncSession,
    redis: aioredis.Redis,
    business: Business,
    phone: str,
    bot_response: BotResponse,
) -> None:
    cd = bot_response.collected_data
    if not all([cd.client_name, cd.date, cd.time_start, cd.party_size]):
        return

    await create_reservation(
        db=db,
        redis=redis,
        business_id=business.id,
        data=ReservationCreate(
            client_name=cd.client_name,
            client_phone=phone,
            date=date.fromisoformat(cd.date),
            time_start=time.fromisoformat(cd.time_start),
            party_size=cd.party_size,
            source="whatsapp",
        ),
    )
    await _clear_context(redis, business.id, phone)


async def process_message(
    db: AsyncSession,
    phone: str,
    text: str,
    business: Business,
) -> None:
    redis: aioredis.Redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    try:
        context = await _load_context(redis, business.id, phone)
        config = await get_business_config(db, business.id)

        availability = None
        if context.collected_data.date:
            try:
                availability = await get_available_slots(
                    db, redis, business.id, date.fromisoformat(context.collected_data.date)
                )
            except Exception:
                pass

        system_prompt = build_system_prompt(business, config, availability, context)

        context.messages.append({"role": "user", "content": text})

        bot_response = await _call_claude(system_prompt, context.messages)

        context.messages.append({"role": "assistant", "content": bot_response.message})
        context.collected_data = bot_response.collected_data

        if bot_response.action == "create_reservation":
            await _handle_create_reservation(db, redis, business, phone, bot_response)
        elif bot_response.action == "cancel":
            await _clear_context(redis, business.id, phone)
        else:
            await _save_context(redis, context)

        await send_text_message(
            phone_number_id=business.whatsapp_phone_number_id,
            access_token=business.whatsapp_access_token,
            to=phone,
            text=bot_response.message,
        )

    except Exception as exc:
        logger.exception("Error procesando mensaje de %s: %s", phone, exc)
    finally:
        await redis.aclose()
