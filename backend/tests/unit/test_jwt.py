from uuid import uuid4

import pytest
from jose import JWTError

from infrastructure.auth.jwt import create_access_token, create_refresh_token, decode_token


def test_access_token_roundtrip():
    user_id = uuid4()
    token = create_access_token(user_id, "admin")
    payload = decode_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["role"] == "admin"
    assert payload["type"] == "access"


def test_refresh_token_roundtrip():
    user_id = uuid4()
    token = create_refresh_token(user_id)
    payload = decode_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["type"] == "refresh"


def test_refresh_token_has_no_role():
    token = create_refresh_token(uuid4())
    payload = decode_token(token)
    assert "role" not in payload


def test_invalid_token_raises():
    with pytest.raises(JWTError):
        decode_token("not.a.valid.token")


def test_tampered_token_raises():
    token = create_access_token(uuid4(), "admin")
    tampered = token[:-5] + "XXXXX"
    with pytest.raises(JWTError):
        decode_token(tampered)
