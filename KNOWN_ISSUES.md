# Known Issues

**Date:** 2026-11-09 · **Branch:** `main` (6 commits pushed) ·
**Hackathon:** Switch Nov 4–7, 2026

**Resolved 2026-11-09:** KI-01, KI-02, KI-03, KI-05, KI-06, KI-07, KI-08, KI-09 (see evidence below). **Still open:** KI-04 (OAuth keys), + genuinely-open gaps in § Open (2026-11-09).

## KI-01 — ~~`app/main.py` missing (service does not boot)~~ — RESOLVED
- **Severity:** Blocking · **Status:** Resolved 2026-11-09 (SB-BE-004/SB-CORE-003)
- The 11 routers are mounted under `/api` in `apps/api/app/main.py`, with `GET /api/health`, lifespan `init_db()`, CORS, request-id logging, and security-headers middleware.
- **Evidence:** `tests/test_health.py` passes as part of **55 passed / 93% coverage**. `uvicorn app.main:app` boots. Uncertainty: none.

## KI-02 — ~~`app/api/integrations.py` imports a missing module~~ — RESOLVED
- **Severity:** Blocking once main.py mounts routers · **Status:** Resolved 2026-11-09 (SB-INT-001)
- `app/integrations/adapters.py` now ships `ADAPTERS` + `describe_contract()`; the catalogue router imports cleanly.
- **Evidence:** integrations + URL-ingest tests pass (`test_url_ingest.py`). Adapters honestly report `not_configured` until OAuth keys exist (see KI-04).

## KI-03 — ~~`app/switch/` has no bridge client~~ — RESOLVED (client+stub; live call needs human)
- **Severity:** Blocking for SB-SWITCH-002/SB-HACK-002 · **Status:** Resolved 2026-11-09 (SB-SWITCH-001)
- `app/switch/client.py` provides the env-gated bridge client (typed errors, timeouts, retries, documented ops `list_rooms`/`post_message`/`read_context`) with a local stub default when no bridge URL is set.
- **Evidence:** Switch client + room template landed (`switch/secondbrain-room.template.yaml`); tests cover the stub/contract. Real room messaging still needs the Switch Console manual step (B-01) — see Open § below.

## KI-04 — Real OAuth keys missing
- **Severity:** Blocking for SB-INT-003 · **Status:** Open (terminal — needs human)
- Secrets must be provisioned by a human.
- **Workaround:** dev runs on `SECRET_KEY` only; skip OAuth tests without keys; adapters report `not_configured` instead of failing.

## KI-05 — ~~Frontend has configs but no source~~ — RESOLVED
- **Severity:** Blocking for `npm run build` · **Status:** Resolved 2026-11-09 (SB-FE-001)
- `apps/web/src/{main.tsx,App.tsx,api/client.ts,components/common.tsx,hooks/ui.tsx,store/theme}` exist; 13 routes wired to the typed shared-contract client.
- **Evidence:** `npm run build` clean (38 modules, 198.58 kB JS); `npm run typecheck` clean; **Vitest 20 passed** incl. axe checks.

## KI-06 — ~~No tests, no CI~~ — RESOLVED
- **Severity:** High until SB-TEST-001/SB-DEVOPS-002 land · **Status:** Resolved 2026-11-09
- `apps/api/tests/` has 13 test files (55 tests); `.github/workflows/{ci,docker}.yml` run pytest (`--cov-fail-under=30`) + web build + Docker builds on push/PR; web has Vitest scripts.
- **Evidence:** **Backend 55 passed, 93% coverage** (`977 stmts, 68 miss`); **Vitest 20 passed**; bench harness `scripts/bench_search.py` landed.

## KI-07 — ~~Nothing committed; parallel-session overwrite risk~~ — RESOLVED (6 commits pushed)
- **Severity:** High · **Status:** Resolved 2026-11-09 (SB-FOUND-001)
- `main` carries 6 commits (up to `392452f`, verified via `git log --oneline`: 392452f, 5cce9a1, e06d234, bff1f07, d183efd, aea89af).
- **Evidence:** git log verified 2026-11-09. Residual risk: the 2026-11-09 batch (Alembic, URL adapter, Vitest, `packages/shared`) is still uncommitted in the working tree — commit it promptly and stage per directory.

## KI-08 — ~~Agents advertised without runners~~ — DONE 2026-11-09
- **Severity:** Medium · **Status:** Resolved 2026-11-09 (SB-BE-005)
- All 9 agents advertise a runner: research, knowledge, reviewer, verifier, learning, memory, qa, project-manager, orchestrator; `run_orchestration()` chains all 8 steps.
- **Evidence:** per-agent pytest contract (`test_projects_agents.py`); orchestration output carries `human_approval: true`.

## KI-09 — ~~Subsystem docs are empty~~ — DONE 2026-11-09
- **Severity:** Low · **Status:** Resolved 2026-11-09 (SB-DOC-001)
- `docs/*` (13 dirs) are filled: product, architecture (+ ADRs), design, security, database, testing (incl. [docs/testing/COVERAGE_REPORT.md](./docs/testing/COVERAGE_REPORT.md)), devops, operations, hackathon, integrations, ai, api, engineering.
- **Evidence:** `docs/README.md` index + subsystem docs cross-linked from CURRENT §7.

## Open (2026-11-09) — genuinely remaining

| ID | Issue | Severity / Status | Workaround |
|---|---|---|---|
| KI-04 | Real OAuth keys missing (Google login). | Blocking SB-INT-003 | Dev on `SECRET_KEY`; adapters report `not_configured` |
| Playwright E2E deferred | Capture → search → research → issue-draft; Switch thread flows not E2E-tested. | Medium (Vitest + pytest cover today) | Manual demo dry-run via seed corpus + `docs/hackathon/DEMO_SCRIPT.md` |
| Semantic / vector search planned | Tokenized ANY-word ILIKE scoring only. | Medium | Keyword search is fast enough (bench p95 32.5 ms on 10k docs); embeddings are a later phase |
| Switch live-room needs human | Real room messaging requires the Switch Console manual step + credentials (sleeping agent ping). | Blocking SB-SWITCH-002/SB-HACK-002 | Env-gated stub + room template; demo runs without Switch |
| Postgres deploy untested | Compose `db` profile + Alembic exist; never validated on a live Postgres host. | Medium | Local SQLite green (`tests/test_alembic.py`); validate `alembic upgrade head` + compose on the demo host before prod (SB-DEVOPS-003) |

## Resolved 2026-11-06

- Two pre-existing test failures fixed (see DEVELOPMENT_LOG).
- Frontend was configs-only; now fully built.
