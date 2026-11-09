"""Hardening tests: retrieval, security, agents, CRUD, upload, lifespan."""
import io
from datetime import UTC, datetime, timedelta

import httpx

from app.api.auth import _hits, check_rate_limit
from app.core.security import create_token, decode_token
from app.services.ingestion import detect_language, extract_summary, extract_topics
from app.services.retrieval import escape_like, search_documents


def _seed(client, headers, content):
    return client.post("/api/sources", headers=headers, json={"content": content}).json()

# 1 word-tokenized search: "rag systems" matches docs with either word
def test_word_tokenized_any_hit(client, auth_headers):
    _seed(client, auth_headers, "RAG retrieval systems are powerful.")
    _seed(client, auth_headers, "Completely unrelated cooking recipe.")
    body = client.get("/api/search", headers=auth_headers, params={"q": "rag systems"}).json()
    assert body["count"] == 1
    assert "rag" in body["results"][0]["text"].lower()

# 2 ranking: doc with both terms ranks first
def test_search_ranking_by_score(client, auth_headers):
    _seed(client, auth_headers, "rag systems together rag systems")
    _seed(client, auth_headers, "only rag here")
    body = client.get("/api/search", headers=auth_headers, params={"q": "rag systems"}).json()
    assert body["results"][0]["text"].lower().startswith("rag systems together")

# 3 LIKE escaping: % does not match everything
def test_like_escaping(client, auth_headers):
    _seed(client, auth_headers, "literal 100% coverage here")
    _seed(client, auth_headers, "other text without percent")
    assert escape_like("100%") == "100\\%"
    body = client.get("/api/search", headers=auth_headers, params={"q": "100%"}).json()
    assert body["count"] == 1

# 4 empty query returns latest docs
def test_empty_query_returns_latest(client, auth_headers):
    _seed(client, auth_headers, "first doc")
    _seed(client, auth_headers, "second doc")
    body = client.get("/api/search", headers=auth_headers, params={"q": ""}).json()
    assert body["count"] >= 2

# 5 since handling naive vs aware
def test_search_since_naive_aware(client, auth_headers):
    _seed(client, auth_headers, "recent doc")
    from tests.conftest import TestingSession
    db = TestingSession()
    try:
        from app.models.models import User
        uid = db.query(User).filter(User.email == "tester@example.com").first().id
        docs_naive = search_documents(db, uid, "recent", since=datetime.now() - timedelta(days=1))
        assert len(docs_naive) >= 1
    finally: db.close()

# helper to look up uid via DB
def _uid_via_db():
    from app.models.models import User
    from tests.conftest import TestingSession
    db = TestingSession()
    try: return db.query(User).filter(User.email == "tester@example.com").first().id
    finally: db.close()

# fix test 5 properly
def test_search_since_works(client, auth_headers):
    _seed(client, auth_headers, "recent doc xyz")
    from tests.conftest import TestingSession
    db = TestingSession()
    try:
        from app.models.models import User
        uid = db.query(User).filter(User.email == "tester@example.com").first().id
        assert search_documents(db, uid, "recent", since=datetime.now(UTC) - timedelta(days=1))
        assert not search_documents(db, uid, "recent", since=datetime.now(UTC) + timedelta(days=1))
    finally: db.close()

# 6 metadata extraction
def test_metadata_extraction():
    text = "The system is fast. It scales well. Kubernetes stuff here."
    assert detect_language(text) == "en"
    assert extract_summary(text)
    assert extract_topics(text)

# 7 dedupe same hash different title
def test_dedupe_different_title(client, auth_headers):
    a = client.post("/api/sources", headers=auth_headers, json={"content": "same content here", "title": "First"}).json()
    b = client.post("/api/sources", headers=auth_headers, json={"content": "same content here", "title": "Second"}).json()
    assert a["id"] == b["id"] and b["deduplicated"] is True
    assert len(client.get("/api/sources", headers=auth_headers).json()) == 1

# 8 login dummy path: unknown email 401 same shape
def test_login_unknown_email_401(client):
    r = client.post("/api/auth/login", json={"email": "ghost@example.com", "password": "password123"})
    assert r.status_code == 401 and r.json()["detail"] == "Invalid credentials"

# 9 email validation 422
def test_email_validation_422(client):
    assert client.post("/api/auth/register", json={"email": "not-an-email", "password": "password123"}).status_code == 422

# 10 rate limiter function
def test_rate_limiter():
    _hits.clear()
    for _ in range(60): assert check_rate_limit("1.2.3.4")
    assert not check_rate_limit("1.2.3.4")
    assert check_rate_limit("5.6.7.8")

# 11 token expiry + revoked (deleted user)
def test_expired_and_deleted_user(client, auth_headers):
    assert decode_token(create_token("x", expires_in=-5)) is None
    from app.models.models import User
    from tests.conftest import TestingSession
    db = TestingSession()
    try:
        u = db.query(User).filter(User.email == "tester@example.com").first()
        db.delete(u); db.commit()
    finally: db.close()
    assert client.get("/api/sources", headers=auth_headers).status_code == 401

