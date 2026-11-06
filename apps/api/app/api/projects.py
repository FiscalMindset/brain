"""Projects and their tasks, plus issue-draft generation."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_user
from app.models.models import Project, ProjectTask
from app.services.audit import record_audit

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=512)
    description: str = ""
    status: str = "active"


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=512)
    body: str = ""
    status: str = "todo"
    assignee: str | None = None


def _get_project(db: Session, user_id: str, project_id: str) -> Project:
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _project_out(project: Project) -> dict:
    return {
        "id": project.id, "title": project.title, "description": project.description,
        "status": project.status, "meta": project.meta,
        "tasks": [_task_out(t) for t in project.tasks],
    }


def _task_out(task: ProjectTask) -> dict:
    return {
        "id": task.id, "project_id": task.project_id, "title": task.title,
        "body": task.body, "status": task.status, "assignee": task.assignee,
    }


@router.post("")
def create_project(payload: ProjectCreate, db: Session = Depends(get_db), user=Depends(require_user)):
    project = Project(user_id=user.id, title=payload.title, description=payload.description, status=payload.status)
    db.add(project)
    db.flush()
    record_audit(db, "project.create", user_id=user.id, target=project.id)
    db.commit()
    db.refresh(project)
    return _project_out(project)


@router.get("")
def list_projects(db: Session = Depends(get_db), user=Depends(require_user)):
    return [_project_out(p) for p in db.query(Project).filter(Project.user_id == user.id)]


@router.get("/{project_id}")
def get_project(project_id: str, db: Session = Depends(get_db), user=Depends(require_user)):
    return _project_out(_get_project(db, user.id, project_id))


@router.post("/{project_id}/tasks")
def add_task(project_id: str, payload: TaskCreate, db: Session = Depends(get_db), user=Depends(require_user)):
    project = _get_project(db, user.id, project_id)
    task = ProjectTask(
        project_id=project.id, title=payload.title, body=payload.body,
        status=payload.status, assignee=payload.assignee,
    )
    db.add(task)
    record_audit(db, "task.create", user_id=user.id, target=task.id, detail={"project_id": project.id})
    db.commit()
    db.refresh(task)
    return _task_out(task)


@router.post("/{project_id}/issue-draft")
def issue_draft(project_id: str, db: Session = Depends(get_db), user=Depends(require_user)):
    """Draft a GitHub-style issue from the project's tasks (text only, no push)."""
    project = _get_project(db, user.id, project_id)
    lines = [f"# {project.title}", project.description or "", "## Tasks"]
    lines += [f"- [{t.status}] {t.title}" + (f" (@{t.assignee})" if t.assignee else "") for t in project.tasks]
    if not project.tasks:
        lines.append("- (no tasks yet)")
    return {
        "project_id": project.id,
        "title": project.title,
        "body": "\n".join(lines),
        "labels": ["secondbrain"],
        "human_approval": True,
    }
