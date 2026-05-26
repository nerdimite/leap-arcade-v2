"""Subcutaneous tests for ``POST /games/four-pics/abandon``."""

from datetime import timedelta

from fastapi.testclient import TestClient

from leap.core.common.time import utc_now
from leap.types.game import GameSessionDTO, GameSessionStatus
from leap.types.player import CurrentPlayer


class TestFourPicsAbandon:
    def test_abandon_active_session_returns_result_shape(
        self, four_pics_client: TestClient
    ) -> None:
        client = four_pics_client
        play = client.post("/games/four-pics/play")
        assert play.status_code == 200
        qid = play.json()["question"]["question_id"]
        correct = {"fp-q1": 2, "fp-q2": 0, "fp-q3": 1}[qid]

        answered = client.post(
            "/games/four-pics/answer",
            json={"question_id": qid, "selected_index": correct, "time_ms": 500},
        )
        assert answered.status_code == 200

        abandon = client.post("/games/four-pics/abandon")
        assert abandon.status_code == 200
        payload = abandon.json()
        result = payload["result"]

        assert isinstance(result["score"], int)
        assert result["questions_correct"] == 1
        assert result["questions_wrong"] == 1
        assert result["questions_not_reached"] == 1
        assert len(result["questions"]) == 3

        statuses = {row["question_id"]: row["status"] for row in result["questions"]}
        assert statuses[qid] == "correct"
        assert sum(1 for s in statuses.values() if s == "wrong") == 1
        assert sum(1 for s in statuses.values() if s == "not_reached") == 1

    def test_abandon_when_already_completed_returns_409(
        self, four_pics_client: TestClient, auth_player: CurrentPlayer
    ) -> None:
        container = four_pics_client.app.state.container
        done_at = utc_now()
        started = done_at - timedelta(minutes=2)
        container.game_session_dao._sessions = [
            GameSessionDTO(
                id="fp-done",
                player_id=auth_player.id,
                game_id="four_pics",
                status=GameSessionStatus.COMPLETED,
                score=300,
                started_at=started,
                completed_at=done_at,
            )
        ]
        container.four_pics_attempt_dao._attempts = []

        response = four_pics_client.post("/games/four-pics/abandon")
        assert response.status_code == 409

    def test_abandon_without_session_returns_404(self, four_pics_client: TestClient) -> None:
        container = four_pics_client.app.state.container
        container.game_session_dao._sessions = []

        response = four_pics_client.post("/games/four-pics/abandon")
        assert response.status_code == 404
