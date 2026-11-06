# Test Strategy
Unit + integration via pytest (FastAPI TestClient, in-memory SQLite). Every service and router has meaningful tests; no meaningless coverage padding. Commands: `cd apps/api && .venv/bin/python -m pytest -q --cov=app --cov-report=term-missing`.
