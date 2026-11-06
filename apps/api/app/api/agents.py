"""Agent catalogue and in-process orchestrator execution."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_user
from app.services.agents import AGENTS, AGENT_NAMES, run_orchestration

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("")
def list_agents():
    """Return the agent catalogue with roles and permissions."""
    return {"agents": AGENTS, "count": len(AGENTS)}


class AgentRunRequest(BaseModel):
    agent: str = "orchestrator"
    query: str = Field(min_length=1)


@router.post("/run")
def run_agent(payload: AgentRunRequest, db: Session = Depends(get_db), user=Depends(require_user)):
    """Execute the orchestrator delegation chain in-process."""
    if payload.agent not in AGENT_NAMES:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=f"Unknown agent '{payload.agent}'. Known: {AGENT_NAMES}")
    output = run_orchestration(db, user.id, payload.query)
    db.commit()
    return {"agent": payload.agent, **output}
