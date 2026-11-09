"""Knowledge graph endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_user
from app.models.models import KnowledgeEntity, KnowledgeRelationship

router = APIRouter(prefix="/graph", tags=["graph"])
class EntityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=512)
    kind: str = "concept"
class RelCreate(BaseModel):
    source_entity_id: str
    target_entity_id: str
    relation: str = Field(default="related")
@router.get("")
def get_graph(db: Session = Depends(get_db), user=Depends(require_user)):
    entities = db.query(KnowledgeEntity).filter(KnowledgeEntity.user_id == user.id).all()
    rels = db.query(KnowledgeRelationship).filter(KnowledgeRelationship.user_id == user.id).all()
    return {"entities": [{"id": e.id, "name": e.name, "kind": e.kind, "meta": e.meta} for e in entities], "relationships": [{"id": r.id, "source_entity_id": r.source_entity_id, "target_entity_id": r.target_entity_id, "relation": r.relation} for r in rels]}
@router.post("/entities")
def create_entity(payload: EntityCreate, db: Session = Depends(get_db), user=Depends(require_user)):
    existing = db.query(KnowledgeEntity).filter(KnowledgeEntity.user_id == user.id, KnowledgeEntity.name == payload.name).first()
    if existing: return {"id": existing.id, "name": existing.name, "kind": existing.kind, "deduplicated": True}
    e = KnowledgeEntity(user_id=user.id, name=payload.name, kind=payload.kind)
    db.add(e); db.commit(); db.refresh(e)
    return {"id": e.id, "name": e.name, "kind": e.kind}
@router.post("/relationships")
def create_rel(payload: RelCreate, db: Session = Depends(get_db), user=Depends(require_user)):
    for eid in (payload.source_entity_id, payload.target_entity_id):
        if not db.query(KnowledgeEntity).filter(KnowledgeEntity.id == eid, KnowledgeEntity.user_id == user.id).first():
            raise HTTPException(404, "Entity not found")
    r = KnowledgeRelationship(user_id=user.id, source_entity_id=payload.source_entity_id, target_entity_id=payload.target_entity_id, relation=payload.relation)
    db.add(r); db.commit(); db.refresh(r)
    return {"id": r.id, "source_entity_id": r.source_entity_id, "target_entity_id": r.target_entity_id, "relation": r.relation}
