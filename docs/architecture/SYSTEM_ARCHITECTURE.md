# SecondBrain — System Architecture

```mermaid
flowchart TB
  WEB[apps/web React+Vite] -->|proxy /api| API[FastAPI app/main.py]
  API --> AUTH[auth] & SRC[sources] & SRCH[search] & RES[research] & AG[agents] & PROJ[projects] & INT[integrations] & MEM[memory] & G[graph] & DASH[dashboard] & AUD[audit]
  AUTH & SRC & SRCH & RES & AG & PROJ & MEM & G & DASH & AUD --> SVC[services: ingestion / retrieval / agents / audit]
  SVC --> DB[(SQLite default / Postgres via DATABASE_URL)]
  API -.->|httpx retry+timeout| SW[Switch bridge: bridge_url + bearer]
  SW -.->|@mentions| ROOM[Switch room secondbrain]
  ROOM -.->|shared context| API
```

Monolith with clean service boundaries (API → services → models). No circular deps. See `DATA_ARCHITECTURE.md`, `AGENT_ARCHITECTURE.md`, `SWITCH_ARCHITECTURE.md`.
