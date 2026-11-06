# Release Notes

## 0.0.1 — 2026-11-04 (Scaffold + backend core drafted, uncommitted)

**What this release is:** uncommitted working-tree snapshot at the
Phase 2 → Phase 3/4 handoff: repo scaffold + full backend core drafted +
frontend configs staged + living docs. ⚠️ **No commits yet** — the first
commit (SB-FOUND-001) is the immediate next step.

### Highlights
- Modular-monolith layout: FastAPI backend (`apps/api/app/{core,api,
  services,models}` implemented; `agents`/`switch`/`integrations`
  placeholders), React+Vite configs (`apps/web/`), shared contracts
  (`packages/shared/` still empty).
- Architecture locked by ADRs ([DECISIONS.md](./DECISIONS.md)): modular
  monolith; SQLite (dev) / Postgres (prod) via `DATABASE_URL`; FastAPI +
  pydantic-settings; React + Vite + TS; Switch as collaboration layer;
  provenance/memory separation.
- Working backend semantics (in code): register/login → bearer token;
  ingest source → dedupe by content hash → chunk → search with citations;
  research → findings/gaps/contradictions with `human_approval: true`;
  findings → project + review tasks + text-only issue draft; every
  mutation audited.
- Hackathon positioning: Switch hackathon **Nov 4–7, 2026**, track **Best
  Personal or Creative Workflow**.

### Included
- [README.md](./README.md) — product overview, hackathon Switch statement,
  quickstart, architecture.
- [CURRENT.md](./CURRENT.md) — handoff: implemented vs partial vs not,
  blockers, exact next tasks.
- [TODO.md](./TODO.md) — master backlog (`SB-*` IDs), Phase 0–2 `[x]`,
  Phase 3/4 `[~]`, Phase 5+ `[ ]`.
- [CHANGELOG.md](./CHANGELOG.md), [DECISIONS.md](./DECISIONS.md),
  [KNOWN_ISSUES.md](./KNOWN_ISSUES.md),
  [DEVELOPMENT_LOG.md](./DEVELOPMENT_LOG.md), `docs/README.md` index.

### Not included yet (expected — see CURRENT §6)
- `app/main.py` (no bootable service, no `GET /health`) and
  `app/integrations/adapters.py` (integrations router broken) — SB-BE-004 /
  SB-INT-001 (`SB-CORE-003` critical path).
- Frontend source (`src/main.tsx`, pages) — SB-FE-001.
- Tests, CI, Docker/compose, Alembic, seed script — SB-TEST-001,
  SB-DEVOPS-001/002, SB-DB-001/002.
- Switch bridge client + real OAuth (blocked: KI-03/KI-04, B-01/B-02).
- Agents runners for learning/memory/verifier/qa (KI-08, SB-BE-005).

### Upgrade / Migration
None — greenfield. Branch `main`, identity `FiscalMindset`, zero commits.

### Next release (0.1.0)
Bootable backend + smoke-tested core: `main.py` + `init_db` + `/health`,
routers mounted, first pytest green, web shell built. See
[TODO.md](./TODO.md).
