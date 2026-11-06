"""Source ingestion: creation, chunking, dedupe, list and fetch."""

CONTENT = "SecondBrain stores research notes. " * 40


def _create(client, headers, content=CONTENT, **extra):
    return client.post("/api/sources", headers=headers, json={"content": content, **extra})


def test_create_source_chunks_content(client, auth_headers):
    resp = _create(client, auth_headers, title="Notes")
    assert resp.status_code == 200
    body = resp.json()
    assert body["chunks"] >= 1
    assert body["deduplicated"] is False

    fetched = client.get(f"/api/sources/{body['id']}", headers=auth_headers)
    assert fetched.status_code == 200
    assert len(fetched.json()["chunks"]) == body["chunks"]


def test_duplicate_content_deduplicated(client, auth_headers):
    first = _create(client, auth_headers).json()
    second = _create(client, auth_headers).json()
    assert second["id"] == first["id"]
    assert second["deduplicated"] is True


def test_list_sources_scoped_to_user(client, auth_headers):
    _create(client, auth_headers)
    listing = client.get("/api/sources", headers=auth_headers).json()
    assert len(listing) == 1


def test_get_missing_source_404(client, auth_headers):
    assert client.get("/api/sources/does-not-exist", headers=auth_headers).status_code == 404
