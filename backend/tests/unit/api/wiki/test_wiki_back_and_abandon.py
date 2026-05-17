"""Tests for POST /games/wiki/back and /games/wiki/abandon."""

import asyncio
from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from leap.api.routes.games import wiki as wiki_routes
from leap.types.player import CurrentPlayer, PlayerDTO
from tests.fakes import FakeWikipediaClient, make_fake_container
from tests.unit.api.wiki.conftest import (
    register_service_exception_handler,
    sample_wiki_rounds,
    warm_wiki_cache,
)


@pytest.fixture
def wiki_client_back_on(
    auth_player: CurrentPlayer,
    auth_override,
) -> Generator[TestClient, None, None]:
    container = make_fake_container(
        players={
            auth_player.id: PlayerDTO(
                id=auth_player.id,
                display_name=auth_player.display_name,
            )
        },
        wiki_rounds=sample_wiki_rounds(),
        wikipedia_client=FakeWikipediaClient(
            {
                "TestStart": "<section><p>start</p></section>",
                "Mid": "<section><p>mid</p></section>",
            }
        ),
        wiki_back_button_enabled=True,
    )
    asyncio.run(warm_wiki_cache(container))
    app = FastAPI()
    register_service_exception_handler(app)
    app.state.container = container
    app.include_router(wiki_routes.router, prefix="/games/wiki")
    auth_override(app)
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_back_returns_403_when_disabled(wiki_client: TestClient) -> None:
    assert wiki_client.post("/games/wiki/play").status_code == 200
    assert wiki_client.post("/games/wiki/navigate", json={"title": "Mid"}).status_code == 200
    r3 = wiki_client.post("/games/wiki/back")
    assert r3.status_code == 403


def test_back_ok_when_enabled(wiki_client_back_on: TestClient) -> None:
    c = wiki_client_back_on
    assert c.post("/games/wiki/play").status_code == 200
    assert c.post("/games/wiki/navigate", json={"title": "Mid"}).status_code == 200
    rb = c.post("/games/wiki/back")
    assert rb.status_code == 200
    body = rb.json()
    assert body["state"] == "active"
    assert body["current"]["steps_taken"] == 2
    assert body["current"]["click_path"] == ["Mid", "TestStart"]


def test_abandon_returns_terminal_and_session_marked(
    wiki_client: TestClient,
    auth_player: CurrentPlayer,
) -> None:
    c = wiki_client
    assert c.post("/games/wiki/play").status_code == 200
    assert c.post("/games/wiki/navigate", json={"title": "Mid"}).status_code == 200
    ra = c.post("/games/wiki/abandon")
    assert ra.status_code == 200
    body = ra.json()
    assert body["state"] == "abandoned"
    assert len(body["results"]) == 1
    assert body["results"][0]["status"] == "abandoned"
    assert body["results"][0]["score"] == 0

    container = c.app.state.container
    sessions = [s for s in container.game_session_dao._sessions if s.game_id == "wiki"]  # noqa: SLF001
    assert len(sessions) == 1
    assert sessions[0].player_id == auth_player.id
    assert sessions[0].status.value == "abandoned"
