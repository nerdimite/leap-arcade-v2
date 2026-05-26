"""Subcutaneous tests for ``POST /games/four-pics/play``."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from tests.unit.api.four_pics.assertions import assert_no_odd_one_out_index_in_payload


class TestFourPicsPlay:
    def test_new_player_returns_active_question(self, four_pics_client: TestClient) -> None:
        with patch(
            "leap.games.four_pics.service.random.choice",
            lambda seq: sorted(seq, key=lambda q: q.id)[0],
        ):
            r = four_pics_client.post("/games/four-pics/play")

        assert r.status_code == 200
        body = r.json()
        assert_no_odd_one_out_index_in_payload(body)
        assert body["session_status"] == "active"
        assert body["session_score"] == 0
        assert body["question"] is not None
        assert body["question"]["question_id"] == "fp-q1"
        assert body.get("result") is None

    def test_second_play_returns_same_active_question(self, four_pics_client: TestClient) -> None:
        with patch(
            "leap.games.four_pics.service.random.choice",
            lambda seq: sorted(seq, key=lambda q: q.id)[0],
        ):
            r1 = four_pics_client.post("/games/four-pics/play")
            r2 = four_pics_client.post("/games/four-pics/play")

        assert r1.status_code == 200
        assert r2.status_code == 200
        q1 = r1.json()["question"]
        q2 = r2.json()["question"]
        assert q1["question_id"] == q2["question_id"]
        assert q1["started_at"] == q2["started_at"]
