"""Audit events (user-scoped, paginated)."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_user
from app.models.models import AuditEvent
router = APIRouter(prefix="/audit", tags=["audit"])
@router.get("")
def list_audit(limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0), db: Session = Depends(get_db), user=Depends(require_user)):
    q = db.query(AuditEvent).filter(AuditEvent.user_id == user.id).order_by(AuditEvent.created_at.desc())
    total = q.count()
    rows = q.offset(offset).limit(limit).all()
    return {"total": total, "limit": limit, "offset": offset, "events": [{"id": e.id, "action": e.action, "target": e.target, "detail": e.detail, "created_at": e.created_at.isoformat() if e.created_at else None} for e in rows]}
