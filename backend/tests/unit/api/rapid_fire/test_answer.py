"""Subcutaneous tests for ``POST /games/rapid-fire/answer``."""

import asyncio
import random

from fastapi import FastAPI
from fastapi.testclient import TestClient

from leap.api.deps import get_current_player
from leap.api.routes.games import rapid_fire as rapid_fire_routes
from leap.types.player import CurrentPlayer, PlayerDTO
from tests.fakes import make_fake_container
from tests.unit.api.rapid_fire.assertions import assert_no_correct_option_index_in_payload
from tests.unit.api.rapid_fire.conftest import (
    register_service_exception_handler,
    sample_questions,
    warm_rapid_fire_cache,
)


def _correct_option(question_id: str) -> int:
    return {"rf-q1": 1, "rf-q2": 2, "rf-q3": 3}[question_id]


class TestRapidFireAnswer:
    def test_correct_answer_has_positive_score_and_next_question(
        self, rapid_fire_client: TestClient
    ) -> None:
        p = rapid_fire_client.post("/games/rapid-fire/play")
        assert p.status_code == 200
        qid = p.json()["question"]["id"]

        r = rapid_fire_client.post(
            "/games/rapid-fire/answer",
            json={
                "question_id": qid,
                "selected_option": _correct_option(qid),
                "time_ms": 500,
            },
        )
        assert r.status_code == 200
        body = r.json()
        assert_no_correct_option_index_in_payload(body)
        assert body["correct"] is True
        assert body["current_score"] > 0
        assert body["next_question"] is not None
        assert "correct_option" in body

    def test_wrong_answer_zero_score_next_question_and_reveal_fields(
        self, rapid_fire_client: TestClient
    ) -> None:
        p = rapid_fire_client.post("/games/rapid-fire/play")
        assert p.status_code == 200
        qid = p.json()["question"]["id"]
        wrong = 4 if _correct_option(qid) != 4 else 3

        r = rapid_fire_client.post(
            "/games/rapid-fire/answer",
            json={"question_id": qid, "selected_option": wrong, "time_ms": 800},
        )
        assert r.status_code == 200
        body = r.json()
        assert_no_correct_option_index_in_payload(body)
        assert body["correct"] is False
        assert body["current_score"] == 0
        assert body["next_question"] is not None
        assert body["correct_option"] in (1, 2, 3, 4)
        assert body["correct_answer_text"]

    def test_skipped_answer_behaves_like_wrong_for_score(
        self, rapid_fire_client: TestClient
    ) -> None:
        p = rapid_fire_client.post("/games/rapid-fire/play")
        assert p.status_code == 200
        qid = p.json()["question"]["id"]

        r = rapid_fire_client.post(
            "/games/rapid-fire/answer",
            json={"question_id": qid, "selected_option": None, "time_ms": 1000},
        )
        assert r.status_code == 200
        body = r.json()
        assert_no_correct_option_index_in_payload(body)
        assert body["correct"] is False
        assert body["current_score"] == 0
        assert body["next_question"] is not None

    def test_last_question_returns_null_next_and_result(
        self,
        auth_player: CurrentPlayer,
    ) -> None:
        qs = sample_questions()[:2]
        container = make_fake_container(
            players={
                auth_player.id: PlayerDTO(
                    id=auth_player.id,
                    display_name=auth_player.display_name,
                )
            },
            rapid_fire_questions=qs,
        )
        asyncio.run(warm_rapid_fire_cache(container))
        app = FastAPI()
        register_service_exception_handler(app)
        app.state.container = container
        app.include_router(rapid_fire_routes.router, prefix="/games/rapid-fire")

        async def _fake_player() -> CurrentPlayer:
            return auth_player

        app.dependency_overrides[get_current_player] = _fake_player
        try:
            random.seed(0)
            client = TestClient(app)
            p = client.post("/games/rapid-fire/play")
            assert p.status_code == 200
            first_id = p.json()["question"]["id"]
            second_id = next(q.id for q in qs if q.id != first_id)

            r1 = client.post(
                "/games/rapid-fire/answer",
                json={
                    "question_id": first_id,
                    "selected_option": _correct_option(first_id),
                    "time_ms": 500,
                },
            )
            assert r1.status_code == 200
            assert_no_correct_option_index_in_payload(r1.json())
            assert r1.json()["next_question"]["id"] == second_id

            r2 = client.post(
                "/games/rapid-fire/answer",
                json={
                    "question_id": second_id,
                    "selected_option": _correct_option(second_id),
                    "time_ms": 500,
                },
            )
            assert r2.status_code == 200
            body = r2.json()
            assert_no_correct_option_index_in_payload(body)
            assert body["next_question"] is None
            assert body["result"] is not None
            assert body["result"]["score"] == body["current_score"]
        finally:
            app.dependency_overrides.clear()

    def test_replay_same_question_returns_409(self, rapid_fire_client: TestClient) -> None:
        p = rapid_fire_client.post("/games/rapid-fire/play")
        qid = p.json()["question"]["id"]
        r1 = rapid_fire_client.post(
            "/games/rapid-fire/answer",
            json={
                "question_id": qid,
                "selected_option": _correct_option(qid),
                "time_ms": 500,
            },
        )
        assert r1.status_code == 200

        r2 = rapid_fire_client.post(
            "/games/rapid-fire/answer",
            json={
                "question_id": qid,
                "selected_option": _correct_option(qid),
                "time_ms": 500,
            },
        )
        assert r2.status_code == 409

    def test_invalid_selected_option_returns_422(self, rapid_fire_client: TestClient) -> None:
        p = rapid_fire_client.post("/games/rapid-fire/play")
        qid = p.json()["question"]["id"]
        r = rapid_fire_client.post(
            "/games/rapid-fire/answer",
            json={"question_id": qid, "selected_option": 5, "time_ms": 500},
        )
        assert r.status_code == 422

    def test_answer_without_session_returns_404(
        self,
        auth_player: CurrentPlayer,
    ) -> None:
        container = make_fake_container(
            players={
                auth_player.id: PlayerDTO(
                    id=auth_player.id,
                    display_name=auth_player.display_name,
                )
            },
            rapid_fire_questions=sample_questions(),
        )
        asyncio.run(warm_rapid_fire_cache(container))
        container.game_session_dao._sessions = []
        app = FastAPI()
        register_service_exception_handler(app)
        app.state.container = container
        app.include_router(rapid_fire_routes.router, prefix="/games/rapid-fire")

        async def _fake_player() -> CurrentPlayer:
            return auth_player

        app.dependency_overrides[get_current_player] = _fake_player
        try:
            client = TestClient(app)
            r = client.post(
                "/games/rapid-fire/answer",
                json={"question_id": "rf-q1", "selected_option": 1, "time_ms": 500},
            )
            assert r.status_code == 404
        finally:
            app.dependency_overrides.clear()
