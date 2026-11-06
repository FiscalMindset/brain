"""Orchestrated research workflow (research -> review -> plan)."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_user
from app.models.models import ResearchSession
from app.services.agents import run_orchestration
from app.services.audit import record_audit

router = APIRouter(prefix="/research", tags=["research"])


class ResearchRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=10, ge=1, le=50)


@router.post("")
def run_research(
    payload: ResearchRequest,
    db: Session = Depends(get_db),
    user=Depends(require_user),
):
    """Run the orchestrated workflow and persist the structured report."""
    output = run_orchestration(db, user.id, payload.query)
    session = ResearchSession(user_id=user.id, query=payload.query, report=output)
    db.add(session)
    record_audit(db, "research.run", user_id=user.id, target=session.id, detail={"query": payload.query})
    db.commit()
    db.refresh(session)
    return {"session_id": session.id, **output}
