"""Hybrid keyword + metadata retrieval over Document rows.

Tokenized ANY-word scoring: tokens split on whitespace, score = matched
term count, rank by score desc then created_at desc.
"""
from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.models import Document

def escape_like(term: str) -> str:
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

def tokenize_query(query: str) -> list[str]:
    return [w.lower() for w in (query or "").replace(","," ").split() if w.strip()]

def search_documents(db, user_id, query, *, kind=None, source_id=None, since=None, limit=20):
    limit = max(1, min(limit, 100))
    if since is not None and since.tzinfo is None:
        since = since.replace(tzinfo=timezone.utc)
    stmt = db.query(Document).filter(Document.user_id == user_id)
    if source_id:
        stmt = stmt.filter(Document.source_id == source_id)
    if since is not None:
        stmt = stmt.filter(Document.created_at >= since)
    if kind:
        from app.models.models import Source
        stmt = stmt.join(Source, Source.id == Document.source_id).filter(Source.kind == kind)
    terms = tokenize_query(query or "")
    if not terms:
        return stmt.order_by(Document.created_at.desc()).limit(limit).all()
    # ANY-word: fetch candidates matching any term, score in Python
    from sqlalchemy import or_
    conds = [Document.text.ilike(f"%{escape_like(t)}%", escape="\\") for t in terms]
    docs = stmt.filter(or_(*conds)).all()
    def score(doc):
        low = doc.text.lower()
        return sum(1 for t in terms if t in low)
    docs.sort(key=lambda d: (-score(d), d.created_at or datetime.min.replace(tzinfo=timezone.utc)), reverse=False)
    # python sort: score desc, recency desc -> use key with negative? handle recency via timestamp
    docs = sorted(docs, key=lambda d: d.created_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    docs = sorted(docs, key=lambda d: score(d), reverse=True)
    return docs[:limit]

def citation_for(doc):
    return {"document_id": doc.id, "source_id": doc.source_id, "chunk_index": doc.chunk_index, "snippet": doc.text[:280], "meta": doc.meta or {}}
