import secrets
from dataclasses import dataclass
from datetime import timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.errors import DomainError
from app.core.security import (
    DUMMY_HASH,
    hash_password,
    issue_access,
    now,
    token_digest,
    verify_password,
)
from app.modules.audit.repository import record
from app.modules.identity.models import AuthSession, RefreshToken, User
from app.modules.identity.repository import IdentityRepository
from app.modules.identity.schemas import TokenView, UserCreate, UserPage, UserUpdate, UserView


def user_view(user: User) -> UserView:
    return UserView(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        active=user.active,
        roles=sorted(r.code for r in user.roles),
        permissions=user.permission_codes,
        last_login_at=user.last_login_at,
    )


@dataclass
class AuthResult:
    tokens: TokenView | None = None
    refresh_token: str | None = None
    error: DomainError | None = None


class IdentityService:
    def __init__(self, db: Session, settings: Settings):
        self.db, self.settings, self.repo = db, settings, IdentityRepository(db)

    def users(self, page: int, page_size: int, search: str) -> UserPage:
        items, total = self.repo.users(page, page_size, search)
        return UserPage(
            items=[user_view(u) for u in items], total=total, page=page, page_size=page_size
        )

    def roles(self) -> list[dict]:
        return [
            {"code": r.code, "name": r.name, "permissions": sorted(p.code for p in r.permissions)}
            for r in self.repo.roles()
        ]

    def sessions(self, user_id: UUID) -> list[AuthSession]:
        return self.repo.sessions(user_id, now())

    def revoke_session(self, user_id: UUID, session_id: UUID):
        self.repo.user(user_id, lock=True)
        session = self.repo.session(session_id, lock=True)
        if not session or session.user_id != user_id:
            raise DomainError("SESSION_NOT_FOUND", "Sesión no encontrada.", 404)
        if not session.revoked_at:
            session.revoked_at = now()
            record(self.db, "auth.session_revoked", user_id, str(session.id))

    def _tokens(self, user: User, session: AuthSession) -> AuthResult:
        raw = secrets.token_urlsafe(48)
        self.db.add(RefreshToken(session_id=session.id, token_hash=token_digest(raw)))
        self.db.flush()
        return AuthResult(
            TokenView(
                access_token=issue_access(user.id, session.id, self.settings),
                expires_in=self.settings.access_token_minutes * 60,
                user=user_view(user),
            ),
            raw,
        )

    def login(self, email: str, password: str, user_agent: str) -> AuthResult:
        user = self.repo.user_by_email(email, lock=True)
        valid = verify_password(password, user.password_hash if user else DUMMY_HASH)
        instant = now()
        denied = DomainError(
            "INVALID_CREDENTIALS", "Credenciales inválidas o acceso temporalmente bloqueado.", 401
        )
        if not user:
            record(self.db, "auth.login_failed")
            return AuthResult(error=denied)
        if not user.active or (user.locked_until and user.locked_until > instant):
            record(self.db, "auth.login_denied", user.id)
            return AuthResult(error=denied)
        if not valid:
            user.failed_attempts += 1
            if user.failed_attempts >= self.settings.login_max_attempts:
                user.locked_until = instant + timedelta(minutes=self.settings.login_lock_minutes)
                user.failed_attempts = 0
            record(self.db, "auth.login_failed", user.id)
            return AuthResult(error=denied)
        user.failed_attempts, user.locked_until, user.last_login_at = 0, None, instant
        session = AuthSession(
            user_id=user.id,
            expires_at=instant + timedelta(days=self.settings.refresh_token_days),
            user_agent=user_agent[:256],
        )
        self.db.add(session)
        self.db.flush()
        record(self.db, "auth.login", user.id, str(session.id))
        return self._tokens(user, session)

    def refresh(self, raw: str) -> AuthResult:
        denied = DomainError("INVALID_SESSION", "La sesión expiró. Inicie sesión nuevamente.", 401)
        token = self.repo.refresh(token_digest(raw))
        if not token:
            return AuthResult(error=denied)
        original_session = self.repo.session(token.session_id)
        if not original_session:
            return AuthResult(error=denied)
        # Orden de bloqueos consistente: usuario -> sesión -> token.
        user = self.repo.user(original_session.user_id, lock=True)
        session = self.repo.session(token.session_id, lock=True)
        token = self.repo.refresh(token_digest(raw), lock=True)
        instant = now()
        if not user or not user.active or session.revoked_at or session.expires_at <= instant:
            return AuthResult(error=denied)
        if token.consumed_at:
            session.revoked_at = instant
            record(self.db, "auth.refresh_replay", user.id, str(session.id))
            return AuthResult(error=denied)
        token.consumed_at = instant
        record(self.db, "auth.refresh", user.id, str(session.id))
        return self._tokens(user, session)

    def logout(self, raw: str | None):
        token = self.repo.refresh(token_digest(raw)) if raw else None
        if token:
            original = self.repo.session(token.session_id)
            self.repo.user(original.user_id, lock=True)
            session = self.repo.session(token.session_id, lock=True)
            if not session.revoked_at:
                session.revoked_at = now()
                record(self.db, "auth.logout", session.user_id, str(session.id))

    def change_password(self, user_id: UUID, current: str, new: str):
        user = self.repo.user(user_id, lock=True)
        if not verify_password(current, user.password_hash):
            raise DomainError("INVALID_PASSWORD", "La contraseña actual no es correcta.", 400)
        if verify_password(new, user.password_hash):
            raise DomainError("PASSWORD_REUSED", "La contraseña nueva debe ser diferente.", 400)
        user.password_hash = hash_password(new)
        self.repo.revoke_all(user.id, now())
        record(self.db, "auth.password_changed", user.id)

    def roles_for(self, codes: list[str]):
        roles = self.repo.roles(codes)
        if len(roles) != len(set(codes)):
            raise DomainError("INVALID_ROLES", "Uno o más roles no existen.", 422)
        return roles

    def _administration(self, actor_id: UUID):
        self.repo.lock_administration()
        actor = self.repo.user(actor_id, lock=True)
        if not actor or not actor.active or "users.manage" not in actor.permission_codes:
            raise DomainError("FORBIDDEN", "No tiene permiso para administrar usuarios.", 403)

    def create_user(self, data: UserCreate, actor_id: UUID) -> UserView:
        self._administration(actor_id)
        if self.repo.user_by_email(str(data.email)):
            raise DomainError("EMAIL_EXISTS", "El correo ya está registrado.", 409)
        user = User(
            email=str(data.email).lower(),
            full_name=data.full_name,
            password_hash=hash_password(data.password.get_secret_value()),
            roles=self.roles_for(data.roles),
        )
        self.db.add(user)
        self.db.flush()
        record(self.db, "users.created", actor_id, str(user.id), {"roles": data.roles})
        return user_view(user)

    def update_user(self, user_id: UUID, data: UserUpdate, actor_id: UUID) -> UserView:
        self._administration(actor_id)
        user = self.repo.user(user_id, lock=True)
        if not user:
            raise DomainError("USER_NOT_FOUND", "Usuario no encontrado.", 404)
        was_admin = user.active and any(r.code == "admin" for r in user.roles)
        roles = self.roles_for(data.roles) if data.roles is not None else user.roles
        active = data.active if data.active is not None else user.active
        remains_admin = active and any(r.code == "admin" for r in roles)
        if was_admin and not remains_admin and self.repo.active_admins() <= 1:
            raise DomainError("LAST_ADMIN", "Debe conservar al menos un administrador activo.", 409)
        if data.full_name is not None:
            user.full_name = data.full_name
        user.active, user.roles = active, roles
        if data.active is not None or data.roles is not None:
            self.repo.revoke_all(user.id, now())
        self.db.flush()
        record(
            self.db,
            "users.updated",
            actor_id,
            str(user.id),
            {"active": active, "roles": [r.code for r in roles]},
        )
        return user_view(user)

    def bootstrap(self, email: str, full_name: str, password: str) -> UserView:
        self.repo.lock_administration()
        if self.repo.active_admins():
            raise DomainError(
                "ADMIN_EXISTS", "Ya existe un administrador activo. Use la administración web.", 409
            )
        if self.repo.user_by_email(email):
            raise DomainError("EMAIL_EXISTS", "El correo ya está registrado.", 409)
        data = UserCreate(email=email, full_name=full_name, password=password, roles=["admin"])
        user = User(
            email=str(data.email).lower(),
            full_name=data.full_name,
            password_hash=hash_password(password),
            roles=self.roles_for(["admin"]),
        )
        self.db.add(user)
        self.db.flush()
        record(self.db, "users.bootstrap", user.id, str(user.id))
        return user_view(user)
