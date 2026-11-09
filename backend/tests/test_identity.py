from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from alembic import command
from sqlalchemy import func, select

from app.core.config import get_settings
from app.core.errors import DomainError
from app.modules.audit.models import AuditLog
from app.modules.identity.models import AuthSession, RefreshToken, User
from app.modules.identity.services import IdentityService

pytestmark = pytest.mark.postgres


def test_migration_roundtrip_and_model_drift(environment):
    client, factory, config = environment
    assert client.get("/api/v1/ready").status_code == 200
    command.check(config)
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    command.check(config)
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(User)) == 0


def test_bootstrap_and_last_admin_are_protected(admin):
    client, factory, user = admin
    with factory() as db, db.begin(), pytest.raises(DomainError, match="Ya existe"):
        IdentityService(db, get_settings()).bootstrap(
            "second@example.com", "Segundo admin", "long-new-password"
        )
    response = client.patch(f"/api/v1/users/{user.id}", json={"active": False})
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "LAST_ADMIN"


def test_login_logout_and_cookie_flags(admin):
    client, factory, user = admin
    login = client.post(
        "/api/v1/auth/login",
        json={"email": user.email.upper(), "password": "test-password-secure-123"},
    )
    assert login.status_code == 200
    assert "httponly" in login.headers["set-cookie"].lower()
    assert "samesite=strict" in login.headers["set-cookie"].lower()
    token = login.json()["access_token"]
    client.headers["Authorization"] = "Bearer " + token
    assert client.get("/api/v1/auth/me").json()["email"] == user.email
    assert client.post("/api/v1/auth/logout").status_code == 204
    assert client.post("/api/v1/auth/logout").status_code == 204
    assert client.get("/api/v1/auth/me").status_code == 401
    with factory() as db:
        assert (
            db.scalar(
                select(func.count()).select_from(AuditLog).where(AuditLog.action == "auth.logout")
            )
            == 1
        )


def test_seller_rbac_and_no_internal_cost_permission(admin):
    client, _factory, _user = admin
    response = client.post(
        "/api/v1/users",
        json={
            "email": "seller@example.com",
            "full_name": "Vendedor de prueba",
            "password": "seller-password-123",
            "roles": ["seller"],
        },
    )
    assert response.status_code == 201
    assert "costs.read" not in response.json()["permissions"]
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "seller@example.com", "password": "seller-password-123"},
    )
    client.headers["Authorization"] = "Bearer " + login.json()["access_token"]
    assert client.get("/api/v1/users").status_code == 403
    assert client.get("/api/v1/roles").status_code == 403
    assert (
        client.post(
            "/api/v1/users",
            json={
                "email": "other@example.com",
                "full_name": "Otro usuario",
                "password": "other-password-123",
                "roles": ["admin"],
            },
        ).status_code
        == 403
    )


def test_refresh_rotation_and_replay_revokes_access(admin):
    client, factory, _user = admin
    old = client.cookies.get("jg_refresh")
    response = client.post("/api/v1/auth/refresh")
    assert response.status_code == 200
    assert client.cookies.get("jg_refresh") != old
    token = response.json()["access_token"]
    client.cookies.clear()
    client.cookies.set("jg_refresh", old, path="/api/v1/auth")
    assert client.post("/api/v1/auth/refresh").status_code == 401
    client.headers["Authorization"] = "Bearer " + token
    assert client.get("/api/v1/auth/me").status_code == 401
    with factory() as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(AuditLog)
                .where(AuditLog.action == "auth.refresh_replay")
            )
            == 1
        )
        assert all(t.token_hash != old for t in db.scalars(select(RefreshToken)))


def test_login_lockout_persists_even_with_401(admin):
    client, factory, user = admin
    for _ in range(5):
        assert (
            client.post(
                "/api/v1/auth/login", json={"email": user.email, "password": "wrong"}
            ).status_code
            == 401
        )
    assert (
        client.post(
            "/api/v1/auth/login", json={"email": user.email, "password": "test-password-secure-123"}
        ).status_code
        == 401
    )
    with factory() as db:
        assert db.get(User, user.id).locked_until is not None
        assert (
            db.scalar(
                select(func.count())
                .select_from(AuditLog)
                .where(AuditLog.action == "auth.login_failed")
            )
            == 5
        )


def test_change_password_revokes_all_sessions(admin):
    client, factory, user = admin
    assert (
        client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "test-password-secure-123",
                "new_password": "new-test-password-123",
            },
        ).status_code
        == 204
    )
    assert client.get("/api/v1/auth/me").status_code == 401
    assert (
        client.post(
            "/api/v1/auth/login", json={"email": user.email, "password": "new-test-password-123"}
        ).status_code
        == 200
    )
    with factory() as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(AuthSession)
                .where(AuthSession.revoked_at.is_not(None))
            )
            == 1
        )


def test_deactivated_user_cannot_use_existing_session(admin):
    client, _factory, _user = admin
    created = client.post(
        "/api/v1/users",
        json={
            "email": "inventory@example.com",
            "full_name": "Usuario de inventario",
            "password": "inventory-password-123",
            "roles": ["inventory"],
        },
    ).json()
    login = client.post(
        "/api/v1/auth/login", json={"email": created["email"], "password": "inventory-password-123"}
    ).json()
    assert client.patch(f"/api/v1/users/{created['id']}", json={"active": False}).status_code == 200
    client.headers["Authorization"] = "Bearer " + login["access_token"]
    assert client.get("/api/v1/auth/me").status_code == 401


