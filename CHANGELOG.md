# Changelog

All notable changes to SecondBrain are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and semantic
versioning.

## [Unreleased]

## [0.2.0] — 2026-11-09

Hardening + closing out the backlog: Alembic migrations (alembic upgrade head creates all 11 tables), SSRF-safe URL ingestion (POST /api/sources/url), security headers middleware, ruff lint wired in CI, Vitest 20 tests + axe a11y, shared OpenAPI types at packages/shared, search perf bench (10k docs: p95 30-33ms vs 300ms budget).

## [0.1.0] — 2026-11-06

Initial production-grade build: FastAPI backend (auth, sources+upload, tokenized search, 8-step research orchestration, 9-agent catalogue, projects/tasks/issue-draft, memory, graph, dashboard, audit), React+Vite frontend (13 routes, dark/light themes), Switch room template + 4 agent instruction files + retrying protocol client, Docker Compose + CI, 116 doc files. Tests: 46 passed, 93% line coverage. Web build clean.


### Added
- Living docs baseline (2026-11-04): `README.md`, `CURRENT.md`, `TODO.md`,
  `DECISIONS.md`, `KNOWN_ISSUES.md`, `DEVELOPMENT_LOG.md`,
  `RELEASE_NOTES.md`, `docs/README.md`.
- Backend core (uncommitted, `main` with zero commits): `app/core/`
  (config, database, security), `app/models/models.py` (11 tables),
  `app/services/` (ingestion, retrieval, audit, agents), 7 routers in
  `app/api/` (auth, sources, search, research, agents, projects,
  integrations).
- Frontend configs (uncommitted): `apps/web/` Vite proxy, TS strict config,
  `index.html`, `package.json` (React 18, react-router-dom).

### Changed
- Hackathon positioning recorded: Switch hackathon Nov 4–7, 2026, track
  Best Personal or Creative Workflow; Switch = collaboration layer, not a
  chat wrapper.

### Known gaps (see CURRENT + KNOWN_ISSUES)
- `app/main.py` and `app/integrations/adapters.py` missing — service does
  not boot; `GET /api/integrations` import is broken.
- `apps/api/tests/`, `apps/web/src/` (incl. `main.tsx`), `packages/shared/`,
  `docker/`, `infra/`, `.github/workflows/` empty or missing.

## [0.0.1] — 2026-11-04

Initial repository state: scaffold + backend core drafted, no commits, no
tests, no bootable entrypoint. Full detail in
[RELEASE_NOTES.md](./RELEASE_NOTES.md).
