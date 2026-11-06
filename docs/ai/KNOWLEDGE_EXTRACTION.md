# Knowledge Extraction
Entity extraction: content words >5 chars, deduped per user (`_get_or_create_entity`). Relationships: co-occurrence within the same finding → `KnowledgeRelationship(relation='co-occurs')`, deduped. Extraction is heuristic and explicitly labelled as derived, never user fact.
