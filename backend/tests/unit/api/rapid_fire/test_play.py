"""Subcutaneous tests for ``POST /games/rapid-fire/play``."""

from datetime import timedelta

from fastapi.testclient import TestClient

from leap.core.common.time import utc_now
from leap.types.game import GameSessionDTO, GameSessionStatus
from leap.types.player import CurrentPlayer
from leap.types.rapid_fire import RapidFireAnswerDTO

from tests.unit.api.rapid_fire.assertions import assert_no_correct_option_index_in_payload


class TestRapidFirePlay:
    def test_second_play_before_any_answer_resumes_same_session(
        self, rapid_fire_client: TestClient, auth_player: CurrentPlayer
    ) -> None:
        r1 = rapid_fire_client.post("/games/rapid-fire/play")
        assert r1.status_code == 200
        r2 = rapid_fire_client.post("/games/rapid-fire/play")
        assert r2.status_code == 200
        assert r2.json()["game_session_id"] == r1.json()["game_session_id"]
        assert r2.json()["questions_answered"] == 0

    def test_new_player_active_with_first_question(
        self, rapid_fire_client: TestClient
    ) -> None:
        r = rapid_fire_client.post("/games/rapid-fire/play")
        assert r.status_code == 200
        body = r.json()
        assert_no_correct_option_index_in_payload(body)
        assert body["status"] == "active"
        assert body["game_session_id"]
        assert body["questions_answered"] == 0
        assert body["questions_total"] == 3
        assert body["question"] is not None
        assert body.get("result") is None

    def test_mid_game_resume_returns_unasked_question(
        self, rapid_fire_client: TestClient, auth_player: CurrentPlayer
    ) -> None:
        container = rapid_fire_client.app.state.container
        sid = "sess-mid"
        now = utc_now()
        container.game_session_dao._sessions = [
            GameSessionDTO(
                id=sid,
                player_id=auth_player.id,
                game_id="rapid_fire",
                status=GameSessionStatus.ACTIVE,
                score=None,
                started_at=now,
                completed_at=None,
            )
        ]
        container.rapid_fire_answer_dao._answers = [
            RapidFireAnswerDTO(
                id="ans-1",
                game_session_id=sid,
                question_id="rf-q1",
                correct=True,
                skipped=False,
                selected_option=1,
                time_ms=500,
                answered_at=now,
            )
        ]

        r = rapid_fire_client.post("/games/rapid-fire/play")
        assert r.status_code == 200
        body = r.json()
        assert_no_correct_option_index_in_payload(body)
        assert body["status"] == "active"
        assert body["questions_answered"] == 1
        assert body["question"] is not None
        assert body["question"]["id"] != "rf-q1"
        assert body["question"]["id"] in ("rf-q2", "rf-q3")

    def test_completed_session_returns_result_without_question(
        self, rapid_fire_client: TestClient, auth_player: CurrentPlayer
    ) -> None:
        container = rapid_fire_client.app.state.container
        done_at = utc_now()
        started = done_at - timedelta(minutes=1)
        sid = "sess-done"
        container.game_session_dao._sessions = [
            GameSessionDTO(
                id=sid,
                player_id=auth_player.id,
                game_id="rapid_fire",
                status=GameSessionStatus.COMPLETED,
                score=100,
                started_at=started,
                completed_at=done_at,
            )
        ]
        container.rapid_fire_answer_dao._answers = [
            RapidFireAnswerDTO(
                id="a1",
                game_session_id=sid,
                question_id="rf-q1",
                correct=True,
                skipped=False,
                selected_option=1,
                time_ms=500,
                answered_at=started,
            ),
        ]

        r = rapid_fire_client.post("/games/rapid-fire/play")
        assert r.status_code == 200
        body = r.json()
        assert_no_correct_option_index_in_payload(body)
        assert body["status"] == "completed"
        assert body["result"] is not None
        assert body["result"]["score"] == 100
        assert body.get("question") is None

    def test_abandoned_session_returns_result_without_question(
        self, rapid_fire_client: TestClient, auth_player: CurrentPlayer
    ) -> None:
        container = rapid_fire_client.app.state.container
        done_at = utc_now()
        started = done_at - timedelta(minutes=1)
        sid = "sess-left"
        container.game_session_dao._sessions = [
            GameSessionDTO(
                id=sid,
                player_id=auth_player.id,
                game_id="rapid_fire",
                status=GameSessionStatus.ABANDONED,
                score=5,
                started_at=started,
                completed_at=done_at,
            )
        ]
        container.rapid_fire_answer_dao._answers = []

        r = rapid_fire_client.post("/games/rapid-fire/play")
        assert r.status_code == 200
        body = r.json()
        assert_no_correct_option_index_in_payload(body)
        assert body["status"] == "abandoned"
        assert body["result"] is not None
        assert body["result"]["score"] == 5
        assert body.get("question") is None
