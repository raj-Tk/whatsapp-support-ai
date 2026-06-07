from datetime import datetime, timedelta, timezone

from jose import jwt

from app.config import settings
from app.services.auth_service import create_access_token


class DummyUser:
    id = "USR-TEST"
    role = "customer"


def test_create_access_token_contains_user_claims():
    token = create_access_token(DummyUser())
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

    assert payload["sub"] == "USR-TEST"
    assert payload["role"] == "customer"


def test_create_access_token_has_future_expiry():
    token = create_access_token(DummyUser())
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

    assert expires_at > datetime.now(timezone.utc) + timedelta(minutes=1)
