# Event Architecture
No broker at this scale. In-process delegation via `run_orchestration()`; audit events are the durable event log (`audit_events` table). Background jobs and webhooks are future work (see `../engineering/BACKGROUND_JOBS.md`).
