# SecondBrain — Master Backlog

**Date:** 2026-11-04 · **Branch:** `main` (no commits yet) · **Hackathon:** Switch Nov 4–7, 2026 — Best Personal or Creative Workflow

**Status legend:** `[ ]` todo · `[~]` in progress · `[x]` done (code present, uncommitted) · `[!]` blocked · `[-]` won't do (this phase)
**Phase status:** Phase 0–2 `[x]` completed · Phase 3 `[~]` in progress · Phase 4 `[~]` started (backend core drafted) · Phase 5+ `[ ]` later.

Conventions: **Priority** P0 = must-have for demo, P1 = should-have, P2 = nice-to-have. Each task lists *Deps*, *Acceptance*, *Tests*, *Files*. Backend tasks reflect the actual files in `apps/api/app/` as of 2026-11-04.

---

## Architecture

- [x] **SB-ARCH-001** (P0) Repo scaffold: modular-monolith layout, `main` branch, git identity FiscalMindset.
  - *Deps:* — *Accept:* `apps/{api,web}`, `packages/shared`, `docker`, `infra`, `docs`, `.github` exist. *Tests:* none. *Files:* directory structure.
- [x] **SB-ARCH-002** (P0) Living docs baseline: README, CURRENT, TODO, CHANGELOG, DECISIONS, KNOWN_ISSUES, DEVELOPMENT_LOG, RELEASE_NOTES, docs index.
  - *Deps:* SB-ARCH-001 *Accept:* all files present, dated 2026-11-04, cross-links resolve. *Tests:* link check (manual). *Files:* root `*.md`, `docs/README.md`.
- [ ] **SB-ARCH-003** (P0) Module boundaries + import rule (api→services→models; agents/switch only via services).
  - *Deps:* SB-FOUND-003 *Accept:* import graph matches README/CURRENT diagram; `ruff`/lint note in `docs/architecture/`. *Tests:* CI lint. *Files:* `apps/api/app/**`, `docs/architecture/`.
- [ ] **SB-ARCH-004** (P1) Shared contracts in `packages/shared` from FastAPI OpenAPI (generated TS types).
  - *Deps:* SB-FOUND-003 *Accept:* web uses generated types; no hand-duplicated DTOs. *Tests:* contract diff in CI. *Files:* `packages/shared/`, `apps/web/src/`.

## Product

- [x] **SB-PROD-001** (P0) Product definition: capture → cite → plan with provenance; Switch = collaboration layer (ADR-005).
  - *Deps:* SB-ARCH-002 *Accept:* README + DECISIONS state it. *Tests:* none. *Files:* `README.md`, `DECISIONS.md`.
- [x] **SB-PROD-002** (P0) Capture backend: `POST /api/sources` with content-hash dedupe, chunking, audit event.
  - *Deps:* — *Accept:* identical content returns existing source (`deduplicated: true`); chunks persisted. *Tests:* pytest (SB-TEST-001). *Files:* `apps/api/app/api/sources.py`, `apps/api/app/services/ingestion.py`, `apps/api/app/models/models.py`.
- [x] **SB-PROD-003** (P0) Recall backend: `GET /api/search` keyword retrieval + citations.
  - *Deps:* SB-PROD-002 *Accept:* results carry `document_id`/`source_id`/`chunk_index` citations. *Tests:* pytest citation-coverage (SB-TEST-001). *Files:* `apps/api/app/api/search.py`, `apps/api/app/services/retrieval.py`.
- [x] **SB-PROD-004** (P1) Research/plan backend: `POST /api/research` orchestrated pipeline + `POST /api/projects/{id}/issue-draft` text draft.
  - *Deps:* SB-PROD-003 *Accept:* persisted `ResearchSession.report`; draft includes `human_approval: true`, no push. *Tests:* pytest human-approval assertion. *Files:* `apps/api/app/api/research.py`, `apps/api/app/api/projects.py`, `apps/api/app/services/agents.py`.
- [ ] **SB-PROD-005** (P0) Capture/Recall UI wired to real API (blocked on SB-FE-001 source).
  - *Deps:* SB-FE-001 *Accept:* create → inbox with provenance; search → cited results. *Tests:* Vitest + Playwright smoke. *Files:* `apps/web/src/pages/`, `apps/web/src/components/`.

