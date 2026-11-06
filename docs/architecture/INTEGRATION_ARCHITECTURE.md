# Integration Architecture
Adapters live in `apps/api/app/integrations/adapters.py` behind a common contract (`validate` / `ingest` / `IngestResult`). Until per-provider OAuth is configured, `ingest` returns `ok: False` with a structured reason — never fake success. See `../integrations/INTEGRATION_CONTRACT.md`.
