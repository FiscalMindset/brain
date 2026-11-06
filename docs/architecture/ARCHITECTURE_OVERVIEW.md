# Architecture Overview
Modular monolith: FastAPI backend (`apps/api/app`), React frontend (`apps/web`), Switch collaboration layer (`switch/`), Docker/CI (`docker/`, `.github/`, `docker-compose.yml`). SQLite for local dev, Postgres via `DATABASE_URL`. Full detail in `SYSTEM_ARCHITECTURE.md`.
