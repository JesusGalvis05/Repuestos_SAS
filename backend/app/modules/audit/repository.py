from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.audit.models import AuditLog


def record(
    db: Session,
    action: str,
    actor_id: UUID | None = None,
    target_id: str | None = None,
    details: dict | None = None,
):
    db.add(AuditLog(action=action, actor_id=actor_id, target_id=target_id, details=details or {}))
