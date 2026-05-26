"""Subcutaneous tests for ``POST /games/pinpoint/abandon``."""

from datetime import timedelta

from fastapi.testclient import TestClient

from leap.core.common.time import utc_now
from leap.types.game import GameSessionDTO, GameSessionStatus
from leap.types.player import CurrentPlayer


class TestPinpointAbandon:
    def test_abandon_mid_puzzle_returns_not_reached_rows(
        self, pinpoint_client: TestClient
    ) -> None:
        client = pinpoint_client
        play = client.post("/games/pinpoint/play")
        assert play.status_code == 200

        abandon = client.post("/games/pinpoint/abandon")
        assert abandon.status_code == 200
        payload = abandon.json()
        result = payload["result"]
        assert result["puzzles_failed"] == 1
        assert result["puzzles_not_reached"] == 1
        not_reached = [p for p in result["puzzles"] if p["status"] == "not_reached"]
        assert len(not_reached) == 1
        assert not_reached[0]["clues_used"] is None
        assert not_reached[0]["score"] == 0
        assert not_reached[0]["time_bonus"] == 0
        assert "answer" not in payload
        assert "answer_aliases" not in payload

    def test_abandon_when_already_completed_returns_409(
        self, pinpoint_client: TestClient, auth_player: CurrentPlayer
    ) -> None:
        container = pinpoint_client.app.state.container
        done_at = utc_now()
        started = done_at - timedelta(minutes=2)
        container.game_session_dao._sessions = [
            GameSessionDTO(
                id="already-done",
                player_id=auth_player.id,
                game_id="pinpoint",
                status=GameSessionStatus.COMPLETED,
                score=500,
                started_at=started,
                completed_at=done_at,
            )
        ]

        response = pinpoint_client.post("/games/pinpoint/abandon")
        assert response.status_code == 409

    def test_abandon_without_session_returns_404(self, pinpoint_client: TestClient) -> None:
        container = pinpoint_client.app.state.container
        container.game_session_dao._sessions = []

        response = pinpoint_client.post("/games/pinpoint/abandon")
        assert response.status_code == 404
