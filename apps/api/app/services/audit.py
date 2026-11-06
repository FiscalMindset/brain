"""Audit-event writer. Failures must never break the request path."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.models import AuditEvent


def record_audit(
    db: Session,
    action: str,
    *,
    user_id: str | None = None,
    target: str | None = None,
    detail: dict | None = None,
) -> AuditEvent | None:
    """Persist an :class:`AuditEvent` inside the caller's transaction.

    Returns the event, or ``None`` if writing failed (never raises).
    """
    try:
        event = AuditEvent(user_id=user_id, action=action, target=target, detail=detail or {})
        db.add(event)
        db.flush()
        return event
    except Exception:  # pragma: no cover - defensive; audit must not break requests
        db.rollback()
        return None
