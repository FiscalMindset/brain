# Performance
Ingestion is chunked (800 chars), search scores in Python over candidates (fine at small scale). Targets: search p95 <200ms locally; measure before scaling (TODO SB-PERF-001).
