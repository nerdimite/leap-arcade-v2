"""Unit tests for WikipediaClient (mocked transport, no live network)."""

import asyncio

import httpx
import pytest

from leap.games.wiki.wikipedia_client import WikipediaClient


def test_fetch_decodes_canonical_title_from_content_location() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert "Attention_(machine_learning)" in str(request.url)
        return httpx.Response(
            200,
            headers={
                "content-location": "https://en.wikipedia.org/api/rest_v1/page/html/Attention_%28machine_learning%29"
            },
            text="<section><p>ok</p></section>",
        )

    transport = httpx.MockTransport(handler)

    async def run() -> None:
        async with httpx.AsyncClient(transport=transport) as base:
            client = WikipediaClient(base)
            dto = await client.fetch_article_html("Attention (machine learning)")
            assert dto.requested_title == "Attention (machine learning)"
            assert dto.canonical_title == "Attention (machine learning)"
            assert "ok" in dto.html

    asyncio.run(run())


@pytest.mark.asyncio
async def test_cache_serves_second_fetch_without_duplicate_request() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url))
        return httpx.Response(
            200,
            headers={"content-location": str(request.url)},
            text="<p>one</p>",
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as base:
        client = WikipediaClient(base)
        a = await client.fetch_article_html("Biology")
        b = await client.fetch_article_html("Biology")
        assert a.html == b.html
        assert len(calls) == 1


@pytest.mark.asyncio
async def test_cache_hit_by_canonical_after_redirect_alias() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url))
        if "Intelligent_machine" in str(request.url):
            return httpx.Response(
                200,
                headers={
                    "content-location": "https://en.wikipedia.org/api/rest_v1/page/html/Artificial_intelligence"
                },
                text="<p>AI</p>",
            )
        raise AssertionError("unexpected URL")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as base:
        client = WikipediaClient(base)
        first = await client.fetch_article_html("Intelligent machine")
        assert first.canonical_title == "Artificial intelligence"
        second = await client.fetch_article_html("Artificial intelligence")
        assert second.requested_title == "Artificial intelligence"
        assert second.canonical_title == "Artificial intelligence"
        assert second.html == first.html
        assert len(calls) == 1
