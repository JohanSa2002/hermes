from datetime import date, time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.modules.bot_engine.prompt import build_system_prompt
from app.modules.calendar.service import _generate_slots
from app.modules.bot_engine.schemas import CollectedData, ConversationContext
from app.modules.calendar.schemas import DayAvailability, SlotRead


def _make_config(**kwargs):
    config = MagicMock()
    config.tone = kwargs.get("tone", "formal")
    config.assistant_name = kwargs.get("assistant_name", "Hermes")
    config.open_days = kwargs.get("open_days", [0, 1, 2, 3, 4])
    config.open_time = kwargs.get("open_time", time(9, 0))
    config.close_time = kwargs.get("close_time", time(18, 0))
    config.slot_duration = kwargs.get("slot_duration", 60)
    config.max_per_slot = kwargs.get("max_per_slot", 2)
    return config


def _make_business(**kwargs):
    b = MagicMock()
    b.name = kwargs.get("name", "Restaurante Demo")
    b.id = 1
    b.whatsapp_phone_number_id = "phone-id"
    b.whatsapp_access_token = "token"
    return b


def test_build_system_prompt_contains_business_name():
    business = _make_business(name="Clínica Sol")
    config = _make_config(assistant_name="Sol")
    context = ConversationContext(phone="5491100000000", business_id=1)
    prompt = build_system_prompt(business, config, None, context)
    assert "Clínica Sol" in prompt
    assert "Sol" in prompt


def test_build_system_prompt_formal_tone():
    business = _make_business()
    config = _make_config(tone="formal")
    context = ConversationContext(phone="549", business_id=1)
    prompt = build_system_prompt(business, config, None, context)
    assert "formal" in prompt.lower()


def test_build_system_prompt_casual_tone():
    business = _make_business()
    config = _make_config(tone="casual")
    context = ConversationContext(phone="549", business_id=1)
    prompt = build_system_prompt(business, config, None, context)
    assert "amigable" in prompt.lower()


def test_build_system_prompt_with_slots():
    business = _make_business()
    config = _make_config()
    context = ConversationContext(phone="549", business_id=1)
    availability = DayAvailability(
        date=date(2026, 5, 5),
        is_open=True,
        slots=[
            SlotRead(time_start=time(10, 0), time_end=time(11, 0), available=2, max_per_slot=2),
            SlotRead(time_start=time(11, 0), time_end=time(12, 0), available=1, max_per_slot=2),
        ],
    )
    prompt = build_system_prompt(business, config, availability, context)
    assert "10:00" in prompt
    assert "11:00" in prompt


def test_build_system_prompt_no_availability():
    business = _make_business()
    config = _make_config()
    context = ConversationContext(phone="549", business_id=1)
    availability = DayAvailability(date=date(2026, 5, 5), is_open=False, slots=[])
    prompt = build_system_prompt(business, config, availability, context)
    assert "No hay disponibilidad" in prompt


def test_build_system_prompt_collected_data_shown():
    business = _make_business()
    config = _make_config()
    context = ConversationContext(
        phone="549",
        business_id=1,
        collected_data=CollectedData(
            client_name="Juan",
            date="2026-05-05",
            time_start="10:00",
            party_size=3,
        ),
    )
    prompt = build_system_prompt(business, config, None, context)
    assert "Juan" in prompt
    assert "2026-05-05" in prompt
    assert "10:00" in prompt
    assert "3" in prompt


def test_build_system_prompt_requires_json_response():
    business = _make_business()
    config = _make_config()
    context = ConversationContext(phone="549", business_id=1)
    prompt = build_system_prompt(business, config, None, context)
    assert "create_reservation" in prompt
    assert "collect_more" in prompt
    assert "cancel" in prompt


@pytest.mark.skip(reason="requiere asyncpg — test de integración")
async def test_process_message_calls_claude_and_sends_reply(db, redis_mock):
    from app.modules.bot_engine import service as bot_service
    from app.modules.bot_engine.schemas import BotResponse, CollectedData

    business = _make_business()
    bot_response = BotResponse(
        message="Hola, ¿cuál es tu nombre?",
        action="collect_more",
        collected_data=CollectedData(),
    )

    with (
        patch.object(bot_service, "_load_context", return_value=ConversationContext(phone="549", business_id=1)),
        patch("app.modules.bot_engine.service.get_business_config", return_value=_make_config()),
        patch.object(bot_service, "_call_claude", return_value=bot_response),
        patch.object(bot_service, "_save_context"),
        patch("app.modules.bot_engine.service.send_text_message", new_callable=AsyncMock) as mock_send,
        patch("app.modules.bot_engine.service.aioredis.from_url", return_value=redis_mock),
    ):
        await bot_service.process_message(db=db, phone="549", text="Hola", business=business)
        mock_send.assert_called_once_with(
            phone_number_id="phone-id",
            access_token="token",
            to="549",
            text="Hola, ¿cuál es tu nombre?",
        )
