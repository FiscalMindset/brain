# Local Setup

```bash
cp .env.example .env
cd apps/api && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/uvicorn app.main:app --reload
cd apps/web && npm install && npm run dev
```
API at :8000, web at :5173 (proxied `/api`). Or `docker compose up --build`.
