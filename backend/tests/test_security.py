import pytest
from jose import JWTError

from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_and_verify_password():
    plain = "supersecret123"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed)


def test_wrong_password_fails():
    hashed = hash_password("correct")
    assert not verify_password("wrong", hashed)


def test_create_and_decode_token():
    data = {"sub": "42", "business_id": 7}
    token = create_access_token(data)
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["business_id"] == 7


def test_tampered_token_raises():
    token = create_access_token({"sub": "1"})
    tampered = token[:-5] + "XXXXX"
    with pytest.raises(JWTError):
        decode_token(tampered)


def test_token_contains_expiry():
    token = create_access_token({"sub": "1"})
    payload = decode_token(token)
    assert "exp" in payload
