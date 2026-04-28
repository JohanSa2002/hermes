from datetime import date, time

import pytest

from app.modules.reservations.schemas import ReservationCreate, ReservationUpdate, StatusUpdate
from app.modules.reservations.service import (
    create_reservation,
    delete_reservation,
    get_reservation,
    list_reservations,
    update_status,
)
from tests.conftest import make_business, make_user


async def _create_test_reservation(db, redis_mock, business_id):
    return await create_reservation(
        db=db,
        redis=redis_mock,
        business_id=business_id,
        data=ReservationCreate(
            client_name="Ana García",
            client_phone="5491112345678",
            date=date(2026, 5, 5),
            time_start=time(10, 0),
            party_size=2,
            source="manual",
        ),
    )


async def test_create_reservation(db, redis_mock):
    business = await make_business(db, name="Res Test")
    r = await _create_test_reservation(db, redis_mock, business.id)

    assert r.id is not None
    assert r.client_name == "Ana García"
    assert r.time_end == time(11, 0)  # 10:00 + 60min slot
    assert r.status == "pending"
    assert r.source == "manual"
    redis_mock.delete.assert_called_once()  # caché invalidada


async def test_list_reservations_filter_by_date(db, redis_mock):
    business = await make_business(db, name="List Test")
    await _create_test_reservation(db, redis_mock, business.id)

    results = await list_reservations(db, business.id, filter_date=date(2026, 5, 5))
    assert len(results) >= 1
    assert all(r.date == date(2026, 5, 5) for r in results)


async def test_list_reservations_filter_by_status(db, redis_mock):
    business = await make_business(db, name="Status Test")
    await _create_test_reservation(db, redis_mock, business.id)

    results = await list_reservations(db, business.id, filter_status="pending")
    assert all(r.status == "pending" for r in results)


async def test_get_reservation_not_found(db):
    business = await make_business(db, name="404 Test")
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await get_reservation(db, business.id, 999999)
    assert exc.value.status_code == 404


async def test_get_reservation_wrong_business(db, redis_mock):
    b1 = await make_business(db, name="Business 1")
    b2 = await make_business(db, name="Business 2")
    r = await _create_test_reservation(db, redis_mock, b1.id)

    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await get_reservation(db, b2.id, r.id)
    assert exc.value.status_code == 404


async def test_update_status_to_confirmed(db, redis_mock):
    business = await make_business(db, name="Confirm Test")
    r = await _create_test_reservation(db, redis_mock, business.id)

    updated = await update_status(db, redis_mock, business.id, r.id, "confirmed")
    assert updated.status == "confirmed"


async def test_update_status_cancelled_invalidates_cache(db, redis_mock):
    business = await make_business(db, name="Cancel Cache Test")
    r = await _create_test_reservation(db, redis_mock, business.id)
    redis_mock.delete.reset_mock()

    await update_status(db, redis_mock, business.id, r.id, "cancelled")
    redis_mock.delete.assert_called_once()  # caché invalidada al cancelar


async def test_update_status_invalid_raises(db, redis_mock):
    business = await make_business(db, name="Invalid Status Test")
    r = await _create_test_reservation(db, redis_mock, business.id)

    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await update_status(db, redis_mock, business.id, r.id, "inexistente")
    assert exc.value.status_code == 422


async def test_delete_reservation(db, redis_mock):
    business = await make_business(db, name="Delete Test")
    r = await _create_test_reservation(db, redis_mock, business.id)
    r_id = r.id
    redis_mock.delete.reset_mock()

    await delete_reservation(db, redis_mock, business.id, r_id)
    redis_mock.delete.assert_called_once()

    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        await get_reservation(db, business.id, r_id)
