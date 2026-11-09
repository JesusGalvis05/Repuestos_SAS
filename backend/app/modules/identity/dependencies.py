from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings
from app.core.db import Db
from app.core.errors import DomainError
from app.core.security import decode_access, now
from app.modules.identity.models import User
from app.modules.identity.repository import IdentityRepository

bearer = HTTPBearer(auto_error=False)


def current_user(
    db: Db, credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]
) -> User:
    denied = DomainError("UNAUTHENTICATED", "Inicie sesión para continuar.", 401)
    if credentials is None:
        raise denied
    try:
        claims = decode_access(credentials.credentials, get_settings())
        if claims["type"] != "access":
            raise denied
        user_id, session_id = UUID(claims["sub"]), UUID(claims["sid"])
    except (jwt.InvalidTokenError, ValueError, KeyError, TypeError):
        raise denied from None
    repo = IdentityRepository(db)
    session = repo.session(session_id)
    user = repo.user(user_id)
    if (
        not user
        or not user.active
        or not session
        or session.user_id != user_id
        or session.revoked_at
        or session.expires_at <= now()
    ):
        raise denied
    return user


CurrentUser = Annotated[User, Depends(current_user)]


def require(permission: str):
    def check(user: CurrentUser) -> User:
        if permission not in user.permission_codes:
            raise DomainError("FORBIDDEN", "No tiene permiso para realizar esta operación.", 403)
        return user

    return check
