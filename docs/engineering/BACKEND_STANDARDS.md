# Backend Standards
Routers thin, services own logic, models own schema. Every user query filters `user_id`. Audit via `record_audit`. Errors via `HTTPException` with user-readable messages; global handler returns `{"detail": ...}`.
