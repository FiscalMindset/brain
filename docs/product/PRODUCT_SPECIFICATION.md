# SecondBrain — Product Specification

## In scope (v0.1 built)
- Auth: register/login with HMAC bearer tokens, PBKDF2 password hashing.
- Ingestion: JSON sources + multipart upload (PDF/MD/TXT, max 5 files / 2MB each), content-hash dedupe, sentence-aware chunking, metadata extraction (language/summary/topics).
- Retrieval: tokenized ANY-word scoring, LIKE-escaped, metadata filters (kind/source/since), citations.
- Research: orchestrated 8-step pipeline (research→knowledge→reviewer→verifier→learning→memory→qa→project-manager), structured report, `human_approval` gate.
- Graph: entities/relationships CRUD with dedupe + co-occurrence extraction.
- Memory: user-scoped CRUD with isolation.
- Projects: CRUD, tasks, issue-draft (text only, never pushed).
- Dashboard/activity: counts + audit timeline.
- Switch: `app/switch/client.py` (retry, timeouts, typed errors) + room template `switch/secondbrain-room.template.yaml`.

## Out of scope
Live OAuth ingestion, embeddings/vector search, external email/push, multi-tenant admin. See `NON_GOALS.md` (planned) and `TODO.md`.
