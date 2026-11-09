"""SB-PERF-001: seed 10k documents across users and measure search latency p95.

Budget: p95 < 300ms for single-user keyword search over 10k docs.

Usage: cd apps/api && .venv/bin/python scripts/bench_search.py
Uses a temp-file SQLite DB (no writes to the dev database).
"""

from __future__ import annotations

import os
import statistics
import sys
import tempfile
import time
import uuid
from pathlib import Path

# Temp DB must be configured before app.core.database creates its engine.
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.core.database import Base  # noqa: E402
from app.models.models import Document, User, _uuid  # noqa: E402
from app.services.retrieval import search_documents  # noqa: E402

NUM_USERS = 5
DOCS_PER_USER = 2000
TOTAL_DOCS = NUM_USERS * DOCS_PER_USER  # 10k
QUERIES = [
    "spaced repetition",
    "knowledge graph",
    "second brain research",
    "project task planning",
    "retrieval rag indexing",
]
RUNS_PER_QUERY = 40
BUDGET_MS = 300

TOPICS = [
    "spaced repetition flashcards",
    "knowledge graph entities",
    "second brain research notes",
    "project task planning checklist",
    "retrieval rag indexing pipeline",
    "unrelated cat care guide",
]


def percent(samples: list[float], pct: float) -> float:
    if not samples:
        return 0.0
    s = sorted(samples)
    k = max(0, min(len(s) - 1, int(round((pct / 100) * (len(s) - 1)))))
    return s[k]


def main() -> int:
    print(f"seeding {TOTAL_DOCS} docs across {NUM_USERS} users into {_tmp.name} ...")
    engine = create_engine(f"sqlite:///{_tmp.name}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    users = []
    now = 0
    for ui in range(NUM_USERS):
        u = User(id=_uuid(), email=f"user{ui}@bench.local", hashed_password="x", full_name=f"Bench {ui}")
        db.add(u)
        users.append(u)
    db.commit()
    rows = []
    for ui, u in enumerate(users):
        for i in range(DOCS_PER_USER):
            rows.append(
                Document(
                    id=_uuid(),
                    user_id=u.id,
                    source_id=None,
                    chunk_index=i,
                    text=f"{TOPICS[i % len(TOPICS)]} doc {i} user {ui} filler paragraph to simulate realistic chunk length " * 8,
                    meta={"bench": True, "i": i},
                )
            )
            if len(rows) >= 500:
                db.bulk_save_objects(rows)
                rows = []
    if rows:
        db.bulk_save_objects(rows)
    db.commit()
    print(f"seeded {TOTAL_DOCS} docs")

    latencies: list[float] = []
    for qi, q in enumerate(QUERIES):
        user = users[qi % len(users)]
        for _ in range(RUNS_PER_QUERY):
            t0 = time.perf_counter()
            hits = search_documents(db, user.id, q, limit=20)
            latencies.append((time.perf_counter() - t0) * 1000)
            assert len(hits) <= 20
    p50 = statistics.median(latencies)
    p95 = percent(latencies, 95)
    print(f"samples: {len(latencies)} (queries={QUERIES}, runs/query={RUNS_PER_QUERY})")
    print(f"p50: {p50:.1f}ms  p95: {p95:.1f}ms  max: {max(latencies):.1f}ms")
    status = "PASS" if p95 < BUDGET_MS else "OVER BUDGET"
    print(f"budget p95 < {BUDGET_MS}ms -> {status} (p95={p95:.1f}ms)")
    return 0 if p95 < BUDGET_MS else 1


if __name__ == "__main__":
    raise SystemExit(main())
