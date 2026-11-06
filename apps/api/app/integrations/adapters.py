"""Integration adapter stubs sharing one ingestion contract.

Every adapter here is a **stub**: real OAuth / API keys are required before
any live ingestion can happen. ``ingest`` therefore degrades gracefully by
returning a structured error instead of raising or pretending to work.

Contract (common to all adapters)::

    validate(payload: dict) -> None          # raise ValueError on bad input
    ingest(payload: dict) -> IngestResult    # idempotent on payload["external_id"]
    IngestResult = {"ok": bool, "external_id": str, "error": str | None}
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict


class IngestResult(TypedDict):
    ok: bool
    external_id: str
    error: str | None


class BaseAdapter(ABC):
    """Shared stub behaviour: validation + graceful degradation."""

    name: str = "base"
    requires_oauth: bool = True
    status: str = "not_configured"

    @abstractmethod
    def validate(self, payload: dict) -> None:
        """Raise ValueError if *payload* is missing required fields."""
        raise NotImplementedError

    def ingest(self, payload: dict) -> IngestResult:
        """Stub: without OAuth credentials we can only report, not ingest."""
        self.validate(payload)
        external_id = str(payload.get("external_id", "unknown"))
        return IngestResult(
            ok=False,
            external_id=external_id,
            error=f"adapter '{self.name}' is not configured: real OAuth credentials are required",
        )


class ChatGPTAdapter(BaseAdapter):
    name = "chatgpt"

    def validate(self, payload: dict) -> None:
        if not payload.get("content"):
            raise ValueError("chatgpt: 'content' is required")


class YouTubeAdapter(BaseAdapter):
    name = "youtube"

    def validate(self, payload: dict) -> None:
        if not payload.get("video_id"):
            raise ValueError("youtube: 'video_id' is required")


class GitHubAdapter(BaseAdapter):
    name = "github"

    def validate(self, payload: dict) -> None:
        if not payload.get("repo") or not payload.get("path"):
            raise ValueError("github: 'repo' and 'path' are required")


class DriveAdapter(BaseAdapter):
    name = "drive"

    def validate(self, payload: dict) -> None:
        if not payload.get("file_id"):
            raise ValueError("drive: 'file_id' is required")


class NotionAdapter(BaseAdapter):
    name = "notion"

    def validate(self, payload: dict) -> None:
        if not payload.get("page_id"):
            raise ValueError("notion: 'page_id' is required")


class PdfAdapter(BaseAdapter):
    name = "pdf"

    def validate(self, payload: dict) -> None:
        if not payload.get("content"):
            raise ValueError("pdf: 'content' is required")


class MarkdownAdapter(BaseAdapter):
    name = "markdown"

    def validate(self, payload: dict) -> None:
        if not payload.get("content"):
            raise ValueError("markdown: 'content' is required")


class BookmarkAdapter(BaseAdapter):
    name = "bookmarks"

    def validate(self, payload: dict) -> None:
        if not payload.get("url"):
            raise ValueError("bookmarks: 'url' is required")


ADAPTERS: list[BaseAdapter] = [
    ChatGPTAdapter(),
    YouTubeAdapter(),
    GitHubAdapter(),
    DriveAdapter(),
    NotionAdapter(),
    PdfAdapter(),
    MarkdownAdapter(),
    BookmarkAdapter(),
]


def describe_contract() -> dict:
    """Machine-readable description of the ingestion contract."""
    return {
        "validate": "validate(payload: dict) -> None (raises ValueError)",
        "ingest": "ingest(payload: dict) -> {ok, external_id, error}",
        "idempotency": "ingest must be idempotent on payload['external_id']",
        "error_handling": "return structured errors; never raise on transport failures",
    }
