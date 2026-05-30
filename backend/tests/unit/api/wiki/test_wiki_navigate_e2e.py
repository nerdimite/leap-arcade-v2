"""API journey: play → navigate optimal path (respx + captured-style fixture HTML).

Includes a seeded-order happy path across all 5 puzzles (fixtures only, no Postgres).
"""

import asyncio
import re
from typing import Callable, List

import httpx
import respx
from fastapi import FastAPI
from fastapi.testclient import TestClient

from leap.api.routes.games import wiki as wiki_routes
from leap.games.wiki.html_rewriter import WikiHtmlRewriter
from leap.games.wiki.wikipedia_client import WikipediaClient
from leap.types.game import GameSessionStatus
from leap.types.player import CurrentPlayer, PlayerDTO
from leap.types.wiki import WikiPuzzleAttemptStatus, WikiRoundDTO
from tests.fakes import FakeServiceContainer, make_fake_container
from tests.fixtures.wiki_html_fixtures import (
    AMAZON_EC2_HTML,
    API_HTML,
    ARM_ARCHITECTURE_HTML,
    ATTENTION_ML_HTML,
    AUTOENCODER_HTML,
    BIOLOGY_HTML,
    BIOLOGY_IN_FICTION_HTML,
    BIOS_HTML,
    COMPUTER_HTML,
    DNA_HTML,
    FREEBSD_HTML,
    INTELLIGENT_MACHINE_HTML,
    MACHINE_LEARNING_HTML,
    MICROSERVICES_HTML,
    WORD_EMBEDDING_HTML,
)
from tests.unit.api.wiki.conftest import register_service_exception_handler

_REST = "https://en.wikipedia.org/api/rest_v1/page/html"
_BASE = re.escape(_REST)


def _two_rounds_prd_like() -> List[WikiRoundDTO]:
    return [
        WikiRoundDTO(
            id="e2e-r1",
            sequence_index=1,
            start_title="Biology",
            start_url="https://en.wikipedia.org/wiki/Biology",
            target_title="Attention (machine learning)",
            target_url="https://en.wikipedia.org/wiki/Attention_(machine_learning)",
            clue="e2e clue",
            optimal_click_count=3,
            solution_path=[
                "Biology",
                "Biology in fiction",
                "Artificial intelligence",
                "Attention (machine learning)",
            ],
            time_limit_ms=180_000,
        ),
        WikiRoundDTO(
            id="e2e-r2",
            sequence_index=2,
            start_title="Second",
            start_url="https://en.wikipedia.org/wiki/Second",
            target_title="Later",
            target_url="https://en.wikipedia.org/wiki/Later",
            clue="later",
            optimal_click_count=1,
            solution_path=[],
            time_limit_ms=180_000,
        ),
    ]


def _five_seeded_order_rounds() -> List[WikiRoundDTO]:
    """Matches ``leap/seeds/data/wiki.json`` ordering and clues.

    Round 1 ``end`` ("Attention") round-trips Wikimedia canonical
    ``Attention (machine learning)``. Round 2 ``end`` ("Word Embeddings")
    round-trips canonical ``Word embedding``. Other targets match the seed.
    """
    return [
        WikiRoundDTO(
            id="00000000-0000-4000-8000-000000000001",
            sequence_index=1,
            start_title="Biology",
            start_url="https://en.wikipedia.org/wiki/Biology",
            target_title="Attention (machine learning)",
            target_url="https://en.wikipedia.org/wiki/Attention_(machine_learning)",
            clue=("I let the model peek around, to find which words truly count — what am I?"),
            optimal_click_count=3,
            solution_path=[
                "Biology",
                "Biology in fiction",
                "Intelligent machine (redirects to Artificial intelligence)",
                "Attention (machine learning)",
            ],
            time_limit_ms=180_000,
        ),
        WikiRoundDTO(
            id="00000000-0000-4000-8000-000000000002",
            sequence_index=2,
            start_title="Biology",
            start_url="https://en.wikipedia.org/wiki/Biology",
            target_title="Word embedding",
            target_url="https://en.wikipedia.org/wiki/Word_embedding",
            clue=(
                "(👑 KING – 👨 MAN) + 👩 WOMAN = ❓. This AI math might feel strange, "
                "but it's how AI understands language. What's the technique behind this?"
            ),
            optimal_click_count=3,
            solution_path=[
                "Biology",
                "Biology in fiction",
                "Intelligent machine (redirects to Artificial intelligence)",
                "Word Embedding",
            ],
            time_limit_ms=180_000,
        ),
        WikiRoundDTO(
            id="00000000-0000-4000-8000-000000000003",
            sequence_index=3,
            start_title="Biology",
            start_url="https://en.wikipedia.org/wiki/Biology",
            target_title="Autoencoder",
            target_url="https://en.wikipedia.org/wiki/Autoencoder",
            clue=(
                "I compress, I decode, I learn without a guide. I see the input, hide "
                "its pride, then try to bring it back, side by side. What am I?"
            ),
            optimal_click_count=3,
            solution_path=["Biology", "DNA", "Machine learning", "Autoencoder"],
            time_limit_ms=180_000,
        ),
        WikiRoundDTO(
            id="00000000-0000-4000-8000-000000000004",
            sequence_index=4,
            start_title="Computer",
            start_url="https://en.wikipedia.org/wiki/Computer",
            target_title="Amazon Elastic Compute Cloud",
            target_url="https://en.wikipedia.org/wiki/Amazon_Elastic_Compute_Cloud",
            clue=(
                "I'm one of Amazon's Web Service, that allows users to rent virtual "
                "computers on which to run their own computer applications."
            ),
            optimal_click_count=3,
            solution_path=[
                "Computer",
                "ARM architecture (redirects to ARM architecture family)",
                "FreeBSD",
                "Amazon EC2 (redirects to Amazon Elastic Compute Cloud)",
            ],
            time_limit_ms=180_000,
        ),
        WikiRoundDTO(
            id="00000000-0000-4000-8000-000000000005",
            sequence_index=5,
            start_title="Computer",
            start_url="https://en.wikipedia.org/wiki/Computer",
            target_title="Microservices",
            target_url="https://en.wikipedia.org/wiki/Microservices",
            clue=(
                "This architectural style allows different services run independently, "
                "communicating through APIs. It's like building with LEGO blocks, where "
                "each block can be developed and scaled separately."
            ),
            optimal_click_count=3,
            solution_path=["Computer", "BIOS", "API", "Microservices"],
            time_limit_ms=180_000,
        ),
    ]


