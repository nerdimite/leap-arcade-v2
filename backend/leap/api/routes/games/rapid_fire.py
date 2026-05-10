"""Rapid Fire Quiz game routes."""

from fastapi import APIRouter, Depends

from leap.api.deps import get_container, get_current_player
from leap.service.container import ServiceContainer
from leap.types.player import CurrentPlayer

router = APIRouter()


@router.post("/start", summary="Start a Rapid Fire session")
async def start(
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
):
    """Create a new game session and return the first question."""
    raise NotImplementedError


@router.get("/state", summary="Get current Rapid Fire session state")
async def state(
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
):
    """Return the active session state and current question."""
    raise NotImplementedError


@router.post("/answer", summary="Submit an answer")
async def answer(
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
):
    """Record the player's answer and return updated session state."""
    raise NotImplementedError


@router.post("/abandon", summary="Abandon the active session", status_code=204)
async def abandon(
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
):
    """Mark the active session as abandoned."""
    raise NotImplementedError