# 12 memory CRUD + isolation
def test_memory_crud_isolation(client, auth_headers):
    m = client.post("/api/memory", headers=auth_headers, json={"key": "pref", "value": "dark"}).json()
    assert client.patch(f"/api/memory/{m['id']}", headers=auth_headers, json={"value": "light"}).json()["value"] == "light"
    # user B
    r2 = client.post("/api/auth/register", json={"email": "b2@example.com", "password": "password123"}).json()
    h2 = {"Authorization": f"Bearer {r2['access_token']}"}
    assert client.patch(f"/api/memory/{m['id']}", headers=h2, json={"value": "hacked"}).status_code == 404
    assert client.delete(f"/api/memory/{m['id']}", headers=auth_headers).status_code == 200

# 13 graph CRUD + co-occurrence
def test_graph_and_cooccurrence(client, auth_headers):
    _seed(client, auth_headers, "alphabeta gamma systems are great.")
    out = client.post("/api/research", headers=auth_headers, json={"query": "alphabeta gamma systems"}).json()
    assert any(s["agent"] == "knowledge" for s in out["steps"])
    g = client.get("/api/graph", headers=auth_headers).json()
    assert len(g["entities"]) >= 1
    # dedupe entities
    e1 = client.post("/api/graph/entities", headers=auth_headers, json={"name": "unique-thing"}).json()
    e2 = client.post("/api/graph/entities", headers=auth_headers, json={"name": "unique-thing"}).json()
    assert e1["id"] == e2["id"]

# 14 dashboard counts
def test_dashboard(client, auth_headers):
    _seed(client, auth_headers, "dashboard seed content")
    client.post("/api/memory", headers=auth_headers, json={"key": "k", "value": "v"})
    d = client.get("/api/dashboard", headers=auth_headers).json()
    assert d["counts"]["sources"] >= 1 and d["counts"]["memories"] >= 1 and "recent_activity" in d

# 15 audit pagination
def test_audit_pagination(client, auth_headers):
    _seed(client, auth_headers, "audit seed")
    a = client.get("/api/audit", headers=auth_headers, params={"limit": 1, "offset": 0}).json()
    assert a["total"] >= 1 and len(a["events"]) == 1

# 16 verifier + learning agents via orchestration
def test_verifier_learning_agents(client, auth_headers):
    _seed(client, auth_headers, "verifiable learning content alpha")
    out = client.post("/api/research", headers=auth_headers, json={"query": "verifiable"}).json()
    names = [s["agent"] for s in out["steps"]]
    assert "verifier" in names and "learning" in names and "qa" in names
    mems = client.get("/api/memory", headers=auth_headers).json()
    assert len(mems) >= 1

# 17 knowledge dedupe on re-run
def test_knowledge_dedupe(client, auth_headers):
    _seed(client, auth_headers, "dedupeentity content here.")
    client.post("/api/research", headers=auth_headers, json={"query": "dedupeentity"})
    n1 = len(client.get("/api/graph", headers=auth_headers).json()["entities"])
    client.post("/api/research", headers=auth_headers, json={"query": "dedupeentity"})
    n2 = len(client.get("/api/graph", headers=auth_headers).json()["entities"])
    assert n2 == n1

# 18 upload txt/md
def test_upload_txt_md(client, auth_headers):
    r = client.post("/api/sources/upload", headers=auth_headers, files=[("files", ("a.txt", io.BytesIO(b"hello txt world"), "text/plain")), ("files", ("b.md", io.BytesIO(b"# Title\ncontent md"), "text/markdown"))])
    assert r.status_code == 200, r.text
    assert r.json()["uploaded"] == 2
    assert client.post("/api/sources/upload", headers=auth_headers, files=[("files", ("c.exe", b"x", "application/octet-stream"))]).status_code == 400

# 19 switch client retry + helper + is_configured
def test_switch_client_helpers():
    from app.switch.client import SwitchClient
    calls = {"n": 0}
    def handler(req):
        calls["n"] += 1
        if calls["n"] == 1: return httpx.Response(500, json={})
        return httpx.Response(200, json={"ok": True})
    c = SwitchClient(bridge_url="http://x", api_key="k", agent_id="a1", transport=httpx.MockTransport(handler))
    assert c.is_configured
    assert c.list_rooms()["ok"] is True and calls["n"] == 2
    c2 = SwitchClient(bridge_url="http://x", api_key="k", agent_id="a1", transport=httpx.MockTransport(lambda r: httpx.Response(200, json={"ok": True})))
    assert c2.post_research_to_room("room1", {"query": "q", "findings": [{"text": "f1"}], "qa": {"questions": ["q1"]}})["ok"] is True

# 20 lifespan boot / routes
def test_lifespan_routes(client):
    assert client.get("/api/health").json()["status"] == "ok"
    assert client.get("/api/dashboard").status_code == 401  # auth required