## Frontend

- [x] **SB-FE-001a** (P0) Frontend configs: Vite (dev+preview `/api` proxy → :8000), TS strict, react-router-dom, `index.html` with theme bootstrap.
  - *Deps:* — *Accept:* configs present. *Tests:* typecheck (blocked until src). *Files:* `apps/web/{package.json,vite.config.ts,tsconfig.json,index.html}`.
- [ ] **SB-FE-001** (P0) `src/main.tsx` + app shell: router, typed API client (JWT header), auth context/store.
  - *Deps:* SB-FE-001a *Accept:* `npm run build` passes; app talks to `GET /health`. *Tests:* Vitest smoke. *Files:* `apps/web/src/main.tsx`, `apps/web/src/store/`, `apps/web/src/hooks/`.
- [ ] **SB-FE-002** (P1) Hooks for sources/search/projects/agents with loading/empty/error states.
  - *Deps:* SB-FE-001 *Accept:* no prop-drilled fetches. *Tests:* Vitest hook tests. *Files:* `apps/web/src/hooks/`, `apps/web/src/pages/`.
- [ ] **SB-FE-003** (P1) Accessibility: landmarks, focus management, keyboard search, axe clean.
  - *Deps:* SB-FE-001 *Accept:* axe zero critical violations. *Tests:* axe in Vitest/Playwright. *Files:* `apps/web/src/components/`.

## Backend

- [x] **SB-BE-001** (P0) Core config + DB + security: pydantic-settings, SQLAlchemy session/`init_db`, PBKDF2 + HMAC tokens + `require_user`.
  - *Deps:* — *Accept:* files present; defaults boot locally (once main.py lands). *Tests:* pytest token round-trip (SB-TEST-001). *Files:* `apps/api/app/core/{config,database,security}.py`.
- [x] **SB-BE-002** (P0) Auth router: `POST /api/auth/register` + `POST /api/auth/login` → bearer token; audit events.
  - *Deps:* SB-BE-001 *Accept:* register 201, duplicate 409, login 401 on bad creds. *Tests:* pytest auth flow. *Files:* `apps/api/app/api/auth.py`.
- [x] **SB-BE-003** (P1) Agents module: 9-agent catalogue + in-process orchestration (research→knowledge→reviewer→project-manager) writing `AgentExecution`; `human_approval` in every output.
  - *Deps:* SB-PROD-003 *Accept:* `/api/agents` lists 9; `/api/agents/run` rejects unknown agent with 400. *Tests:* pytest agent contract. *Files:* `apps/api/app/services/agents.py`, `apps/api/app/api/agents.py` (pipeline/research/knowledge/reviewer/project-manager runners present; learning/memory/verifier/qa runners NOT yet implemented).
- [ ] **SB-BE-004** (P0) `app/main.py`: app factory, `init_db()`, mount all routers under `API_PREFIX`, `GET /health`, CORS/request-id.
  - *Deps:* SB-FOUND-002 *Accept:* `uvicorn app.main:app` boots; `/docs` serves OpenAPI; health 200. *Tests:* pytest TestClient health/config. *Files:* `apps/api/app/main.py` (MISSING), `apps/api/app/api/__init__.py`.
- [ ] **SB-BE-005** (P1) Agents runners for learning, memory, verifier, qa.
  - *Deps:* SB-BE-003 *Accept:* each runner exists and is callable from orchestration or `/agents/run`. *Tests:* pytest per-runner. *Files:* `apps/api/app/services/agents.py`.

## AI / Agents

- [x] **SB-AI-001** (P1) Retrieval service: ILIKE hybrid (text + kind/source_id/since filters); `citation_for()`.
  - *Deps:* SB-PROD-002 *Accept:* `/search` ranked newest-first with citations. *Tests:* pytest ranking test. *Files:* `apps/api/app/services/retrieval.py`.
