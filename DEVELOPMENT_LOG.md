# Development Log

## 2026-11-04 — Day 1: Scaffold + backend drafted + living docs (Phase 0–2 complete, Phase 3 [~], Phase 4 [~])

- Repo `secondbrain` on branch `main` (git identity `FiscalMindset`,
  `algsoch@gmail.com`); ⚠️ **zero commits** — everything below is
  uncommitted working-tree state from parallel sessions.
- Scaffold verified: `apps/{api,web}`, `packages/shared`, `docker`,
  `infra`, `docs/{ai,api,architecture/ADR,database,design,devops,
  engineering,hackathon,integrations,operations,product,security,testing}`,
  `.github/workflows` (empty).
- Backend drafted in working tree (verified by reading the files):
  - `app/core/{config,database,security}.py` — pydantic-settings (SQLite
    default, `API_PREFIX=/api`, Switch bridge env), `get_db` +
    `init_db()` (`create_all`), PBKDF2 hashing + HMAC tokens +
    `require_user` dependency.
  - `app/models/models.py` — 11 tables with UUID string PKs: `User`,
    `Source`, `Document`, `KnowledgeEntity`, `KnowledgeRelationship`,
    `Project`, `ProjectTask`, `ResearchSession`, `AgentExecution`,
    `AuditEvent`, `UserMemory`.
  - `app/services/` — `ingestion.py` (normalize/fingerprint/chunk),
    `retrieval.py` (ILIKE + filters + `citation_for`), `audit.py`
    (never-raises audit writer), `agents.py` (9-agent catalogue;
    runnable pipeline research→knowledge→reviewer→project-manager,
    `run_orchestration` persists `AgentExecution`).
  - `app/api/` — 7 routers: auth (register/login), sources (dedupe +
    chunks), search (citations), research, agents (list/run),
    projects (+ tasks + text-only issue-draft), integrations (catalogue —
    imports missing `app.integrations.adapters`: **broken**).
  - `app/{agents,integrations,switch}/` — docstring placeholders only.
- Frontend configs staged: `apps/web/{index.html,vite.config.ts,
  tsconfig.json,package.json}` — Vite proxy `/api → :8000`, React 18.3,
  react-router-dom, TS strict. `src/` (incl. `main.tsx`) empty.
- Wrote/rewrote the living-doc suite: `README.md`, `CURRENT.md`,
  `TODO.md`, `CHANGELOG.md`, `DECISIONS.md` (ADR-001…006), `KNOWN_ISSUES.md`,
  `DEVELOPMENT_LOG.md`, `RELEASE_NOTES.md`, `docs/README.md`.
- Decision lock-in: modular monolith (ADR-001), SQLite/Postgres via
  `DATABASE_URL` (ADR-002), FastAPI + pydantic-settings (ADR-003),
  React+Vite+TS (ADR-004), Switch = collaboration layer not chat wrapper
  (ADR-005), provenance/memory separation (ADR-006).
- Hackathon target: Switch, Nov 4–7, 2026, **Best Personal or Creative
  Workflow**.
- Current phase: **Phase 3 (foundation) in progress + Phase 4 (core)
  started** — backend ~70% written but unwired. Blockers: B-01 Switch
  Console manual step, B-02 real OAuth keys; critical-path gap: missing
  `app/main.py` (SB-CORE-003).

**Next (in order):** SB-FOUND-001 (commit) → SB-FOUND-002 (adapters +
main.py boot) → SB-TEST-001 (first pytest smoke) → SB-FE-001 (web
source). See [CURRENT.md](./CURRENT.md) §6 / [TODO.md](./TODO.md).

## 2026-11-06 — Full build completion
- Fixed 2 failing tests (research step-sequence: pipeline now 8 steps; `since` naive/aware test now looks up real user id).
- Built complete React frontend: `src/main.tsx`, `src/App.tsx` (13 routes incl. login, dashboard, library, search, research, agents, projects, integrations, graph, memory, activity, settings), typed API client, theme/toast contexts, design tokens.
- Fixed client/backend mismatches: upload accepts multiple `files`, memory update uses PATCH, audit pagination uses `limit`/`offset`.
- Wrote 116 doc files across `docs/` (product, architecture, design, engineering, integrations, ai, security, database, api, testing, devops, operations, hackathon).
- Added `docker-compose.yml` (validated with `docker compose config`), Dockerfiles, CI workflows, `.gitignore`, `.env.example`, `switch/README.md`.
- Verification: 46 tests passed / 93% coverage; `npm run build` clean; YAML all valid.

## 2026-11-09 — Backlog close-out
- Alembic migrations added (alembic.ini + versions/0001_initial.py covering all 11 tables; upgrade head verified on temp DB).
- URL ingestion adapter (apps/api/app/integrations/url_adapter.py) + POST /api/sources/url with SSRF guards (scheme/host/IP validation, 500KB cap, timeouts) — 5 new tests.
- Security headers middleware (nosniff/DENY/Referrer-Policy/CSP) — 1 new test.
- Ruff config (pyproject.toml, line-length 100) wired in CI; all lint errors fixed.
- Vitest 20 tests (API client + component render + axe zero-critical) and tsc typecheck gate added to CI; shared OpenAPI types exported to packages/shared.
- Perf bench (10k docs): p95 30-33ms — PASS vs 300ms budget; documented.
- Living docs refreshed: CURRENT/TODO/KNOWN_ISSUES now reflect verified reality; only OAuth/Switch-console-dependent items remain open.
- Final numbers: backend 55 passed / 93% line coverage; frontend 20 passed, typecheck + build clean; docker compose config valid.