def _mock_article(*, html: str, canonical_slug: str) -> Callable[[httpx.Request], httpx.Response]:
    canon_url = f"{_REST}/{canonical_slug}"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-location": canon_url},
            text=html,
        )

    return handler


def _register_wikimedia_routes() -> None:
    mocks: List[tuple[str, str, str]] = [
        ("Biology", BIOLOGY_HTML, "Biology"),
        ("Biology_in_fiction", BIOLOGY_IN_FICTION_HTML, "Biology_in_fiction"),
        ("Intelligent_machine", INTELLIGENT_MACHINE_HTML, "Artificial_intelligence"),
        ("Attention_(machine_learning)", ATTENTION_ML_HTML, "Attention_(machine_learning)"),
        ("Word_embedding", WORD_EMBEDDING_HTML, "Word_embedding"),
        ("DNA", DNA_HTML, "DNA"),
        ("Machine_learning", MACHINE_LEARNING_HTML, "Machine_learning"),
        ("Autoencoder", AUTOENCODER_HTML, "Autoencoder"),
        ("Computer", COMPUTER_HTML, "Computer"),
        ("ARM_architecture", ARM_ARCHITECTURE_HTML, "ARM_architecture"),
        ("FreeBSD", FREEBSD_HTML, "FreeBSD"),
        ("Amazon_Elastic_Compute_Cloud", AMAZON_EC2_HTML, "Amazon_Elastic_Compute_Cloud"),
        ("BIOS", BIOS_HTML, "BIOS"),
        ("API", API_HTML, "API"),
        ("Microservices", MICROSERVICES_HTML, "Microservices"),
    ]
    for regex_suffix, html, canon_slug in mocks:
        respx.get(url__regex=rf"{_BASE}/{re.escape(regex_suffix)}$").mock(
            side_effect=_mock_article(html=html, canonical_slug=canon_slug),
        )


# Optimal navigations aligned with captured HTML links in wiki_html_fixtures.py
FIXTURE_CORPUS_NAV_STEPS: List[List[str]] = [
    ["Biology in fiction", "Intelligent machine", "Attention (machine learning)"],
    ["Biology in fiction", "Intelligent machine", "Word embedding"],
    ["DNA", "Machine learning", "Autoencoder"],
    ["ARM architecture", "FreeBSD", "Amazon Elastic Compute Cloud"],
    ["BIOS", "API", "Microservices"],
]


async def _warm_wiki(container: FakeServiceContainer) -> None:
    async with container.context_manager.session() as session:
        await container.wiki_speed_run.initialize(session)