- [ ] **SB-AI-002** (P1) Summarizer/judge layer: cited gap/contradiction detection; every claim maps to a citation.
  - *Deps:* SB-AI-001, SB-BE-003 *Accept:* `/research` report has citations + gaps + `human_approval`. *Tests:* pytest citation-coverage. *Files:* `apps/api/app/services/agents.py`, `apps/api/app/api/research.py`.

## Integrations

- [ ] **SB-INT-001** (P0) `app/integrations/adapters.py`: `ADAPTERS` + `describe_contract()` so `GET /api/integrations` works.
  - *Deps:* — *Accept:* router imports without error; adapters carry name/status/requires_oauth. *Tests:* pytest integrations endpoint. *Files:* `apps/api/app/integrations/adapters.py` (MISSING — current router broken).
- [ ] **SB-INT-002** (P1) Webhook/URL ingestion adapter (fetch + normalize → source pipeline).
  - *Deps:* SB-INT-001 *Accept:* URL ingest creates deduped source. *Tests:* mocked-httpx pytest. *Files:* `apps/api/app/integrations/`, `apps/api/app/services/ingestion.py`.
- [ ] **SB-INT-003** (P1) Google OAuth login (real keys; blocked B-02).
  - *Deps:* [!] blocked on keys *Accept:* login flow succeeds with real keys. *Tests:* integration test (skip without keys). *Files:* `apps/api/app/integrations/`, `apps/web/src/`.

## Switch (Collaboration Layer)

- [ ] **SB-SWITCH-001** (P0) Switch bridge client: `apps/api/app/switch/client.py` per Settings (`SWITCH_BRIDGE_URL/API_KEY/AGENT_ID`), env-gated, local stub default.
  - *Deps:* [!] B-01 for live call, not for client+stub *Accept:* with no key, stub serves; with key, real client used. *Tests:* stub + contract tests. *Files:* `apps/api/app/switch/` (currently `__init__.py` docstring only).
- [ ] **SB-SWITCH-002** (P0) UI: per-source threads, @mentions, activity feed, shared collections.
  - *Deps:* SB-SWITCH-001 *Accept:* discuss a source without leaving provenance context. *Tests:* Vitest + Playwright smoke. *Files:* `apps/web/src/components/`, `apps/web/src/pages/`.

## Database

- [x] **SB-DB-001a** (P0) ORM models (11 tables, UUID string PKs, UTC timestamps, JSON meta): User, Source, Document, KnowledgeEntity, KnowledgeRelationship, Project, ProjectTask, ResearchSession, AgentExecution, AuditEvent, UserMemory.
  - *Deps:* SB-BE-001 *Accept:* `Base.metadata.create_all` works on SQLite. *Tests:* pytest model CRUD (SB-TEST-001). *Files:* `apps/api/app/models/models.py`.
- [ ] **SB-DB-001** (P0) Alembic migrations + Postgres parity (replace/augment `create_all`).
  - *Deps:* SB-DB-001a *Accept:* `alembic upgrade head` green on SQLite and Postgres. *Tests:* migration smoke in CI. *Files:* `apps/api/alembic/` (MISSING).
- [ ] **SB-DB-002** (P1) Seed script: demo corpus (sources/chunks/memory) via the same pipeline.
  - *Deps:* SB-DB-001a *Accept:* `python -m app.seed` loads demo data idempotently. *Tests:* seed idempotency test. *Files:* `apps/api/app/seed.py` (MISSING).

## Security

- [x] **SB-SEC-001a** (P0) Password hashing (PBKDF2-HMAC-SHA256, 120k rounds) + HMAC bearer tokens + `require_user` guard on authenticated routers.
  - *Deps:* SB-BE-001 *Accept:* hash/verify round-trip; tokens expire; tampered token → 401. *Tests:* pytest security. *Files:* `apps/api/app/core/security.py`.
- [ ] **SB-SEC-001** (P1) Rate limit on auth endpoints, security headers, CORS allowlist.
  - *Deps:* SB-BE-004 *Accept:* headers present; brute-force rate-limited; secret scanning clean. *Tests:* CI (bandit/gitleaks). *Files:* `apps/api/app/core/`, `.github/workflows/`.
