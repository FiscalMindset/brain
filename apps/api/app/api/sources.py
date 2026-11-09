"""Source ingestion: create (with dedupe), list, fetch, upload."""
import ipaddress
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_user
from app.integrations.url_adapter import UrlAdapter, UrlFetchError, UrlOversizeError
from app.models.models import Document, Source
from app.services.audit import record_audit
from app.services.ingestion import chunk_text, extract_metadata, fingerprint

router = APIRouter(prefix="/sources", tags=["sources"])
class SourceCreate(BaseModel):
    kind: str = Field(default="note", max_length=64)
    title: str | None = Field(default=None, max_length=512)
    url: str | None = None
    content: str = Field(min_length=1)
    meta: dict = Field(default_factory=dict)
class SourceOut(BaseModel):
    id: str; kind: str; title: str | None; url: str | None; content_hash: str; chunks: int = 0; deduplicated: bool = False

class UrlIngestRequest(BaseModel):
    url: str

def _ingest(db, user, content, kind="note", title=None, url=None, meta=None):
    meta = meta or {}
    digest = fingerprint(content)
    existing = db.query(Source).filter(Source.user_id == user.id, Source.content_hash == digest).first()
    if existing is not None:
        return existing, True
    enriched = {**meta, **extract_metadata(content)}
    source = Source(user_id=user.id, kind=kind, title=title, url=url, content_hash=digest, content=content, meta=enriched)
    db.add(source); db.flush()
    for index, text in enumerate(chunk_text(content)):
        db.add(Document(user_id=user.id, source_id=source.id, chunk_index=index, text=text))
    record_audit(db, "source.create", user_id=user.id, target=source.id, detail={"kind": kind})
    return source, False

@router.post("", response_model=SourceOut)
def create_source(payload: SourceCreate, db: Session = Depends(get_db), user=Depends(require_user)):
    source, dedup = _ingest(db, user, payload.content, payload.kind, payload.title, payload.url, payload.meta)
    if not dedup: db.commit()
    count = db.query(Document).filter(Document.source_id == source.id).count()
    return SourceOut(id=source.id, kind=source.kind, title=source.title, url=source.url, content_hash=source.content_hash, chunks=count, deduplicated=dedup)

def _validate_url(raw: str) -> str:
    parsed = urlparse(raw)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(400, "Invalid URL: only http and https schemes are allowed")
    host = (parsed.hostname or "").lower()
    if not host or host in ("localhost",) or host.endswith((".localhost", ".local")):
        raise HTTPException(400, "Invalid URL: localhost is not allowed")
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast or ip.is_unspecified:
            raise HTTPException(400, "Invalid URL: private or reserved IP addresses are not allowed")
    except ValueError:
        # Not a literal IP (e.g. a domain name) — we do not resolve DNS.
        pass
    # Common literal private ranges that ip_address classifies as reserved/private are
    # covered above; also reject well-known literal encodings handled as plain hostnames:
    if host in ("0.0.0.0", "::", "[::1]", "::1"):
        raise HTTPException(400, "Invalid URL: private or reserved IP addresses are not allowed")
    return raw


@router.post("/url", response_model=SourceOut)
def ingest_url(payload: UrlIngestRequest, db: Session = Depends(get_db), user=Depends(require_user)):
    url = _validate_url(payload.url)
    try:
        text, title, meta = UrlAdapter().fetch(url)
    except UrlOversizeError:
        raise HTTPException(400, "Fetched content too large (500KB max)")
    except UrlFetchError as e:
        raise HTTPException(502, f"Failed to fetch URL: {e}")
    except Exception as e:
        raise HTTPException(502, f"Failed to fetch URL: {e}")
    if not text.strip():
        raise HTTPException(400, "Fetched URL contained no extractable text")
    source, dedup = _ingest(db, user, text, kind="url", title=title or None, url=url, meta=meta)
    if not dedup:
        db.commit()
    count = db.query(Document).filter(Document.source_id == source.id).count()
    return SourceOut(id=source.id, kind=source.kind, title=source.title, url=source.url, content_hash=source.content_hash, chunks=count, deduplicated=dedup)


@router.post("/upload")
def upload_sources(files: list[UploadFile], db: Session = Depends(get_db), user=Depends(require_user)):
    if len(files) > 5: raise HTTPException(400, "Maximum 5 files")
    results = []
    for f in files:
        name = (f.filename or "").lower()
        if not name.endswith((".pdf", ".md", ".txt")): raise HTTPException(400, f"Unsupported file type: {f.filename}")
        raw = f.file.read()
        if len(raw) > 2*1024*1024: raise HTTPException(400, "File too large (2MB max)")
        if name.endswith(".pdf"):
            try:
                from io import BytesIO

                from pypdf import PdfReader
                reader = PdfReader(BytesIO(raw))
                text = "\n".join((p.extract_text() or "") for p in reader.pages)
            except ImportError:
                raise HTTPException(400, "PDF support requires pypdf (install pypdf)")
            except Exception as e:
                raise HTTPException(400, f"Failed to read PDF: {e}")
        else:
            try: text = raw.decode("utf-8")
            except UnicodeDecodeError: text = raw.decode("latin-1")
        source, dedup = _ingest(db, user, text, kind="upload", title=f.filename)
        results.append({"filename": f.filename, "source_id": source.id, "deduplicated": dedup})
    db.commit()
    return {"uploaded": len(results), "results": results}

@router.get("", response_model=list[SourceOut])
def list_sources(db: Session = Depends(get_db), user=Depends(require_user)):
    out = []
    for source in db.query(Source).filter(Source.user_id == user.id).order_by(Source.created_at.desc()):
        count = db.query(Document).filter(Document.source_id == source.id).count()
        out.append(SourceOut(id=source.id, kind=source.kind, title=source.title, url=source.url, content_hash=source.content_hash, chunks=count))
    return out

@router.get("/{source_id}")
def get_source(source_id: str, db: Session = Depends(get_db), user=Depends(require_user)):
    source = db.query(Source).filter(Source.id == source_id, Source.user_id == user.id).first()
    if source is None: raise HTTPException(404, "Source not found")
    chunks = db.query(Document).filter(Document.source_id == source.id).order_by(Document.chunk_index).all()
    return {"id": source.id, "kind": source.kind, "title": source.title, "url": source.url, "content_hash": source.content_hash, "meta": source.meta, "chunks": [{"id": c.id, "chunk_index": c.chunk_index, "text": c.text} for c in chunks]}
