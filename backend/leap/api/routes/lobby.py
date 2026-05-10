"""Lobby route — exposes the player's status across all games."""

from fastapi import APIRouter, Depends

from leap.api.deps import CurrentPlayer, get_container, get_current_player
from leap.api.schema.lobby import LobbyResponse
from leap.service.container import ServiceContainer

router = APIRouter()


@router.get("", response_model=LobbyResponse, summary="Get lobby state for the authenticated player")
async def get_lobby(
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> LobbyResponse:
    """Return the player profile and per-game play status."""
    return await container.lobby.get_lobby(player)