class TestWikiNavigateE2E:
    def test_first_round_optimal_path_completes_puzzle(
        self, auth_player: CurrentPlayer, auth_override
    ) -> None:
        with respx.mock:
            _register_wikimedia_routes()
            httpx_c = httpx.AsyncClient()
            wiki_http = WikipediaClient(httpx_c)

            container = make_fake_container(
                players={
                    auth_player.id: PlayerDTO(
                        id=auth_player.id,
                        display_name=auth_player.display_name,
                    )
                },
                wiki_rounds=_two_rounds_prd_like(),
                wikipedia_client=wiki_http,
                wiki_html_rewriter=WikiHtmlRewriter(),
            )
            asyncio.run(_warm_wiki(container))

            app = FastAPI()
            register_service_exception_handler(app)
            app.state.container = container
            app.include_router(wiki_routes.router, prefix="/games/wiki")
            auth_override(app)
            try:
                client = TestClient(app)
                r0 = client.post("/games/wiki/play")
                assert r0.status_code == 200
                body0 = r0.json()
                assert body0["state"] == "active"
                assert body0["current"]["steps_taken"] == 0
                assert 'data-wiki-title="Biology in fiction"' in body0["current"]["article_html"]
                assert "https://" not in body0["current"]["article_html"]

                r1 = client.post("/games/wiki/navigate", json={"title": "Biology in fiction"})
                assert r1.status_code == 200
                assert r1.json()["state"] == "active"
                assert r1.json()["current"]["steps_taken"] == 1
                assert r1.json()["current"]["click_path"] == ["Biology in fiction"]

                r2 = client.post("/games/wiki/navigate", json={"title": "Intelligent machine"})
                assert r2.status_code == 200
                body2 = r2.json()
                assert body2["state"] == "active"
                assert body2["current"]["steps_taken"] == 2
                assert body2["current"]["click_path"][-1] == "Artificial intelligence"
                assert body2["current"]["current_title"] == "Artificial intelligence"

                r3 = client.post(
                    "/games/wiki/navigate", json={"title": "Attention (machine learning)"}
                )
                assert r3.status_code == 200
                body3 = r3.json()
                assert body3["state"] == "puzzle_completed"
                assert body3["puzzle_result"]["steps_taken"] == 3
                assert body3["puzzle_result"]["target_title"] == "Attention (machine learning)"
                assert body3["next_puzzle_available"] is True
                assert body3["total_score"] == body3["puzzle_result"]["score"]
                assert body3["puzzle_result"]["score"] > 0
            finally:
                app.dependency_overrides.clear()
                asyncio.run(httpx_c.aclose())
                asyncio.run(wiki_http.aclose())

    def test_five_round_fixture_corpus_optimal_path_completes_session(
        self, auth_player: CurrentPlayer, auth_override
    ) -> None:
        """Play + navigate optimal path across all 5 seeded rounds (respx, no Postgres)."""
        expected = _five_seeded_order_rounds()
        with respx.mock:
            _register_wikimedia_routes()
            httpx_c = httpx.AsyncClient()
            wiki_http = WikipediaClient(httpx_c)

            container = make_fake_container(
                players={
                    auth_player.id: PlayerDTO(
                        id=auth_player.id,
                        display_name=auth_player.display_name,
                    )
                },
                wiki_rounds=expected,
                wikipedia_client=wiki_http,
                wiki_html_rewriter=WikiHtmlRewriter(),
            )
            asyncio.run(_warm_wiki(container))

            app = FastAPI()
            register_service_exception_handler(app)
            app.state.container = container
            app.include_router(wiki_routes.router, prefix="/games/wiki")
            auth_override(app)
            try:
                client = TestClient(app)
                total_from_nav = 0
                for puzzle_idx, clicks in enumerate(FIXTURE_CORPUS_NAV_STEPS):
                    r_play = client.post("/games/wiki/play")
                    assert r_play.status_code == 200
                    play_body = r_play.json()
                    assert play_body["state"] == "active"
                    assert (
                        play_body["current"]["puzzle_index"] == expected[puzzle_idx].sequence_index
                    )
                    assert play_body["current"]["clue"] == expected[puzzle_idx].clue

                    for title in clicks:
                        r_nav = client.post("/games/wiki/navigate", json={"title": title})
                        assert r_nav.status_code == 200
                        nav_body = r_nav.json()
                        if nav_body["state"] == "active":
                            continue
                        assert nav_body["state"] == "puzzle_completed"
                        completed = puzzle_idx == len(expected) - 1
                        assert nav_body["next_puzzle_available"] is not completed
                        pr = nav_body["puzzle_result"]
                        assert pr["steps_taken"] == expected[puzzle_idx].optimal_click_count
                        assert pr["target_title"] == expected[puzzle_idx].target_title
                        assert pr["score"] > 0
                        assert pr["status"] == WikiPuzzleAttemptStatus.COMPLETED.value
                        total_from_nav += pr["score"]
                        assert nav_body["total_score"] == total_from_nav
                        break
                    else:
                        raise AssertionError("expected puzzle to complete within navigations")

                r_terminal = client.post("/games/wiki/play")
                assert r_terminal.status_code == 200
                term = r_terminal.json()
                assert term["state"] == "completed"
                assert term["total_score"] == total_from_nav
                assert sum(r["score"] for r in term["results"]) == term["total_score"]
                assert len(term["results"]) == 5
                for r in term["results"]:
                    assert r["status"] == WikiPuzzleAttemptStatus.COMPLETED.value

                sess = container.game_session_dao._sessions[0]  # noqa: SLF001
                assert sess.game_id == "wiki"
                assert sess.status == GameSessionStatus.COMPLETED
                assert sess.score == term["total_score"]
            finally:
                app.dependency_overrides.clear()
                asyncio.run(httpx_c.aclose())
                asyncio.run(wiki_http.aclose())
