# Endpoint Reference

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/api/health` | no | liveness |
| POST | `/api/auth/register` | no | create user → token (201) |
| POST | `/api/auth/login` | no | login → token |
| POST | `/api/sources` | yes | ingest JSON source (dedupe by hash) |
| POST | `/api/sources/upload` | yes | multipart upload PDF/MD/TXT (max 5, 2MB each) |
| POST | `/api/sources/url` | yes | fetch http(s) URL → source (dedupe, SSRF-safe, 500KB cap) |
| GET | `/api/sources` | yes | list sources |
| GET | `/api/sources/{id}` | yes | source + chunks |
| GET | `/api/search?q=&kind=&limit=` | yes | cited search |
| POST | `/api/research` | yes | 8-step orchestration → structured report |
| GET | `/api/agents` | no | agent catalogue |
| POST | `/api/agents/run` | yes | run orchestrator chain |
| GET | `/api/integrations` | no | adapter catalogue + contract |
| POST/GET | `/api/projects`, `/api/projects/{id}` | yes | project CRUD |
| POST | `/api/projects/{id}/tasks` | yes | add task |
| POST | `/api/projects/{id}/issue-draft` | yes | GitHub issue text (never pushed) |
| GET/POST/PATCH/DELETE | `/api/memory` | yes | memory CRUD (user-scoped) |
| PATCH/DELETE | `/api/memory/{id}` | yes | edit/delete memory |
| GET | `/api/graph` | yes | entities + relationships |
| POST | `/api/graph/entities`, `/api/graph/relationships` | yes | create |
| GET | `/api/dashboard` | yes | counts + recent activity |
| GET | `/api/audit?limit=&offset=` | yes | audit events |
