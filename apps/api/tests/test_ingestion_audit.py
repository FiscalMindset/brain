"""Ingestion primitives, audit writes, and adapter/Switch contracts."""

import pytest

from app.integrations.adapters import ADAPTERS, describe_contract
from app.models.models import AuditEvent
from app.services.ingestion import chunk_text, fingerprint, normalize


def test_normalize_and_fingerprint():
    assert normalize("  a\n\n b\t c ") == "a b c"
    assert fingerprint("a  b") == fingerprint("a b")
    assert fingerprint("a b") != fingerprint("a c")


def test_chunk_text_respects_size():
    text = " ".join(f"Sentence number {i}." for i in range(50))
    chunks = chunk_text(text, chunk_size=100)
    assert len(chunks) > 1
    assert all(len(c) <= 100 for c in chunks)
    assert chunk_text("") == []


def test_audit_event_written_on_ingest(client, auth_headers):
    client.post("/api/sources", headers=auth_headers, json={"content": "auditable content"})
    from tests.conftest import TestingSession

    db = TestingSession()
    try:
        events = db.query(AuditEvent).filter(AuditEvent.action == "source.create").all()
        assert len(events) == 1
    finally:
        db.close()


def test_adapter_stub_degrades_gracefully():
    adapter = next(a for a in ADAPTERS if a.name == "markdown")
    with pytest.raises(ValueError):
        adapter.validate({})
    result = adapter.ingest({"content": "# hello", "external_id": "x-1"})
    assert result["ok"] is False
    assert "OAuth" in result["error"]
    assert describe_contract()["idempotency"]


def test_switch_client_ops_and_guard():
    import httpx

    from app.switch.client import DOC_OPS, SwitchClient

    assert set(DOC_OPS) == {"list_rooms", "post_message", "read_context"}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ok": True, "path": request.url.path})

    client = SwitchClient(
        bridge_url="http://switch.local", api_key="k", agent_id="a-1",
        transport=httpx.MockTransport(handler),
    )
    assert client.list_rooms()["ok"] is True
    assert client.connection_ws_url().endswith("/agents/a-1/connection/ws")
    with pytest.raises(ValueError):
        client.run_op("delete_everything")
