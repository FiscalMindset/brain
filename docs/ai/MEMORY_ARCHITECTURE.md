# Memory Architecture
`UserMemory` rows are user-scoped, keyed by `(user_id, key)`, with `meta.source_document_id` provenance for learned entries. Three origins are distinguished in `meta.origin`: user-provided, imported, AI-derived. Learning agent writes AI-derived only; never overwrites user facts.
