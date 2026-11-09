from uuid import UUID

from sqlalchemy import func, select, text, update
from sqlalchemy.orm import Session

from app.modules.identity.models import AuthSession, RefreshToken, Role, User


class IdentityRepository:
    def __init__(self, db: Session):
        self.db = db

    def user_by_email(self, email: str, *, lock: bool = False) -> User | None:
        stmt = select(User).where(User.email == email.strip().lower())
        return self.db.scalar(stmt.with_for_update() if lock else stmt)

    def user(self, user_id: UUID, *, lock: bool = False) -> User | None:
        stmt = select(User).where(User.id == user_id)
        return self.db.scalar(
            stmt.with_for_update().execution_options(populate_existing=True) if lock else stmt
        )

    def users(self, page: int, page_size: int, search: str) -> tuple[list[User], int]:
        pattern = "%" + search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        condition = User.email.ilike(pattern, escape="\\") | User.full_name.ilike(
            pattern, escape="\\"
        )
        total = self.db.scalar(select(func.count()).select_from(User).where(condition)) or 0
        users = self.db.scalars(
            select(User)
            .where(condition)
            .order_by(User.created_at, User.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        return list(users), total

    def roles(self, codes: list[str] | None = None) -> list[Role]:
        stmt = select(Role).order_by(Role.code)
        if codes is not None:
            stmt = stmt.where(Role.code.in_(codes))
        return list(self.db.scalars(stmt).all())

    def lock_administration(self):
        # Una clave compartida por aprovisionamiento y cambios de roles/estado.
        self.db.execute(text("SELECT pg_advisory_xact_lock(74218001)"))

    def active_admins(self) -> int:
        return (
            self.db.scalar(
                select(func.count())
                .select_from(User)
                .where(User.active.is_(True), User.roles.any(Role.code == "admin"))
            )
            or 0
        )

    def session(self, session_id: UUID, *, lock: bool = False) -> AuthSession | None:
        stmt = select(AuthSession).where(AuthSession.id == session_id)
        return self.db.scalar(
            stmt.with_for_update().execution_options(populate_existing=True) if lock else stmt
        )

    def refresh(self, digest: str, *, lock: bool = False) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == digest)
        return self.db.scalar(
            stmt.with_for_update().execution_options(populate_existing=True) if lock else stmt
        )

    def revoke_all(self, user_id: UUID, instant):
        self.db.execute(
            update(AuthSession)
            .where(AuthSession.user_id == user_id, AuthSession.revoked_at.is_(None))
            .values(revoked_at=instant)
        )

    def sessions(self, user_id: UUID, instant) -> list[AuthSession]:
        return list(
            self.db.scalars(
                select(AuthSession)
                .where(
                    AuthSession.user_id == user_id,
                    AuthSession.revoked_at.is_(None),
                    AuthSession.expires_at > instant,
                )
                .order_by(AuthSession.created_at.desc())
            ).all()
        )
