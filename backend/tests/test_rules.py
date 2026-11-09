from uuid import uuid4

import jwt
import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.core.security import (
    decode_access,
    hash_password,
    issue_access,
    token_digest,
    verify_password,
)
from app.modules.identity.schemas import UserCreate


def settings(**kwargs):
    kwargs.setdefault("docker_runtime", False)
    return Settings(
        _env_file=None,
        database_url="postgresql+psycopg://unit@localhost:5432/unit",
        jwt_secret="unit-test-secret-with-more-than-32-characters",
        **kwargs,
    )


def test_password_is_argon2_and_verifies():
    hashed = hash_password("a long test password")
    assert hashed.startswith("$argon2id$")
    assert verify_password("a long test password", hashed)
    assert not verify_password("another password", hashed)


def test_access_contract_and_wrong_key():
    user_id, session_id = uuid4(), uuid4()
    token = issue_access(user_id, session_id, settings())
    claims = decode_access(token, settings())
    assert claims["sub"] == str(user_id)
    assert claims["sid"] == str(session_id)
    assert claims["exp"] - claims["iat"] == 600
    with pytest.raises(jwt.InvalidTokenError):
        decode_access(
            token,
            Settings(
                _env_file=None,
                database_url="postgresql+psycopg://unit@localhost:5432/unit",
                docker_runtime=False,
                jwt_secret="a different secret that is sufficiently long",
            ),
        )


@pytest.mark.parametrize("secret", ["short", "REPLACE_WITH_RANDOM_SECRET_AT_LEAST_32_CHARACTERS"])
def test_insecure_secret_rejected(secret):
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            database_url="postgresql+psycopg://unit@localhost:5432/unit",
            docker_runtime=False,
            jwt_secret=secret,
        )


def test_production_requires_https_and_secure_cookies():
    with pytest.raises(ValidationError):
        settings(app_env="production", cookie_secure=False)


def test_schema_rejects_short_password_blank_name_and_extra_fields():
    for overrides in [{"password": "short"}, {"full_name": "   "}, {"active": True}]:
        data = {
            "email": "seller@example.com",
            "full_name": "Vendedor de prueba",
            "password": "long-enough-password",
            "roles": ["seller"],
        }
        data.update(overrides)
        with pytest.raises(ValidationError):
            UserCreate(**data)


def test_only_digests_of_refresh_tokens_are_persisted():
    assert len(token_digest("refresh-secret")) == 64
    assert token_digest("refresh-secret") != token_digest("other-secret")
