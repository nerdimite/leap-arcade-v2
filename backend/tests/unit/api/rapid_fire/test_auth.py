"""JWT requirement for Rapid Fire routes (no ``get_current_player`` override)."""

import asyncio

from fastapi import FastAPI
from fastapi.testclient import TestClient

from leap.api.routes.games import rapid_fire as rapid_fire_routes
from leap.types.player import PlayerDTO

from tests.fakes import make_fake_container
from tests.unit.api.rapid_fire.conftest import (
    register_service_exception_handler,
    sample_questions,
    warm_rapid_fire_cache,
)


class TestRapidFireUnauthorized:
    def test_play_without_token_returns_401(self) -> None:
        container = make_fake_container(
            players={"emp001": PlayerDTO(id="emp001", display_name="X")},
            rapid_fire_questions=sample_questions(),
        )
        asyncio.run(warm_rapid_fire_cache(container))
        app = FastAPI()
        register_service_exception_handler(app)
        app.state.container = container
        app.include_router(rapid_fire_routes.router, prefix="/games/rapid-fire")
        try:
            client = TestClient(app)
            r = client.post("/games/rapid-fire/play")
            assert r.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_answer_without_token_returns_401(self) -> None:
        container = make_fake_container(
            players={"emp001": PlayerDTO(id="emp001", display_name="X")},
            rapid_fire_questions=sample_questions(),
        )
        asyncio.run(warm_rapid_fire_cache(container))
        app = FastAPI()
        register_service_exception_handler(app)
        app.state.container = container
        app.include_router(rapid_fire_routes.router, prefix="/games/rapid-fire")
        try:
            client = TestClient(app)
            r = client.post(
                "/games/rapid-fire/answer",
                json={"question_id": "rf-q1", "selected_option": 1, "time_ms": 500},
            )
            assert r.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_abandon_without_token_returns_401(self) -> None:
        container = make_fake_container(
            players={"emp001": PlayerDTO(id="emp001", display_name="X")},
            rapid_fire_questions=sample_questions(),
        )
        asyncio.run(warm_rapid_fire_cache(container))
        app = FastAPI()
        register_service_exception_handler(app)
        app.state.container = container
        app.include_router(rapid_fire_routes.router, prefix="/games/rapid-fire")
        try:
            client = TestClient(app)
            r = client.post("/games/rapid-fire/abandon")
            assert r.status_code == 401
        finally:
            app.dependency_overrides.clear()
