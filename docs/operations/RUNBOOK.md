# Runbook
Boot: `cd apps/api && .venv/bin/uvicorn app.main:app --reload`. Tests: `cd apps/api && .venv/bin/python -m pytest -q --cov=app`. Web: `cd apps/web && npm run dev`. Rotate secret: change `SECRET_KEY` in `.env`, restart (all tokens invalidated).
