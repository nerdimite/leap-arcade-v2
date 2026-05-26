"""Subcutaneous tests for ``POST /games/four-pics/answer``."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from tests.unit.api.four_pics.assertions import assert_no_odd_one_out_index_in_payload


class TestFourPicsAnswer:
    def _play(self, client: TestClient) -> dict:
        with patch(
            "leap.games.four_pics.service.random.choice",
            lambda seq: sorted(seq, key=lambda q: q.id)[0],
        ):
            r = client.post("/games/four-pics/play")
        assert r.status_code == 200
        return r.json()

    def test_correct_answer_advances(self, four_pics_client: TestClient) -> None:
        play = self._play(four_pics_client)
        question = play["question"]
        assert question is not None

        with patch(
            "leap.games.four_pics.service.random.choice",
            lambda seq: sorted(seq, key=lambda q: q.id)[0],
        ):
            r = four_pics_client.post(
                "/games/four-pics/answer",
                json={
                    "question_id": question["question_id"],
                    "selected_index": 2,
                    "time_ms": 0,
                },
            )

        assert r.status_code == 200
        body = r.json()
        assert_no_odd_one_out_index_in_payload(body)
        assert body["correct"] is True
        assert body["score"] == 150
        assert body["time_bonus"] == 50
        assert body["session_status"] == "active"
        assert body["question"] is not None
        assert body["question"]["question_id"] == "fp-q2"

    def test_wrong_answer_advances_with_zero_score(self, four_pics_client: TestClient) -> None:
        play = self._play(four_pics_client)
        question = play["question"]
        assert question is not None

        with patch(
            "leap.games.four_pics.service.random.choice",
            lambda seq: sorted(seq, key=lambda q: q.id)[0],
        ):
            r = four_pics_client.post(
                "/games/four-pics/answer",
                json={
                    "question_id": question["question_id"],
                    "selected_index": 0,
                    "time_ms": 500,
                },
            )

        assert r.status_code == 200
        body = r.json()
        assert body["correct"] is False
        assert body["score"] == 0
        assert body["time_bonus"] == 0
        assert body["question"] is not None

    def test_rejects_selected_index_out_of_range(self, four_pics_client: TestClient) -> None:
        play = self._play(four_pics_client)
        question = play["question"]
        assert question is not None

        r = four_pics_client.post(
            "/games/four-pics/answer",
            json={
                "question_id": question["question_id"],
                "selected_index": 4,
                "time_ms": 0,
            },
        )
        assert r.status_code == 422

    def test_rejects_replay(self, four_pics_client: TestClient) -> None:
        play = self._play(four_pics_client)
        question = play["question"]
        assert question is not None
        payload = {
            "question_id": question["question_id"],
            "selected_index": 2,
            "time_ms": 0,
        }

        with patch(
            "leap.games.four_pics.service.random.choice",
            lambda seq: sorted(seq, key=lambda q: q.id)[0],
        ):
            first = four_pics_client.post("/games/four-pics/answer", json=payload)
            second = four_pics_client.post("/games/four-pics/answer", json=payload)

        assert first.status_code == 200
        assert second.status_code == 409
