"""Projects/tasks, issue drafts, agent catalogue and orchestrator runs."""


def test_project_crud_and_tasks(client, auth_headers):
    project = client.post(
        "/api/projects", headers=auth_headers, json={"title": "Launch", "description": "ship it"}
    ).json()
    assert project["tasks"] == []

    task = client.post(
        f"/api/projects/{project['id']}/tasks",
        headers=auth_headers,
        json={"title": "Write docs", "assignee": "vic"},
    ).json()
    assert task["title"] == "Write docs"

    fetched = client.get(f"/api/projects/{project['id']}", headers=auth_headers).json()
    assert len(fetched["tasks"]) == 1

    draft = client.post(f"/api/projects/{project['id']}/issue-draft", headers=auth_headers).json()
    assert "Write docs" in draft["body"]
    assert draft["human_approval"] is True


def test_agent_catalogue_lists_all(client, auth_headers):
    body = client.get("/api/agents", headers=auth_headers).json()
    names = [a["name"] for a in body["agents"]]
    for expected in ("orchestrator", "research", "knowledge", "reviewer", "qa", "memory", "verifier"):
        assert expected in names


def test_agent_run_executes_orchestration(client, auth_headers):
    client.post(
        "/api/sources",
        headers=auth_headers,
        json={"content": "Memory consolidation helps long-term retention of facts."},
    )
    resp = client.post("/api/agents/run", headers=auth_headers, json={"agent": "orchestrator", "query": "memory"})
    assert resp.status_code == 200
    assert resp.json()["project_id"]


def test_agent_run_unknown_agent(client, auth_headers):
    resp = client.post("/api/agents/run", headers=auth_headers, json={"agent": "nope", "query": "x"})
    assert resp.status_code == 400


def test_integrations_catalogue(client, auth_headers):
    body = client.get("/api/integrations", headers=auth_headers).json()
    names = [i["name"] for i in body["integrations"]]
    for expected in ("chatgpt", "youtube", "github", "drive", "notion", "pdf", "markdown", "bookmarks"):
        assert expected in names
    assert body["contract"]["ingest"]
