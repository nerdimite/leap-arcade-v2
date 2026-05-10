"""Tests for AuthService.login."""

from typing import Dict, Optional

import pytest

from leap.service.auth_service import AuthService
from leap.service.exceptions import InvalidEventCodeException, PlayerNotFoundException
from leap.types.player import PlayerDTO
from tests.fakes import FakeContextManager, FakePlayerDAO


_VALID_PLAYER = PlayerDTO(id="emp001", display_name="Alice Smith")
_EVENT_CODE = "supersecret"


def _make_service(players: Optional[Dict[str, PlayerDTO]] = None) -> AuthService:
    return AuthService(
        context_manager=FakeContextManager(),
        player_dao=FakePlayerDAO(players=players or {"emp001": _VALID_PLAYER}),
    )


class TestAuthServiceLogin:
    @pytest.mark.asyncio
    async def test_returns_jwt_and_player_for_valid_credentials(self, monkeypatch):
        """Happy path: known corp_id + correct event code → LoginResponse with token."""
        monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-long-enough-for-hs256-32b")
        monkeypatch.setenv("JWT_EXPIRE_HOURS", "24")
        monkeypatch.setenv("EVENT_CODE", _EVENT_CODE)
        monkeypatch.setenv("POSTGRES_CONNECTION_STRING", "postgresql+asyncpg://x:x@localhost/x")

        svc = _make_service()
        result = await svc.login("EMP001", _EVENT_CODE)  # uppercase — should be normalised

        assert result.access_token
        assert result.token_type == "bearer"
        assert result.player.id == "emp001"
        assert result.player.display_name == "Alice Smith"

    @pytest.mark.asyncio
    async def test_normalises_corp_id_to_lowercase(self, monkeypatch):
        """corp_id lookup is case-insensitive — normalised before DB query."""
        monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-long-enough-for-hs256-32b")
        monkeypatch.setenv("JWT_EXPIRE_HOURS", "24")
        monkeypatch.setenv("EVENT_CODE", _EVENT_CODE)
        monkeypatch.setenv("POSTGRES_CONNECTION_STRING", "postgresql+asyncpg://x:x@localhost/x")

        svc = _make_service()
        result = await svc.login("EMP001", _EVENT_CODE)
        assert result.player.id == "emp001"

    @pytest.mark.asyncio
    async def test_raises_player_not_found_for_unknown_corp_id(self, monkeypatch):
        """Unknown corp_id → PlayerNotFoundException (404)."""
        monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-long-enough-for-hs256-32b")
        monkeypatch.setenv("JWT_EXPIRE_HOURS", "24")
        monkeypatch.setenv("EVENT_CODE", _EVENT_CODE)
        monkeypatch.setenv("POSTGRES_CONNECTION_STRING", "postgresql+asyncpg://x:x@localhost/x")

        svc = _make_service(players={})
        with pytest.raises(PlayerNotFoundException):
            await svc.login("unknown", _EVENT_CODE)

    @pytest.mark.asyncio
    async def test_raises_invalid_event_code_for_wrong_code(self, monkeypatch):
        """Wrong event code → InvalidEventCodeException (401)."""
        monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-long-enough-for-hs256-32b")
        monkeypatch.setenv("JWT_EXPIRE_HOURS", "24")
        monkeypatch.setenv("EVENT_CODE", _EVENT_CODE)
        monkeypatch.setenv("POSTGRES_CONNECTION_STRING", "postgresql+asyncpg://x:x@localhost/x")

        svc = _make_service()
        with pytest.raises(InvalidEventCodeException):
            await svc.login("emp001", "wrongcode")

    @pytest.mark.asyncio
    async def test_raises_player_not_found_before_checking_event_code(self, monkeypatch):
        """Player lookup happens before event code check — 404 not 401 for unknown player."""
        monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-long-enough-for-hs256-32b")
        monkeypatch.setenv("JWT_EXPIRE_HOURS", "24")
        monkeypatch.setenv("EVENT_CODE", _EVENT_CODE)
        monkeypatch.setenv("POSTGRES_CONNECTION_STRING", "postgresql+asyncpg://x:x@localhost/x")

        svc = _make_service(players={})
        with pytest.raises(PlayerNotFoundException):
            await svc.login("ghost", "wrongcode")

# TODO (executor): add edge case tests for:
# - corp_id with leading/trailing whitespace (should be stripped + normalised)
# - corp_id that is empty string after normalisation (should raise PlayerNotFoundException)
# - event_code that is empty string (should raise InvalidEventCodeException)
