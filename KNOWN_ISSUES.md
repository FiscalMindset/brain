# Known Issues

**Date:** 2026-11-04 · **Branch:** `main` (no commits yet) ·
**Hackathon:** Switch Nov 4–7, 2026

## KI-01 — `app/main.py` missing (service does not boot)
- **Severity:** Blocking · **Status:** Open (SB-BE-004/SB-CORE-003)
- The 7 routers exist but nothing mounts them; there is no `GET /health`,
  no `init_db()` call site, no `uvicorn` target.
- **Workaround:** none — fix is SB-CORE-003 (write `main.py`, request-id,
  CORS, mount routers under `API_PREFIX`).

## KI-02 — `app/api/integrations.py` imports a missing module
- **Severity:** Blocking once main.py mounts routers · **Status:** Open (SB-INT-001)
- Imports `app.integrations.adapters` (`ADAPTERS`, `describe_contract`) —
  the file does not exist.
- **Workaround:** write `adapters.py` before mounting, or leave the router
  out of `main.py` until it exists.

## KI-03 — `app/switch/` has no bridge client
- **Severity:** Blocking for SB-SWITCH-002/SB-HACK-002 · **Status:** Open
- `switch/__init__.py` is a docstring; `Settings` has bridge URL/key/agent
  ID but no client code. Real Switch also needs the Switch Console manual
  step (B-01).
- **Workaround:** env-gated stub client (SB-SWITCH-001). Core
  capture/retrieval/contracts unaffected.

## KI-04 — Real OAuth keys missing
- **Severity:** Blocking for SB-INT-003 · **Status:** Open
- Secrets must be provisioned by a human.
- **Workaround:** dev runs on `SECRET_KEY` only; skip OAuth tests without
  keys.

## KI-05 — Frontend has configs but no source
- **Severity:** Blocking for `npm run build` · **Status:** Open (SB-FE-001)
- `apps/web/src/{components,hooks,pages,store}` are empty and
  `src/main.tsx` is absent — `index.html` expects `/src/main.tsx`.
- **Workaround:** none until SB-FE-001.

## KI-06 — No tests, no CI
- **Severity:** High until SB-TEST-001/SB-DEVOPS-002 land · **Status:** Open
- `pytest`/`pytest-cov` are in `requirements.txt` but `apps/api/tests/`
  is empty; `.github/workflows/` is empty; web has no test scripts.
- **Workaround:** first CI job is a blocker for merging Phase 3/4 work.

## KI-07 — Nothing committed; parallel-session overwrite risk
- **Severity:** High · **Status:** Open (SB-FOUND-001)
- `main` has zero commits; all backend code, frontend configs and these
  docs are uncommitted working-tree files from parallel sessions.
- **Workaround:** commit SB-FOUND-001 immediately; stage selectively
  (`git add` per directory, redo §2 of CURRENT) instead of bulk-adding.

## KI-08 — Agents advertised without runners
- **Severity:** Medium · **Status:** Open (SB-BE-005)
- `/api/agents` lists 9 agents but only research/knowledge/reviewer/
  project-manager have runners; learning/memory/verifier/qa have no
  functions yet.
- **Workaround:** today `/agents/run` always runs the orchestrator chain;
  per-agent endpoints need the missing runners first.

## KI-09 — Subsystem docs are empty
- **Severity:** Low · **Status:** Open (SB-DOC-001)
- `docs/*` (13 dirs) are empty; only root docs + `docs/README.md` exist.
  Subsystem links will 404 until SB-DOC-001 lands.
- **Workaround:** treat `docs/README.md` status column as truth.

## Resolved 2026-11-06
- Two pre-existing test failures fixed (see DEVELOPMENT_LOG).
- Frontend was configs-only; now fully built.

## Still open
- KI-01 Switch Console manual setup requires a human (install app, import template, link messaging account).
- KI-02 Real OAuth keys needed for live ChatGPT/YouTube/GitHub/Drive/Notion ingest; adapters honestly report not_configured until then.
- KI-03 Semantic/vector search not implemented — tokenized ANY-word scoring only (planned).