def test_origin_validation_and_validation_does_not_echo_secrets(admin):
    client, _factory, _user = admin
    assert (
        client.post(
            "/api/v1/auth/refresh", headers={"Origin": "https://untrusted.example"}
        ).status_code
        == 403
    )
    response = client.post(
        "/api/v1/auth/login", json={"email": "invalid", "password": "secret-do-not-echo"}
    )
    assert response.status_code == 422
    assert "secret-do-not-echo" not in response.text
    assert response.headers["Cache-Control"] == "no-store"


def test_invalid_role_rolls_back_user_and_audit(admin):
    client, factory, _user = admin
    response = client.post(
        "/api/v1/users",
        json={
            "email": "invalid@example.com",
            "full_name": "Prueba de reversión",
            "password": "invalid-password-123",
            "roles": ["nonexistent"],
        },
    )
    assert response.status_code == 422
    with factory() as db:
        assert db.scalar(select(User).where(User.email == "invalid@example.com")) is None
        assert (
            db.scalar(
                select(func.count()).select_from(AuditLog).where(AuditLog.action == "users.created")
            )
            == 0
        )


def test_users_pagination_and_duplicate_email(admin):
    client, _factory, _user = admin
    payload = {
        "email": "second@example.com",
        "full_name": "Segundo usuario",
        "password": "second-password-123",
        "roles": ["seller"],
    }
    assert client.post("/api/v1/users", json=payload).status_code == 201
    assert client.post("/api/v1/users", json=payload).status_code == 409
    page = client.get("/api/v1/users", params={"page": 2, "page_size": 1}).json()
    assert page["total"] == 2 and len(page["items"]) == 1
    assert client.get("/api/v1/users?page=0").status_code == 422


def test_concurrent_refresh_has_one_success_and_detects_replay(admin):
    client, factory, _user = admin
    raw = client.cookies.get("jg_refresh")
    barrier = Barrier(2)

    def renew():
        barrier.wait(timeout=10)
        with factory() as db, db.begin():
            result = IdentityService(db, get_settings()).refresh(raw)
            return result.error.code if result.error else "ok"

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: renew(), range(2)))
    assert sorted(results) == ["INVALID_SESSION", "ok"]
    with factory() as db:
        assert db.scalar(select(AuthSession)).revoked_at is not None


def test_concurrent_bootstrap_creates_only_one_admin(environment):
    _client, factory, _config = environment
    barrier = Barrier(2)

    def bootstrap(index):
        barrier.wait(timeout=10)
        try:
            with factory() as db, db.begin():
                IdentityService(db, get_settings()).bootstrap(
                    f"admin{index}@example.com", "Admin concurrente", "test-password-123"
                )
            return "ok"
        except DomainError as exc:
            return exc.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(bootstrap, range(2)))
    assert sorted(results) == ["ADMIN_EXISTS", "ok"]
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(User)) == 1


def test_concurrent_changes_preserve_one_active_admin(admin):
    client, factory, user = admin
    response = client.post(
        "/api/v1/users",
        json={
            "email": "admin2@example.com",
            "full_name": "Otro administrador",
            "password": "admin-password-123",
            "roles": ["admin"],
        },
    )
    assert response.status_code == 201
    from uuid import UUID

    from app.modules.identity.schemas import UserUpdate

    ids = [user.id, UUID(response.json()["id"])]
    barrier = Barrier(2)

    def deactivate(user_id):
        barrier.wait(timeout=10)
        try:
            with factory() as db, db.begin():
                IdentityService(db, get_settings()).update_user(
                    user_id, UserUpdate(active=False), user_id
                )
            return "ok"
        except DomainError as exc:
            return exc.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(deactivate, ids))
    assert sorted(results) == ["LAST_ADMIN", "ok"]
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(User).where(User.active.is_(True))) == 1


def test_revoke_session_is_owned_and_idempotent(admin):
    client, factory, _user = admin
    session_id = client.get("/api/v1/auth/sessions").json()[0]["id"]
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "test-password-secure-123"},
    )
    client.headers["Authorization"] = "Bearer " + login.json()["access_token"]
    assert client.delete(f"/api/v1/auth/sessions/{session_id}").status_code == 204
    assert client.delete(f"/api/v1/auth/sessions/{session_id}").status_code == 204
    with factory() as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(AuditLog)
                .where(AuditLog.action == "auth.session_revoked")
            )
            == 1
        )
    created = client.post(
        "/api/v1/users",
        json={
            "email": "seller@example.com",
            "full_name": "Vendedor de prueba",
            "password": "seller-password-123",
            "roles": ["seller"],
        },
    )
    assert created.status_code == 201
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "seller@example.com", "password": "seller-password-123"},
    )
    client.headers["Authorization"] = "Bearer " + login.json()["access_token"]
    assert client.delete(f"/api/v1/auth/sessions/{session_id}").status_code == 404
