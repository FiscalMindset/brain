"""User memory CRUD (user-scoped)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_user
from app.models.models import UserMemory

router = APIRouter(prefix="/memory", tags=["memory"])
class MemoryCreate(BaseModel):
    key: str = Field(min_length=1, max_length=256)
    value: str = ""
    meta: dict = Field(default_factory=dict)
class MemoryPatch(BaseModel):
    value: str | None = None
    meta: dict | None = None
def _out(m): return {"id": m.id, "key": m.key, "value": m.value, "meta": m.meta}
@router.get("")
def list_memory(db: Session = Depends(get_db), user=Depends(require_user)):
    return [_out(m) for m in db.query(UserMemory).filter(UserMemory.user_id == user.id).all()]
@router.post("")
def create_memory(payload: MemoryCreate, db: Session = Depends(get_db), user=Depends(require_user)):
    m = UserMemory(user_id=user.id, key=payload.key, value=payload.value, meta=payload.meta)
    db.add(m); db.commit(); db.refresh(m)
    return _out(m)
@router.patch("/{memory_id}")
def patch_memory(memory_id: str, payload: MemoryPatch, db: Session = Depends(get_db), user=Depends(require_user)):
    m = db.query(UserMemory).filter(UserMemory.id == memory_id, UserMemory.user_id == user.id).first()
    if not m: raise HTTPException(404, "Memory not found")
    if payload.value is not None: m.value = payload.value
    if payload.meta is not None: m.meta = payload.meta
    db.commit(); db.refresh(m)
    return _out(m)
@router.delete("/{memory_id}")
def delete_memory(memory_id: str, db: Session = Depends(get_db), user=Depends(require_user)):
    m = db.query(UserMemory).filter(UserMemory.id == memory_id, UserMemory.user_id == user.id).first()
    if not m: raise HTTPException(404, "Memory not found")
    db.delete(m); db.commit()
    return {"deleted": True, "id": memory_id}
