"""Contract tests for shared hand-written fakes (Sub-1 test infrastructure)."""

from datetime import datetime

from typing import Callable

import pytest
import pytz
from fastapi import FastAPI
from fastapi.testclient import TestClient

from leap.api.routes import lobby
from leap.core.common.time import utc_now
from leap.types.game import GameSessionDTO, GameSessionStatus, LeaderboardEntryDTO
from leap.types.player import PlayerDTO
from leap.types.rapid_fire import RapidFireQuestionDTO
from tests.fakes import (
    FakeAsyncSession,
    FakeGameSessionDAO,
    FakePlayerDAO,
    FakeRapidFireQuestionDAO,
    FakeServiceContainer,
    make_fake_container,
)


def _question(qid: str = "q1") -> RapidFireQuestionDTO:
    return RapidFireQuestionDTO(
        id=qid,
        question="?",
        options=["a", "b"],
        correct_option_index=1,
        time_limit_ms=1000,
    )


class TestFakeRapidFireQuestionDAO:
    @pytest.mark.asyncio
    async def test_get_all_returns_cached_questions(self) -> None:
        q1, q2 = _question("q1"), _question("q2")
        dao = FakeRapidFireQuestionDAO(questions=[q1, q2])
        got = await dao.get_all(FakeAsyncSession())
        assert len(got) == 2
        assert {x.id for x in got} == {"q1", "q2"}

    def test_exposes_only_get_all_like_real_dao(self) -> None:
        assert hasattr(FakeRapidFireQuestionDAO, "get_all")
        assert not hasattr(FakeRapidFireQuestionDAO, "get_random_excluding")
        assert not hasattr(FakeRapidFireQuestionDAO, "get_question_count")


class TestFakeGameSessionDAOUpdateStatus:
    @pytest.mark.asyncio
    async def test_completed_sets_completed_at(self) -> None:
        started = datetime(2026, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
        session_row = GameSessionDTO(
            id="s1",
            player_id="p1",
            game_id="rapid_fire",
            status=GameSessionStatus.ACTIVE,
            score=None,
            started_at=started,
            completed_at=None,
        )
        dao = FakeGameSessionDAO(sessions=[session_row])
        before = utc_now()
        updated = await dao.update_status(FakeAsyncSession(), "s1", GameSessionStatus.COMPLETED, score=10)
        assert updated.completed_at is not None
        assert updated.completed_at >= before
        assert (updated.completed_at - started).total_seconds() >= 0

    @pytest.mark.asyncio
    async def test_active_does_not_set_completed_at(self) -> None:
        started = datetime(2026, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
        session_row = GameSessionDTO(
            id="s1",
            player_id="p1",
            game_id="rapid_fire",
            status=GameSessionStatus.ACTIVE,
            score=None,
            started_at=started,
            completed_at=None,
        )
        dao = FakeGameSessionDAO(sessions=[session_row])
        updated = await dao.update_status(FakeAsyncSession(), "s1", GameSessionStatus.ACTIVE)
        assert updated.completed_at is None


class TestFakeGameSessionDAOGetLeaderboard:
    @pytest.mark.asyncio
    async def test_aggregates_and_orders_by_domain_rules(self) -> None:
        """Higher score first; tie-break by more completed games; then earlier first_completion."""
        early = datetime(2026, 1, 1, 10, 0, 0, tzinfo=pytz.UTC)
        late = datetime(2026, 1, 1, 11, 0, 0, tzinfo=pytz.UTC)
        player_dao = FakePlayerDAO(
            players={
                "a": PlayerDTO(id="a", display_name="Ann"),
                "b": PlayerDTO(id="b", display_name="Bob"),
                "c": PlayerDTO(id="c", display_name="Cy"),
            }
        )
        sessions = [
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
                score=5,
                started_at=early,
                completed_at=late,
            ),
        ]
        dao = FakeGameSessionDAO(sessions=sessions, player_dao=player_dao)
        rows = await dao.get_leaderboard(FakeAsyncSession())
        assert isinstance(rows[0], LeaderboardEntryDTO)
        # Bob: 60 total, 2 completed; Ann: 50, 1; Cy: 5 abandoned-only → first_completion None sorts last among ties
        assert [r.player_id for r in rows] == ["b", "a", "c"]
        bob = next(r for r in rows if r.player_id == "b")
        assert bob.total_score == 60
        assert bob.games_completed == 2
        ann = next(r for r in rows if r.player_id == "a")
        assert ann.total_score == 50
        assert ann.games_completed == 1
        assert ann.first_completion == early
        cy = next(r for r in rows if r.player_id == "c")
        assert cy.total_score == 5
        assert cy.games_completed == 0
        assert cy.first_completion is None


class TestDependencyOverrideInfrastructure:
    def test_make_container_builds_working_fake_services(self) -> None:
        container = make_fake_container()
        assert isinstance(container, FakeServiceContainer)
        assert container.lobby is not None
        assert container.rapid_fire is not None
        assert container.leaderboard is not None

    def test_auth_override_fixture_wires_lobby_without_real_jwt(
        self,
        fake_container: FakeServiceContainer,
        auth_override: Callable[[FastAPI], None],
    ) -> None:
        app = FastAPI()
        app.state.container = fake_container
        app.include_router(lobby.router, prefix="/lobby")
        auth_override(app)
        try:
            client = TestClient(app)
            r = client.get("/lobby")
            assert r.status_code == 200
            assert r.json()["player_display_name"] == "Test Player"
        finally:
            app.dependency_overrides.clear()
