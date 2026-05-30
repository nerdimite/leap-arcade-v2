"""Subcutaneous tests for ``POST /games/rapid-fire/abandon``."""

from datetime import timedelta

from fastapi.testclient import TestClient

from leap.core.common.time import utc_now
from leap.types.game import GameSessionDTO, GameSessionStatus
from leap.types.player import CurrentPlayer
from tests.unit.api.rapid_fire.assertions import assert_no_correct_option_index_in_payload


class TestRapidFireAbandon:
    def test_abandon_with_answers_yields_positive_score(
        self, rapid_fire_client: TestClient, auth_player: CurrentPlayer
    ) -> None:
        client = rapid_fire_client
        p = client.post("/games/rapid-fire/play")
        assert p.status_code == 200
        body = p.json()
        qid = body["question"]["id"]
        correct = {"rf-q1": 1, "rf-q2": 2, "rf-q3": 3}[qid]

        r = client.post(
            "/games/rapid-fire/answer",
            json={"question_id": qid, "selected_option": correct, "time_ms": 500},
        )
        assert r.status_code == 200
        assert_no_correct_option_index_in_payload(r.json())

        a = client.post("/games/rapid-fire/abandon")
        assert a.status_code == 200
        payload = a.json()
        assert_no_correct_option_index_in_payload(payload)
        assert payload["result"]["score"] > 0
        assert payload["result"]["correct_count"] >= 1

    def test_abandon_without_answers_yields_zero_score(self, rapid_fire_client: TestClient) -> None:
        client = rapid_fire_client
        p = client.post("/games/rapid-fire/play")
        assert p.status_code == 200

        a = client.post("/games/rapid-fire/abandon")
        assert a.status_code == 200
        payload = a.json()
        assert_no_correct_option_index_in_payload(payload)
        res = payload["result"]
        assert res["score"] == 0
        assert res["correct_count"] == 0
        assert res["wrong_count"] == 0
        assert res["skipped_count"] == 0

    def test_abandon_when_already_completed_returns_409(
        self, rapid_fire_client: TestClient, auth_player: CurrentPlayer
    ) -> None:
        container = rapid_fire_client.app.state.container
        done_at = utc_now()
        started = done_at - timedelta(minutes=2)
        sid = "already-done"
        container.game_session_dao._sessions = [
            GameSessionDTO(
                id=sid,
                player_id=auth_player.id,
                game_id="rapid_fire",
                status=GameSessionStatus.COMPLETED,
                score=10,
                started_at=started,
                completed_at=done_at,
            )
        ]
        container.rapid_fire_answer_dao._answers = []

        r = rapid_fire_client.post("/games/rapid-fire/abandon")
        assert r.status_code == 409

    def test_abandon_without_session_returns_404(self, rapid_fire_client: TestClient) -> None:
        container = rapid_fire_client.app.state.container
        container.game_session_dao._sessions = []

        r = rapid_fire_client.post("/games/rapid-fire/abandon")
        assert r.status_code == 404
