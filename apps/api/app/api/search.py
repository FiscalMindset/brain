"""Keyword search over ingested documents, with citations."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_user
from app.services.retrieval import citation_for, search_documents

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
def search(
    q: str = Query(default=""),
    kind: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user=Depends(require_user),
):
    """Return matching document chunks plus citations."""
    docs = search_documents(db, user.id, q, kind=kind, limit=limit)
    return {
        "query": q,
        "count": len(docs),
        "results": [
            {
                "document_id": doc.id,
                "source_id": doc.source_id,
                "chunk_index": doc.chunk_index,
                "text": doc.text,
                "citation": citation_for(doc),
            }
            for doc in docs
        ],
        "citations": [citation_for(d) for d in docs],
    }