- [ ] **SB-SEC-002** (P1) `AuditEvent` coverage review + retention policy doc (writer exists, never raises).
  - *Deps:* SB-SEC-001a *Accept:* every mutating router audits. *Tests:* pytest audit assertion. *Files:* `apps/api/app/services/audit.py` (core DONE).

## Testing

- [ ] **SB-TEST-001** (P0) pytest suite: `apps/api/tests/` — security round-trip, auth flow, sources dedupe, search citations, agents contract, integrations catalogue (once adapters exist).
  - *Deps:* SB-FOUND-002/003 *Accept:* `pytest` passes locally; CI runs it. *Tests:* this is the test task. *Files:* `apps/api/tests/` (EMPTY — pytest in requirements.txt).
- [ ] **SB-TEST-002** (P1) Vitest + typecheck gate; Playwright E2E (capture → search → research → issue-draft; Switch thread).
  - *Deps:* SB-FE-001 *Accept:* `npm run typecheck && npm run build` + E2E green. *Tests:* Vitest/Playwright. *Files:* `apps/web/` (no test scripts in package.json yet).
- [ ] **SB-TEST-003** (P1) Coverage gate (pytest-cov, e.g. ≥70% on services) wired in CI.
  - *Deps:* SB-TEST-001 *Accept:* CI fails below threshold. *Tests:* CI. *Files:* `.github/workflows/`, `apps/api/`.

## DevOps

- [ ] **SB-DEVOPS-001** (P0) Dockerfiles (api, web) + `docker/compose.yml` (api+web+Postgres).
  - *Deps:* SB-BE-004 *Accept:* `docker compose up --build` works. *Tests:* CI build. *Files:* `docker/`, `apps/api/Dockerfile`, `apps/web/Dockerfile` (all EMPTY/MISSING).
- [ ] **SB-DEVOPS-002** (P0) CI workflow: lint + pytest + typecheck/build on push/PR to `main`.
  - *Deps:* SB-TEST-001 *Accept:* GitHub Actions green. *Tests:* CI itself. *Files:* `.github/workflows/` (EMPTY).
- [ ] **SB-DEVOPS-003** (P2) Infra manifests (`infra/`) + deploy notes for demo host.
  - *Deps:* SB-DEVOPS-001 *Accept:* documented deploy path. *Tests:* n/a. *Files:* `infra/`, `docs/devops/`.

## Docs

- [x] **SB-DOC-001a** (P0) Root doc suite (this baseline) + `docs/README.md` index.
  - *Deps:* SB-ARCH-001 *Accept:* all root docs present, links resolve to existing files. *Tests:* link check. *Files:* root `*.md`, `docs/README.md`.
- [ ] **SB-DOC-001** (P1) Fill subsystem docs as code lands (api, database, architecture, hackathon…).
  - *Deps:* SB-DOC-001a *Accept:* `docs/README.md` status flips to real content; no 404 links. *Tests:* link check. *Files:* `docs/` (13 dirs still empty).
- [ ] **SB-DOC-002** (P1) Verify README quickstart verbatim on a clean machine after SB-BE-004.
  - *Deps:* SB-BE-004 *Accept:* quickstart steps executed succeed. *Tests:* manual checklist. *Files:* `README.md`, `apps/api/`.

## Performance

- [ ] **SB-PERF-001** (P2) Search latency budget: <300ms p95 on 10k documents; ILIKE index review (trigram vs FTS).
  - *Deps:* SB-AI-001 *Accept:* bench script reports p95. *Tests:* bench in `apps/api/tests/`. *Files:* `apps/api/app/services/retrieval.py`.

## Accessibility

- [ ] **SB-A11Y-001** (P1) WCAG 2.2 AA pass on core flows (capture, search, detail).
  - *Deps:* SB-FE-003 *Accept:* axe + keyboard walkthrough clean. *Tests:* axe/Playwright. *Files:* `apps/web/src/`.

## Hackathon

- [ ] **SB-HACK-001** (P0) Submission package: seed corpus (SB-DB-002), 3-minute demo script, README polish, video outline.
  - *Deps:* SB-PROD-002/003/004, SB-DB-002 *Accept:* script runs start→finish on demo data. *Tests:* dry-run checklist. *Files:* `docs/hackathon/`, `README.md`.
