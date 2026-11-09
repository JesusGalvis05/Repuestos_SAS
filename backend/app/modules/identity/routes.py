from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response

from app.core.config import get_settings
from app.core.db import Db
from app.core.errors import DomainError, error_response
from app.modules.identity.dependencies import CurrentUser, require
from app.modules.identity.models import User
from app.modules.identity.schemas import (
    ChangePassword,
    Login,
    SessionView,
    TokenView,
    UserCreate,
    UserPage,
    UserUpdate,
    UserView,
)
from app.modules.identity.services import AuthResult, IdentityService, user_view

router = APIRouter()
Admin = Annotated[User, Depends(require("users.manage"))]
COOKIE = "jg_refresh"
COOKIE_PATH = "/api/v1/auth"


def check_origin(request: Request, required: bool = False):
    origin = request.headers.get("origin")
    if (required and not origin) or (origin and origin not in get_settings().allowed_origins):
        raise DomainError("UNTRUSTED_ORIGIN", "Origen de solicitud no permitido.", 403)


def clear_cookie(response: Response):
    response.delete_cookie(
        COOKIE,
        path=COOKIE_PATH,
        secure=get_settings().cookie_secure,
        httponly=True,
        samesite="strict",
    )


def auth_response(result: AuthResult, response: Response):
    if result.error:
        failure = error_response(result.error.code, result.error.message, result.error.status)
        clear_cookie(failure)
        return failure
    response.set_cookie(
        COOKIE,
        result.refresh_token,
        httponly=True,
        secure=get_settings().cookie_secure,
        samesite="strict",
        path=COOKIE_PATH,
        max_age=get_settings().refresh_token_days * 86400,
    )
    response.headers["Cache-Control"] = "no-store"
    return result.tokens


@router.post("/auth/login", response_model=TokenView, tags=["Autenticación"])
def login(data: Login, request: Request, response: Response, db: Db):
    check_origin(request)
    result = IdentityService(db, get_settings()).login(
        str(data.email), data.password.get_secret_value(), request.headers.get("user-agent", "")
    )
    return auth_response(result, response)


@router.post("/auth/refresh", response_model=TokenView, tags=["Autenticación"])
def refresh(request: Request, response: Response, db: Db):
    check_origin(request, required=True)
    result = IdentityService(db, get_settings()).refresh(request.cookies.get(COOKIE, ""))
    return auth_response(result, response)


@router.post("/auth/logout", status_code=204, tags=["Autenticación"])
def logout(request: Request, db: Db):
    check_origin(request, required=True)
    IdentityService(db, get_settings()).logout(request.cookies.get(COOKIE))
    response = Response(status_code=204)
    clear_cookie(response)
    return response


@router.get("/auth/me", response_model=UserView, tags=["Autenticación"])
def me(user: CurrentUser):
    return user_view(user)


@router.post("/auth/change-password", status_code=204, tags=["Autenticación"])
def change_password(data: ChangePassword, user: CurrentUser, db: Db):
    IdentityService(db, get_settings()).change_password(
        user.id, data.current_password.get_secret_value(), data.new_password.get_secret_value()
    )
    response = Response(status_code=204)
    clear_cookie(response)
    return response


@router.get("/auth/sessions", response_model=list[SessionView], tags=["Autenticación"])
def sessions(user: CurrentUser, db: Db):
    return IdentityService(db, get_settings()).sessions(user.id)


@router.delete("/auth/sessions/{session_id}", status_code=204, tags=["Autenticación"])
def revoke_session(session_id: UUID, user: CurrentUser, db: Db):
    IdentityService(db, get_settings()).revoke_session(user.id, session_id)
    return Response(status_code=204)


@router.get("/users", response_model=UserPage, tags=["Usuarios"])
def users(
    db: Db,
    actor: Admin,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", max_length=120),
):
    return IdentityService(db, get_settings()).users(page, page_size, search)


@router.post("/users", response_model=UserView, status_code=201, tags=["Usuarios"])
def create_user(data: UserCreate, actor: Admin, db: Db):
    return IdentityService(db, get_settings()).create_user(data, actor.id)


@router.patch("/users/{user_id}", response_model=UserView, tags=["Usuarios"])
def update_user(user_id: UUID, data: UserUpdate, actor: Admin, db: Db):
    return IdentityService(db, get_settings()).update_user(user_id, data, actor.id)


@router.get("/roles", tags=["Usuarios"])
def roles(db: Db, actor: Admin):
    return IdentityService(db, get_settings()).roles()
