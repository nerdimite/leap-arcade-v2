"""Shared pytest fixtures for FastAPI dependency overrides and fake containers."""

from typing import Callable

import pytest
from fastapi import FastAPI

from leap.api.deps import get_current_player
from leap.types.player import CurrentPlayer
from tests.fakes import FakeServiceContainer, make_fake_container


@pytest.fixture
def auth_player() -> CurrentPlayer:
    """Fixed JWT identity for tests that override ``get_current_player``."""
    return CurrentPlayer(id="emp001", display_name="Test Player")


@pytest.fixture
def auth_override(auth_player: CurrentPlayer) -> Callable[[FastAPI], None]:
    """Return a callable ``(app) -> None`` that registers ``get_current_player`` override.

    The caller should clear ``app.dependency_overrides`` when done (e.g. in a ``finally``
    block) so tests do not leak overrides across cases.
    """

    def _apply(app: FastAPI) -> None:
        async def _fake_player() -> CurrentPlayer:
            return auth_player

        app.dependency_overrides[get_current_player] = _fake_player

    return _apply


@pytest.fixture
def fake_container() -> FakeServiceContainer:
    """Default wired fake stack (all in-memory DAOs)."""
    return make_fake_container()
