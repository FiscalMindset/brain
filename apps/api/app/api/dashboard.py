"""Dashboard aggregated counts."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_user
from app.models.models import AuditEvent, Document, KnowledgeEntity, Project, ProjectTask, ResearchSession, Source, UserMemory
router = APIRouter(prefix="/dashboard", tags=["dashboard"])
@router.get("")
def dashboard(db: Session = Depends(get_db), user=Depends(require_user)):
    uid = user.id
    recent = db.query(AuditEvent).filter(AuditEvent.user_id == uid).order_by(AuditEvent.created_at.desc()).limit(10).all()
    return {
      "counts": {
        "sources": db.query(Source).filter(Source.user_id == uid).count(),
        "documents": db.query(Document).filter(Document.user_id == uid).count(),
        "projects": db.query(Project).filter(Project.user_id == uid).count(),
        "tasks": db.query(ProjectTask).join(Project, Project.id == ProjectTask.project_id).filter(Project.user_id == uid).count(),
        "research_sessions": db.query(ResearchSession).filter(ResearchSession.user_id == uid).count(),
        "memories": db.query(UserMemory).filter(UserMemory.user_id == uid).count(),
        "entities": db.query(KnowledgeEntity).filter(KnowledgeEntity.user_id == uid).count(),
      },
      "recent_activity": [{"id": e.id, "action": e.action, "target": e.target, "created_at": e.created_at.isoformat() if e.created_at else None} for e in recent],
      "coverage": {"has_sources": db.query(Source).filter(Source.user_id == uid).count() > 0},
    }
