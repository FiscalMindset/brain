# Data Architecture
11 tables (see `../database/DATA_MODEL.md`), UUID string PKs, UTC timestamps, JSON `meta` columns for extensibility. Provenance chain: `Source.content_hash` → `Document` chunks → citations → `ResearchSession.report` → `AuditEvent` trail. User scoping (`user_id` on every user-owned row) is enforced in every service query.
