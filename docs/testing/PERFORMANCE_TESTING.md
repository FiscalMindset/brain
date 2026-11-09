# Performance Testing

Search latency budget: p95 < 300 ms on 10k documents (SB-PERF-001). Automated via `python scripts/bench_search.py` (seeds 10k docs across 5 users into a temp SQLite DB, 200 samples, 5 queries).

## Bench results (2026-11-09)

```text
seeding 10000 docs across 5 users into /var/folders/.../tmpda7clrvp.db ...
seeded 10000 docs
samples: 200 (queries=['spaced repetition', 'knowledge graph', 'second brain research', 'project task planning', 'retrieval rag indexing'], runs/query=40)
p50: 14.0ms  p95: 32.5ms  max: 47.5ms
budget p95 < 300ms -> PASS (p95=32.5ms)
```

Previously noted (never measured on this hardware): p50 ~12.6 ms / p95 ~30.0 ms. The 2026-11-09 re-run measured **p50 14.0 ms, p95 32.5 ms** — close enough that the earlier estimate stands, and both are an order of magnitude under budget. ILIKE trigram-vs-FTS review remains the planned follow-up.
