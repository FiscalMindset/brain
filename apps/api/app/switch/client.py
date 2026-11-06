"""Switch bridge client with timeouts, retries, typed errors."""
from __future__ import annotations
import os, time
import httpx
DOC_OPS = ("list_rooms", "post_message", "read_context")

class SwitchError(Exception):
    def __init__(self, message: str, status: int | None = None):
        super().__init__(message); self.status = status

class SwitchClient:
    def __init__(self, bridge_url=None, api_key=None, agent_id=None, transport=None):
        self.bridge_url = (bridge_url or os.getenv("SWITCH_BRIDGE_URL", "")).rstrip("/")
        self.api_key = api_key or os.getenv("SWITCH_API_KEY", "")
        self.agent_id = agent_id or os.getenv("SWITCH_AGENT_ID", "")
        self._transport = transport
    @property
    def is_configured(self) -> bool:
        return bool(self.bridge_url)
    def _headers(self): return {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
    def _client(self): return httpx.Client(base_url=self.bridge_url, headers=self._headers(), timeout=httpx.Timeout(10.0, read=10.0, write=10.0), transport=self._transport)
    def _request_with_retry(self, method, path, **kw):
        last_exc = None
        for attempt in range(2):
            try:
                with self._client() as client:
                    resp = client.request(method, path, **kw)
                    if resp.status_code in (429, 500, 502, 503, 504) and attempt == 0:
                        last_exc = SwitchError(f"Switch {resp.status_code}", status=resp.status_code)
                        time.sleep(0.5 if resp.status_code != 429 else 1.0)
                        continue
                    try: resp.raise_for_status()
                    except httpx.HTTPStatusError as e: raise SwitchError(str(e), status=e.response.status_code)
                    try: return resp.json()
                    except Exception: return {"status": resp.status_code, "text": resp.text}
            except SwitchError: raise
            except httpx.RequestError as e:
                if attempt == 0: last_exc = SwitchError(str(e)); time.sleep(0.5); continue
                raise SwitchError(str(e))
        raise last_exc or SwitchError("request failed")
    def register(self, name, **fields): return self._request_with_retry("POST", "/agents", json={"name": name, **fields})
    def connection_ws_url(self, agent_id=None): return f"{self.bridge_url}/agents/{agent_id or self.agent_id}/connection/ws"
    def run_op(self, op, payload=None, agent_id=None):
        if op not in DOC_OPS: raise ValueError(f"unsupported Switch op '{op}': documented ops are {DOC_OPS}")
        return self._request_with_retry("POST", f"/agents/{agent_id or self.agent_id}/ops/{op}", json=payload or {})
    def list_rooms(self): return self.run_op("list_rooms")
    def post_message(self, room_id, text): return self.run_op("post_message", {"room_id": room_id, "text": text})
    def read_context(self, room_id, limit=20): return self.run_op("read_context", {"room_id": room_id, "limit": limit})
    def send_message(self, text, agent_id=None): return self._request_with_retry("POST", f"/agents/{agent_id or self.agent_id}/messages", json={"text": text})
    def post_research_to_room(self, room_id, report):
        lines = [f"# Research: {report.get('query', '')}", ""]
        for f in report.get("findings", [])[:5]: lines.append(f"- {f.get('text','')[:200]}")
        lines += ["", "## QA", *[f"- {q}" for q in report.get("qa", {}).get("questions", [])]]
        return self.post_message(room_id, "\n".join(lines))