- [ ] **SB-HACK-002** (P0) Switch Console manual step completed + credentials stored in env (B-01).
  - *Deps:* [!] blocked on human console step *Accept:* real Switch API responds. *Tests:* live ping. *Files:* `apps/api/app/switch/`, `.env` (never committed).
- [ ] **SB-HACK-003** (P1) Judging criteria mapping: Best Personal/Creative Workflow story, screenshots/GIFs.
  - *Deps:* SB-HACK-001 *Accept:* submission page complete before Nov 7. *Tests:* n/a. *Files:* `docs/hackathon/`.

## Production

- [ ] **SB-PROD-006** (P2) Production hardening: Postgres default, structured logs, backups note, `infra/` deploy.
  - *Deps:* SB-DEVOPS-003 *Accept:* compose + migrate + health green on deploy host. *Tests:* deploy checklist. *Files:* `infra/`, `docs/operations/`.

## Foundation (Phase 3 — in progress)

- [~] **SB-FOUND-001** (P0) Initial commit: monorepo scaffold + backend core + frontend configs + doc suite on `main`.
  - *Deps:* SB-ARCH-001 *Accept:* first commit lands; verified: code present uncommitted on `main`, zero commits so far. *Tests:* CI placeholder. *Files:* everything in §4 of CURRENT.
- [~] **SB-FOUND-002** (P0) `app/integrations/adapters.py` + `app/main.py` (boot the service).
  - *Deps:* SB-FOUND-001 *Accept:* `uvicorn app.main:app` boots with all 7 routers mounted. *Tests:* smoke (SB-TEST-001). *Files:* `apps/api/app/main.py` (MISSING), `apps/api/app/integrations/adapters.py` (MISSING).
- [ ] **SB-FOUND-003** (P1) `apps/api/.env.example`, root `.gitignore`, lint/format (ruff, eslint), GitHub Actions skeleton.
  - *Deps:* SB-FOUND-001 *Accept:* fresh clone follows README quickstart. *Tests:* CI. *Files:* `.github/workflows/` (EMPTY), `.env.example` (MISSING).

## Core (Phase 4 — started / backend drafted)

- [x] **SB-CORE-001** (P0) Capture pipeline (fingerprint → dedupe → chunk → AuditEvent) — `POST/GET /api/sources`.
  - *Deps:* SB-CORE-002 *Accept:* verified in code. *Tests:* pytest pending (SB-TEST-001). *Files:* `apps/api/app/services/ingestion.py`, `apps/api/app/api/sources.py`.
- [x] **SB-CORE-002** (P0) Retrieval + citations — `GET /api/search`; agents/research/projects routers wired in code (unmounted until main.py).
  - *Deps:* SB-CORE-001 *Accept:* verified in code. *Tests:* pytest pending (SB-TEST-001). *Files:* `apps/api/app/services/retrieval.py`, `apps/api/app/api/search.py`.
- [~] **SB-CORE-003** (P0) Wire-up: `main.py` + `init_db()` + boot smoke — **the blocker for everything.**
  - *Deps:* SB-FOUND-002 *Accept:* service boots; `/health` 200; `/docs` serves all 7 routers. *Tests:* pytest TestClient. *Files:* `apps/api/app/main.py`.

---

## Phase Map

| Phase | Scope | Status |
|---|---|---|
| 0 — Scoping | product definition, hackathon track, ADR baseline | [x] |
| 1 — Architecture | stack choices, modular monolith, provenance/memory split | [x] |
| 2 — Scaffolding | repo layout, domains, doc suite | [x] |
| 3 — Foundation | configs, core, DB, CI, Docker | [~] backend drafted; main.py/tests/CI pending |
| 4 — Core | capture, linking, search, frontend, Switch layer | [~] backend drafted; entrypoint/frontend/Switch pending |
| 5 — Polish | AI runners, OAuth, E2E, a11y, perf, submission | [ ] |
| 6+ — Production | deploy, hardening, backups | [ ] |
