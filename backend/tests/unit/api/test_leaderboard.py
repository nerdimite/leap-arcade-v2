"""Subcutaneous tests for ``GET /leaderboard`` (HTTP surface + fake DAO stack)."""

from datetime import datetime
from typing import Callable

import pytest
import pytz
from fastapi import FastAPI
from fastapi.testclient import TestClient

from leap.api.routes import leaderboard as leaderboard_routes
from leap.types.game import GameSessionDTO, GameSessionStatus
from leap.types.player import PlayerDTO
from tests.fakes import FakeServiceContainer, make_fake_container


@pytest.fixture
def leaderboard_client(
    fake_container: FakeServiceContainer,
    auth_override: Callable[[FastAPI], None],
) -> TestClient:
    app = FastAPI()
    app.state.container = fake_container
    app.include_router(leaderboard_routes.router, prefix="/leaderboard")
    auth_override(app)
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


class TestLeaderboardUnauthorized:
    def test_missing_token_returns_401(self) -> None:
        app = FastAPI()
        app.state.container = make_fake_container()
        app.include_router(leaderboard_routes.router, prefix="/leaderboard")
        try:
            client = TestClient(app)
            r = client.get("/leaderboard")
            assert r.status_code == 401
        finally:
            app.dependency_overrides.clear()


class TestLeaderboardAuthorized:
    def test_includes_all_players_with_zeros_when_no_sessions(
        self, leaderboard_client: TestClient
    ) -> None:
        container = leaderboard_client.app.state.container
        container.player_dao._players = {
            "x": PlayerDTO(id="x", display_name="Xavier"),
            "y": PlayerDTO(id="y", display_name="Yvonne"),
        }
        r = leaderboard_client.get("/leaderboard")
        assert r.status_code == 200
        body = r.json()
        assert body["total_players"] == 2
        assert len(body["entries"]) == 2
        by_id = {e["player_id"]: e for e in body["entries"]}
        assert by_id["x"]["total_score"] == 0
        assert by_id["x"]["games_completed"] == 0
        assert by_id["y"]["total_score"] == 0

    def test_entries_ordered_and_ranked_sequentially(self, leaderboard_client: TestClient) -> None:
        early = datetime(2026, 1, 1, 10, 0, 0, tzinfo=pytz.UTC)
        late = datetime(2026, 1, 1, 11, 0, 0, tzinfo=pytz.UTC)
        container = leaderboard_client.app.state.container
        container.player_dao._players = {
            "a": PlayerDTO(id="a", display_name="Ann"),
            "b": PlayerDTO(id="b", display_name="Bob"),
            "c": PlayerDTO(id="c", display_name="Cy"),
        }
        container.game_session_dao._sessions = [
            GameSessionDTO(
                id="s-a1",
                player_id="a",
                game_id="rapid_fire",
                status=GameSessionStatus.COMPLETED,
                score=50,
                started_at=early,
                completed_at=early,
            ),
            GameSessionDTO(
                id="s-b1",
                player_id="b",
                game_id="rapid_fire",
                status=GameSessionStatus.COMPLETED,
                score=50,
                started_at=early,
                completed_at=late,
            ),
            GameSessionDTO(
                id="s-b2",
                player_id="b",
                game_id="rapid_fire",
                status=GameSessionStatus.COMPLETED,
                score=10,
                started_at=early,
                completed_at=late,
            ),
            GameSessionDTO(
                id="s-c1",
                player_id="c",
                game_id="rapid_fire",
                status=GameSessionStatus.ABANDONED,
                score=7,
                started_at=early,
                completed_at=late,
            ),
        ]
        r = leaderboard_client.get("/leaderboard")
        assert r.status_code == 200
        body = r.json()
        assert body["total_players"] == 3
        ids = [e["player_id"] for e in body["entries"]]
        assert ids == ["b", "a", "c"]
        ranks = [e["rank"] for e in body["entries"]]
        assert ranks == [1, 2, 3]
        bob = next(e for e in body["entries"] if e["player_id"] == "b")
        assert bob["total_score"] == 60
        assert bob["games_completed"] == 2
        cy = next(e for e in body["entries"] if e["player_id"] == "c")
        assert cy["total_score"] == 7
        assert cy["games_completed"] == 0

    def test_response_has_no_first_completion_field(self, leaderboard_client: TestClient) -> None:
        container = leaderboard_client.app.state.container
        container.player_dao._players = {"p1": PlayerDTO(id="p1", display_name="Pat")}
        r = leaderboard_client.get("/leaderboard")
        assert r.status_code == 200
        entry = r.json()["entries"][0]
        assert "first_completion" not in entry

    def test_fake_container_exposes_leaderboard_service(self) -> None:
        c = make_fake_container()
        assert c.leaderboard is not None
