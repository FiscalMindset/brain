"""Seed demo corpus: 3 sources + research run. Run with API up:
   curl -X POST :8000/api/auth/register ... or use this script against TestClient.
Usage: python -m scripts.seed_demo  (uses in-process TestClient, no server needed)
"""
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, SessionLocal
from app.models import models  # noqa
Base.metadata.create_all(bind=engine)
c = TestClient(app)
tok = c.post("/api/auth/register", json={"email": "demo@example.com", "password": "password123", "full_name": "Demo"}).json()["access_token"]
h = {"Authorization": f"Bearer {tok}"}
for content in [
    "RAG systems retrieve relevant chunks from a vector index and cite them in generated answers.",
    "Spaced repetition schedules reviews at expanding intervals to improve long-term retention.",
    "Multi-agent architectures delegate to specialist agents with structured handoffs and human approval gates.",
]:
    print(c.post("/api/sources", headers=h, json={"content": content}).json())
print(c.post("/api/research", headers=h, json={"query": "RAG systems"}).json()["steps"][0]["agent"])
print("seed ok")
