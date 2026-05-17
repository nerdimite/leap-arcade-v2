"""Tests for LobbyService.get_lobby."""

import pytest

from leap.api.deps import CurrentPlayer
from leap.service.lobby_service import LobbyService
from leap.types.game import GameSessionDTO, GameSessionStatus
from leap.core.common.time import utc_now
from tests.fakes import FakeContextManager, FakeGameSessionDAO


def _make_player(corp_id: str = "emp001", display_name: str = "Alice") -> CurrentPlayer:
    return CurrentPlayer(id=corp_id, display_name=display_name)


def _make_service(sessions: list[GameSessionDTO] | None = None) -> LobbyService:
    return LobbyService(
        context_manager=FakeContextManager(),
        game_session_dao=FakeGameSessionDAO(sessions=sessions or []),
    )


def _completed_session(game_id: str, score: int) -> GameSessionDTO:
    return GameSessionDTO(
        id=f"session-{game_id}",
        player_id="emp001",
        game_id=game_id,
        status=GameSessionStatus.COMPLETED,
        score=score,
        started_at=utc_now(),
        completed_at=utc_now(),
    )


class TestLobbyServiceGetLobby:
    @pytest.mark.asyncio
    async def test_returns_all_games_when_player_has_not_played_any(self):
        """Fresh player → all games returned with has_played=False and no score."""
        svc = _make_service()
        result = await svc.get_lobby(_make_player())

        assert len(result.games) == 5
        assert all(not g.has_played for g in result.games)
        assert all(g.score is None for g in result.games)

    @pytest.mark.asyncio
    async def test_marks_played_game_with_score(self):
        """Player with a completed rapid_fire session → has_played True and score set."""
        svc = _make_service(sessions=[_completed_session("rapid_fire", 80)])
        result = await svc.get_lobby(_make_player())

        rapid_fire = next(g for g in result.games if g.game_id == "rapid_fire")
        assert rapid_fire.has_played is True
        assert rapid_fire.score == 80

    @pytest.mark.asyncio
    async def test_unplayed_games_still_present_when_some_played(self):
        """Played one game → the other 4 still appear with has_played=False."""
        svc = _make_service(sessions=[_completed_session("rapid_fire", 80)])
        result = await svc.get_lobby(_make_player())

        unplayed = [g for g in result.games if g.game_id != "rapid_fire"]
        assert len(unplayed) == 4
        assert all(not g.has_played for g in unplayed)

    @pytest.mark.asyncio
    async def test_game_order_matches_games_constant(self):
        """Games are returned in the canonical GAMES registry order."""
        from leap.config.constants import GAME_IDS

        svc = _make_service()
        result = await svc.get_lobby(_make_player())

        assert [g.game_id for g in result.games] == GAME_IDS

    @pytest.mark.asyncio
    async def test_active_session_does_not_count_as_played(self):
        """An in-progress session is not locked in the lobby yet."""
        active = GameSessionDTO(
            id="session-rf",
            player_id="emp001",
            game_id="rapid_fire",
            status=GameSessionStatus.ACTIVE,
            score=None,
            started_at=utc_now(),
            completed_at=None,
        )
        svc = _make_service(sessions=[active])
        result = await svc.get_lobby(_make_player())

        rapid_fire = next(g for g in result.games if g.game_id == "rapid_fire")
        assert rapid_fire.has_played is False

    @pytest.mark.asyncio
    async def test_abandoned_session_counts_as_played_with_score(self):
        """Abandoned sessions lock the tile like completed ones (partial score shown)."""
        abandoned = GameSessionDTO(
            id="session-wiki",
            player_id="emp001",
            game_id="wiki",
            status=GameSessionStatus.ABANDONED,
            score=120,
            started_at=utc_now(),
            completed_at=utc_now(),
        )
        svc = _make_service(sessions=[abandoned])
        result = await svc.get_lobby(_make_player())

        wiki = next(g for g in result.games if g.game_id == "wiki")
        assert wiki.has_played is True
        assert wiki.score == 120

    @pytest.mark.asyncio
    async def test_player_display_name_in_response(self):
        """Player display_name from JWT is echoed back in the lobby response."""
        svc = _make_service()
        result = await svc.get_lobby(_make_player(display_name="Bob Verma"))
        assert result.player_display_name == "Bob Verma"

# TODO (executor): add edge case tests for:
# - player with sessions for all 5 games
# - player whose session list contains an unknown game_id (should be silently ignored)
