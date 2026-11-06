# API Standards
Versioned under `/api`. JSON in/out, Pydantic in, explicit out shapes. Pagination: `limit`/`offset` (audit). Idempotency: sources dedupe by content hash; entities dedupe by (user, name). Auth: `Authorization: Bearer`.
