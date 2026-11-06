"""Search with citations and the orchestrated research workflow."""


def _seed(client, headers):
    client.post(
        "/api/sources",
        headers=headers,
        json={"content": "Kubernetes autoscaling scales pods based on CPU metrics."},
    )
    client.post(
        "/api/sources",
        headers=headers,
        json={"content": "Unrelated note about gardening and soil preparation."},
    )


def test_search_returns_citations(client, auth_headers):
    _seed(client, auth_headers)
    resp = client.get("/api/search", headers=auth_headers, params={"q": "autoscaling"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] >= 1
    assert body["citations"]
    assert body["citations"][0]["document_id"]
    assert all("autoscaling" in r["text"].lower() for r in body["results"])


def test_search_no_match(client, auth_headers):
    _seed(client, auth_headers)
    body = client.get("/api/search", headers=auth_headers, params={"q": "zzz-no-hit"}).json()
    assert body["count"] == 0


def test_research_workflow(client, auth_headers):
    _seed(client, auth_headers)
    resp = client.post("/api/research", headers=auth_headers, json={"query": "autoscaling"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["session_id"]
    assert body["findings"] and body["citations"]
    assert body["human_approval"] is True
    assert "next_actions" in body
    # full delegation chain: research -> knowledge -> reviewer -> verifier -> learning -> memory -> qa -> project-manager
    steps = [s["agent"] for s in body["steps"]]
    assert steps == ["research", "knowledge", "reviewer", "verifier", "learning", "memory", "qa", "project-manager"]
