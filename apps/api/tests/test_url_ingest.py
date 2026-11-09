"""URL ingestion endpoint tests (no network: UrlAdapter.fetch monkeypatched)."""

import httpx

from app.integrations.url_adapter import UrlAdapter, UrlFetchError, UrlOversizeError

HTML = (
    "<html><head><title>Example Title</title>"
    "<style>.x{color:red}</style>"
    "<script>alert('x')</script></head>"
    "<body><p>First paragraph with enough text to be meaningful content here.</p>"
    "<p>Second paragraph adds more detail for chunking and fingerprinting.</p>"
    "</body></html>"
)


def _patch_fetch(monkeypatch, result):
    def fake_fetch(self, url):
        return result

    monkeypatch.setattr(UrlAdapter, "fetch", fake_fetch)


def test_url_ingest_success_and_dedupe(client, auth_headers, monkeypatch):
    _patch_fetch(
        monkeypatch,
        ("First paragraph with enough text to be meaningful content here. Second paragraph adds more detail.", "Example Title", {"url": "https://example.com/page"}),
    )
    r = client.post("/api/sources/url", headers=auth_headers, json={"url": "https://example.com/page"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["kind"] == "url"
    assert body["title"] == "Example Title"
    assert body["deduplicated"] is False

    r2 = client.post("/api/sources/url", headers=auth_headers, json={"url": "https://example.com/page"})
    assert r2.status_code == 200, r2.text
    body2 = r2.json()
    assert body2["id"] == body["id"]
    assert body2["deduplicated"] is True

    listing = client.get("/api/sources", headers=auth_headers).json()
    assert len(listing) == 1


def test_url_ingest_invalid_scheme_rejected(client, auth_headers):
    r = client.post("/api/sources/url", headers=auth_headers, json={"url": "file:///etc/passwd"})
    assert r.status_code == 400


def test_url_ingest_localhost_rejected(client, auth_headers):
    r = client.post("/api/sources/url", headers=auth_headers, json={"url": "http://localhost:8000/x"})
    assert r.status_code == 400


def test_url_ingest_private_ip_rejected(client, auth_headers):
    r = client.post("/api/sources/url", headers=auth_headers, json={"url": "http://127.0.0.1/secret"})
    assert r.status_code == 400


def test_url_ingest_fetch_error_maps_to_502(client, auth_headers, monkeypatch):
    def fake_fetch(self, url):
        raise UrlFetchError(f"fetch failed for {url}: connection refused")

    monkeypatch.setattr(UrlAdapter, "fetch", fake_fetch)
    r = client.post("/api/sources/url", headers=auth_headers, json={"url": "https://example.com/page"})
    assert r.status_code == 502


def test_url_ingest_oversize_maps_to_400(client, auth_headers, monkeypatch):
    def fake_fetch(self, url):
        raise UrlOversizeError("response too large (600000 bytes > 512000)")

    monkeypatch.setattr(UrlAdapter, "fetch", fake_fetch)
    r = client.post("/api/sources/url", headers=auth_headers, json={"url": "https://example.com/big"})
    assert r.status_code == 400


def test_url_adapter_parses_html_via_mock_transport(monkeypatch):
    def handler(request):
        return httpx.Response(200, text=HTML, headers={"content-type": "text/html"})

    import httpx as _httpx


    class FakeClient(_httpx.Client):
        def get(self, url, **kwargs):
            return handler(_httpx.Request("GET", url))

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    monkeypatch.setattr("app.integrations.url_adapter.httpx.Client", FakeClient)
    adapter = UrlAdapter()
    text, title, meta = adapter.fetch("https://example.com/page")
    assert title == "Example Title"
    assert "First paragraph" in text
    assert "alert" not in text
    assert meta["status_code"] == 200
