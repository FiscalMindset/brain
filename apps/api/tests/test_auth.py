"""Auth: register, duplicate email, login and token enforcement."""


def test_register_and_login(client):
    resp = client.post(
        "/api/auth/register",
        json={"email": "a@example.com", "password": "password123"},
    )
    assert resp.status_code == 201
    assert resp.json()["token_type"] == "bearer"

    login = client.post(
        "/api/auth/login", json={"email": "a@example.com", "password": "password123"}
    )
    assert login.status_code == 200
    assert login.json()["access_token"]


def test_duplicate_email_rejected(client):
    payload = {"email": "dup@example.com", "password": "password123"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    assert client.post("/api/auth/register", json=payload).status_code == 409


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={"email": "b@example.com", "password": "password123"})
    resp = client.post("/api/auth/login", json={"email": "b@example.com", "password": "nope-nope"})
    assert resp.status_code == 401


def test_protected_route_requires_token(client):
    assert client.get("/api/sources").status_code == 401
    assert client.get("/api/sources", headers={"Authorization": "Bearer garbage"}).status_code == 401
