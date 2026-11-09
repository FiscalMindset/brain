# Coverage Report (2026-11-09)

```text
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
app/__init__.py                       0      0   100%
app/agents/__init__.py                0      0   100%
app/api/__init__.py                   0      0   100%
app/api/agents.py                    21      0   100%
app/api/audit.py                     12      0   100%
app/api/auth.py                      66      1    98%   40
app/api/dashboard.py                 11      0   100%
app/api/graph.py                     34      6    82%   30-35
app/api/integrations.py               6      0   100%
app/api/memory.py                    37      0   100%
app/api/projects.py                  58      3    95%   31, 63, 92
app/api/research.py                  21      0   100%
app/api/search.py                    10      0   100%
app/api/sources.py                  113     14    88%   65, 78-79, 81, 99-107, 110
app/core/__init__.py                  0      0   100%
app/core/config.py                   13      0   100%
app/core/database.py                 16      6    62%   22-26, 31-33
app/core/security.py                 58      3    95%   37-39
app/integrations/__init__.py          0      0   100%
app/integrations/adapters.py         61     15    75%   36, 53-54, 61-62, 69-70, 77-78, 85-86, 93-94, 109-110
app/integrations/url_adapter.py      52      6    88%   43-44, 47, 51, 70, 73
app/main.py                          42      3    93%   15-16, 40
app/models/__init__.py                0      0   100%
app/models/models.py                107      0   100%
app/services/__init__.py              0      0   100%
app/services/agents.py              101      0   100%
app/services/audit.py                 9      0   100%
app/services/ingestion.py            43      1    98%   22
app/services/retrieval.py            35      3    91%   23, 27-28
app/switch/__init__.py                0      0   100%
app/switch/client.py                 51      7    86%   33, 35-40
---------------------------------------------------------------
TOTAL                               977     68    93%
55 passed, 2 warnings in 4.48s
```

Command: `cd apps/api && .venv/bin/python -m pytest -q --cov=app --cov-report=term-missing` (13 test files, incl. `test_alembic.py`, `test_security_headers.py`, `test_url_ingest.py`, `test_hardening.py`).
Lowest modules: `app/core/database.py` 62% (engine config), `app/integrations/adapters.py` 75% (OAuth-gated), `app/api/graph.py` 82%. Frontend: `npm run test` = **20 passed** (Vitest, incl. axe checks) — see `docs/testing/TEST_RESULTS.md`.
