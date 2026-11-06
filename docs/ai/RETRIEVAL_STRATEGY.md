# Retrieval Strategy
Tokenized ANY-word: split query on whitespace, any-term ILIKE match with LIKE escaping (`%_\`), score = matched-term count, rank by score desc then recency desc. Filters: `kind` (join to Source), `source_id`, `since` (naive datetimes normalized to UTC). Empty query returns latest docs. Semantic/hybrid vector search is planned (TODO.md).
