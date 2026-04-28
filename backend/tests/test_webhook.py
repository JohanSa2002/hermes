import hashlib
import hmac

import pytest
from fastapi import HTTPException

from app.modules.whatsapp.service import verify_signature


def _make_signature(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def test_valid_signature_passes(monkeypatch):
    monkeypatch.setattr("app.modules.whatsapp.service.settings.META_APP_SECRET", "mysecret")
    body = b'{"object":"whatsapp_business_account"}'
    sig = _make_signature("mysecret", body)
    verify_signature(body, sig)  # no debe lanzar


def test_invalid_signature_raises(monkeypatch):
    monkeypatch.setattr("app.modules.whatsapp.service.settings.META_APP_SECRET", "mysecret")
    body = b'{"object":"whatsapp_business_account"}'
    with pytest.raises(HTTPException) as exc:
        verify_signature(body, "sha256=invalidsignature")
    assert exc.value.status_code == 403


def test_missing_signature_raises(monkeypatch):
    monkeypatch.setattr("app.modules.whatsapp.service.settings.META_APP_SECRET", "mysecret")
    with pytest.raises(HTTPException) as exc:
        verify_signature(b"body", "")
    assert exc.value.status_code == 403


def test_missing_prefix_raises(monkeypatch):
    monkeypatch.setattr("app.modules.whatsapp.service.settings.META_APP_SECRET", "mysecret")
    with pytest.raises(HTTPException):
        verify_signature(b"body", "notsha256=abc")


async def test_webhook_verification_endpoint(client_no_db):
    import app.core.config as cfg
    cfg.settings.META_WEBHOOK_VERIFY_TOKEN = "test-verify-token"

    response = await client_no_db.get(
        "/whatsapp/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "test-verify-token",
            "hub.challenge": "challenge123",
        },
    )
    assert response.status_code == 200
    assert response.text == "challenge123"


async def test_webhook_verification_wrong_token(client_no_db):
    import app.core.config as cfg
    cfg.settings.META_WEBHOOK_VERIFY_TOKEN = "test-verify-token"

    response = await client_no_db.get(
        "/whatsapp/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong-token",
            "hub.challenge": "abc",
        },
    )
    assert response.status_code == 403
