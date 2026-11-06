# Backend Architecture
FastAPI with lifespan startup, request logging middleware, global exception handler, env-based CORS. Routers validate with Pydantic and delegate to services; services own DB logic; models are the only schema definition (`create_all` today; Alembic planned). Security: PBKDF2 + HMAC tokens, rate limiting on auth, user scoping on every query.
