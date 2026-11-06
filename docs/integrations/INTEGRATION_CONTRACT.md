# Integration Contract

```python
validate(payload: dict) -> None  # raise ValueError on bad input
ingest(payload: dict) -> {"ok": bool, "external_id": str, "error": str | None}
```
Idempotent on `external_id`. Structured errors, never raise on transport failures. Until OAuth configured: `ok: False` with reason.
