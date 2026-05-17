"""HTTP fetcher for Wikimedia page HTML (REST `page/html` endpoint)."""

from typing import Dict, Optional
from urllib.parse import unquote, quote

import httpx

from leap.types.wiki import WikiArticleDTO


class WikipediaClient:
    """Fetches article HTML; follows redirects (httpx default). Caches by canonical title."""

    _BASE = "https://en.wikipedia.org/api/rest_v1/page/html"

    def __init__(self, client: Optional[httpx.AsyncClient] = None) -> None:
        self._owns_client = client is None
        headers = {
            "User-Agent": "LEAP-WikiSpeedRun/0.1 (corporate event; contact: leap@example.invalid)",
            "Accept": "text/html; charset=utf-8",
        }
        self._client = client or httpx.AsyncClient(
            headers=headers,
            follow_redirects=True,
            timeout=30.0,
        )
        self._cache: Dict[str, WikiArticleDTO] = {}

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    @staticmethod
    def _canonical_title_from_content_location(content_location: str, fallback_requested: str) -> str:
        if not content_location:
            return fallback_requested
        if "/page/html/" in content_location:
            segment = content_location.rsplit("/page/html/", 1)[-1]
            segment = segment.split("/", 1)[0]
            return unquote(segment).replace("_", " ")
        return fallback_requested

    async def fetch_article_html(self, title: str) -> WikiArticleDTO:
        if title in self._cache:
            hit = self._cache[title]
            if hit.requested_title == title:
                return hit
            return WikiArticleDTO(
                requested_title=title,
                canonical_title=hit.canonical_title,
                html=hit.html,
            )

        safe = quote(title.replace(" ", "_"), safe="()/:")
        url = f"{self._BASE}/{safe}"

        resp = await self._client.get(url)
        resp.raise_for_status()
        canonical = self._canonical_title_from_content_location(
            resp.headers.get("content-location", ""),
            title,
        )
        dto = WikiArticleDTO(
            requested_title=title,
            canonical_title=canonical,
            html=resp.text,
        )
        self._cache[dto.requested_title] = dto
        if dto.canonical_title != dto.requested_title:
            self._cache[dto.canonical_title] = dto
        return dto
