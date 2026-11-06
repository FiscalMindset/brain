# Scalability
Current: single-process monolith, SQLite. Next: Postgres (`DATABASE_URL`), stateless API workers behind a load balancer, embeddings/pgvector search, background workers for ingestion (see `TODO.md` SB-DB-001, SB-SCALE-001). No premature microservices.
