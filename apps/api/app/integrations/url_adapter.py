"""URL ingestion adapter: fetch a page and extract readable text."""

from __future__ import annotations

import html
import re

import httpx

MAX_BYTES = 500 * 1024  # 500KB max response body
TIMEOUT_SECONDS = 10.0

_TAG_RE = re.compile(r"<[^>]+>")
_SCRIPT_RE = re.compile(r"<script\b[^>]*>.*?</script\s*>", re.IGNORECASE | re.DOTALL)
_STYLE_RE = re.compile(r"<style\b[^>]*>.*?</style\s*>", re.IGNORECASE | re.DOTALL)
_TITLE_RE = re.compile(r"<title\b[^>]*>(.*?)</title\s*>", re.IGNORECASE | re.DOTALL)
_PARA_RE = re.compile(r"<p\b[^>]*>(.*?)</p\s*>", re.IGNORECASE | re.DOTALL)
_WS_RE = re.compile(r"\s+")


class UrlFetchError(Exception):
    """Raised when fetching a URL fails (network error, bad status, timeout)."""


class UrlOversizeError(UrlFetchError):
    """Raised when the response exceeds the size limit."""


def _clean(text: str) -> str:
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    return _WS_RE.sub(" ", text).strip()


class UrlAdapter:
    """Fetch and extract (text, title, meta) from a URL."""

    def fetch(self, url: str) -> tuple[str, str, dict]:
        headers = {"User-Agent": "SecondBrain-URLAdapter/1.0"}
        try:
            with httpx.Client(timeout=TIMEOUT_SECONDS, follow_redirects=True) as client:
                response = client.get(url, headers=headers)
        except (httpx.TimeoutException, httpx.RequestError) as exc:
            raise UrlFetchError(f"fetch failed for {url}: {exc}") from exc

        if response.status_code < 200 or response.status_code >= 300:
            raise UrlFetchError(f"fetch failed for {url}: HTTP {response.status_code}")

        body = response.content
        if len(body) > MAX_BYTES:
            raise UrlOversizeError(f"response too large ({len(body)} bytes > {MAX_BYTES})")

        content_type = response.headers.get("content-type", "")

        page = body.decode(response.encoding or "utf-8", errors="replace")

        page = _SCRIPT_RE.sub(" ", page)
        page = _STYLE_RE.sub(" ", page)

        title = ""
        title_match = _TITLE_RE.search(page)
        if title_match:
            title = _clean(title_match.group(1))

        paragraphs = [_clean(p) for p in _PARA_RE.findall(page)]
        paragraphs = [p for p in paragraphs if p]
        if paragraphs:
            text = "\n".join(paragraphs)
        else:
            text = _clean(page)

        if not text and not title:
            raise UrlFetchError(f"no extractable text from {url}")

        try:
            final_url = str(response.url)
        except RuntimeError:
            final_url = url
        meta = {
            "url": url,
            "final_url": final_url,
            "status_code": response.status_code,
            "content_type": content_type,
            "size_bytes": len(body),
        }
        return text, title, meta
