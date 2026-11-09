#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
API_BASE="${API_BASE:-http://localhost:8000}"
OUT="$ROOT/packages/shared/openapi.json"
mkdir -p "$ROOT/packages/shared"
if curl -fsS "$API_BASE/openapi.json" -o "$OUT" 2>/dev/null; then
  echo "saved $OUT from $API_BASE/openapi.json"
else
  echo "server not running, falling back to TestClient fetch" >&2
  (cd "$ROOT/apps/api" && .venv/bin/python - "$OUT" <<'PY'
import json, sys
from fastapi.testclient import TestClient
from app.main import app
spec = TestClient(app).get("/openapi.json").json()
with open(sys.argv[1], "w") as f:
    json.dump(spec, f, indent=1)
print(f"saved {sys.argv[1]} via TestClient")
PY
  )
fi
echo "Types are hand-maintained in packages/shared/types.ts (header dated from openapi.json)."
