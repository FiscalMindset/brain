# Test Results (2026-11-09)

Backend: **55 passed, 0 failed** (2 benign warnings: starlette httpx deprecation; alembic `path_separator` deprecation). Coverage: **93%** (`977 stmts, 68 miss`) — see `docs/testing/COVERAGE_REPORT.md`. Command: `cd apps/api && .venv/bin/python -m pytest -q --cov=app --cov-report=term-missing`.
Web: **Vitest 20 passed** (2 files: `src/api/client.test.ts`, `src/components/common.test.tsx` incl. 4 axe zero-critical/serious checks). `npm run typecheck` clean; `npm run build` clean (38 modules, 198.58 kB JS).
Search bench (10k docs / 5 users, 200 samples): **p50 14.0 ms, p95 32.5 ms, max 47.5 ms — PASS** (budget p95 < 300 ms) — see `docs/testing/PERFORMANCE_TESTING.md`.
