import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from pwdlib import PasswordHash

from app.core.config import Settings

password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash(secrets.token_urlsafe(24))


def now() -> datetime:
    return datetime.now(UTC)


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def issue_access(user_id: UUID, session_id: UUID, settings: Settings) -> str:
    instant = now()
    return jwt.encode(
        {
            "sub": str(user_id),
            "sid": str(session_id),
            "iat": instant,
            "exp": instant + timedelta(minutes=settings.access_token_minutes),
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
            "type": "access",
        },
        settings.jwt_secret.get_secret_value(),
        algorithm="HS256",
    )


def decode_access(token: str, settings: Settings) -> dict:
    return jwt.decode(
        token,
        settings.jwt_secret.get_secret_value(),
        algorithms=["HS256"],
        audience=settings.jwt_audience,
        issuer=settings.jwt_issuer,
        options={"require": ["sub", "sid", "exp", "iat", "iss", "aud", "type"]},
    )
