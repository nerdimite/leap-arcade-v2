"""Tests for ``GET /players/me/sessions``."""

from datetime import datetime
from typing import Callable, List

import pytest
import pytz
from fastapi import FastAPI
from fastapi.testclient import TestClient

from leap.api.routes import players as players_routes
from leap.config.constants import GAME_IDS
from leap.types.game import GameSessionDTO, GameSessionStatus
from leap.types.player import PlayerDTO
from tests.fakes import FakeServiceContainer, make_fake_container


@pytest.fixture
def player_sessions_client(
    fake_container: FakeServiceContainer,
    auth_override: Callable[[FastAPI], None],
) -> TestClient:
    app = FastAPI()
    app.state.container = fake_container
    app.include_router(players_routes.router, prefix="/players")
    auth_override(app)
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


class TestPlayerSessionsUnauthorized:
    def test_missing_token_returns_401(self) -> None:
        app = FastAPI()
        app.state.container = make_fake_container()
        app.include_router(players_routes.router, prefix="/players")
        try:
            client = TestClient(app)
            r = client.get("/players/me/sessions")
            assert r.status_code == 401
        finally:
            app.dependency_overrides.clear()


class TestPlayerSessionsAuthorized:
    def test_returns_sessions_for_authenticated_player(
        self, player_sessions_client: TestClient
    ) -> None:
        t0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
        container = player_sessions_client.app.state.container
        container.player_dao._players = {
            "emp001": PlayerDTO(id="emp001", display_name="Test Player"),
        }
        container.game_session_dao._sessions = [
            GameSessionDTO(
                id="s-rf",
                player_id="emp001",
                game_id="rapid_fire",
                status=GameSessionStatus.ACTIVE,
                score=0,
                started_at=t0,
                completed_at=None,
            ),
            GameSessionDTO(
                id="s-wiki",
                player_id="emp001",
                game_id="wiki",
                status=GameSessionStatus.COMPLETED,
                score=42,
                started_at=t0,
                completed_at=t0,
            ),
        ]
        r = player_sessions_client.get("/players/me/sessions")
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, list)
        assert len(body) == 2
        by_game = {item["game_id"]: item for item in body}
        assert by_game["rapid_fire"]["status"] == "active"
        assert by_game["rapid_fire"]["score"] is None
        assert by_game["wiki"]["status"] == "completed"
        assert by_game["wiki"]["score"] == 42

    def test_returns_empty_list_when_no_sessions(self, player_sessions_client: TestClient) -> None:
        container = player_sessions_client.app.state.container
        container.player_dao._players = {
            "emp001": PlayerDTO(id="emp001", display_name="Test Player"),
        }
        container.game_session_dao._sessions = []
        r = player_sessions_client.get("/players/me/sessions")
        assert r.status_code == 200
        assert r.json() == []

    def test_includes_all_five_game_ids_when_present(
        self, player_sessions_client: TestClient
    ) -> None:
        t0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
        container = player_sessions_client.app.state.container
        container.player_dao._players = {
            "emp001": PlayerDTO(id="emp001", display_name="Test Player"),
        }
        sessions: List[GameSessionDTO] = []
        for idx, gid in enumerate(GAME_IDS):
            sessions.append(
                GameSessionDTO(
                    id=f"s-{gid}",
                    player_id="emp001",
                    game_id=gid,
                    status=GameSessionStatus.COMPLETED,
                    score=idx,
                    started_at=t0,
                    completed_at=t0,
                )
            )
        container.game_session_dao._sessions = sessions
        r = player_sessions_client.get("/players/me/sessions")
        assert r.status_code == 200
        returned_ids = {item["game_id"] for item in r.json()}
        assert returned_ids == set(GAME_IDS)
