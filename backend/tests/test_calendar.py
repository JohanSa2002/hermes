from datetime import date, time

import pytest

from app.modules.calendar.service import _generate_slots, get_available_slots
from tests.conftest import make_business


def test_generate_slots_basic():
    slots = _generate_slots(time(9, 0), time(12, 0), 60)
    assert len(slots) == 3
    assert slots[0] == (time(9, 0), time(10, 0))
    assert slots[1] == (time(10, 0), time(11, 0))
    assert slots[2] == (time(11, 0), time(12, 0))


def test_generate_slots_30min():
    slots = _generate_slots(time(9, 0), time(10, 0), 30)
    assert len(slots) == 2
    assert slots[0] == (time(9, 0), time(9, 30))
    assert slots[1] == (time(9, 30), time(10, 0))


def test_generate_slots_exact_fit():
    slots = _generate_slots(time(9, 0), time(9, 30), 30)
    assert len(slots) == 1


def test_generate_slots_no_fit():
    # slot_duration mayor que el rango → lista vacía
    slots = _generate_slots(time(9, 0), time(9, 20), 30)
    assert len(slots) == 0


async def test_availability_closed_day(db, redis_mock):
    business = await make_business(db, name="Test Cerrado")
    # open_days = [0,1,2,3,4] → domingo (6) está cerrado
    sunday = date(2026, 4, 26)  # domingo
    result = await get_available_slots(db, redis_mock, business.id, sunday)
    assert result.is_open is False
    assert result.slots == []


async def test_availability_open_day_no_reservations(db, redis_mock):
    business = await make_business(db, name="Test Abierto")
    monday = date(2026, 4, 27)  # lunes
    result = await get_available_slots(db, redis_mock, business.id, monday)
    assert result.is_open is True
    assert len(result.slots) == 9  # 09:00–18:00 en slots de 60 min
    assert all(s.available == 2 for s in result.slots)  # max_per_slot=2, sin reservas


async def test_availability_blocked_date(db, redis_mock):
    from datetime import date as d
    business = await make_business(db, name="Test Bloqueado")

    # Bloquear el lunes
    monday = date(2026, 4, 27)
    from app.modules.business.service import get_business_config
    config = await get_business_config(db, business.id)
    config.blocked_dates = [monday]
    await db.commit()

    result = await get_available_slots(db, redis_mock, business.id, monday)
    assert result.is_open is False


async def test_availability_cached(db, redis_mock):
    import json
    from app.modules.calendar.schemas import DayAvailability

    business = await make_business(db, name="Test Cache")
    monday = date(2026, 4, 27)

    cached_data = DayAvailability(date=monday, is_open=False, slots=[])
    redis_mock.get = pytest.AsyncMock(return_value=cached_data.model_dump_json())

    result = await get_available_slots(db, redis_mock, business.id, monday)
    assert result.is_open is False
    # Redis.get fue llamado → no consulta DB
    redis_mock.get.assert_called_once()
