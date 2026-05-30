"""Wikipedia Speed Run routes."""

from fastapi import APIRouter, Depends

from leap.api.deps import get_container, get_current_player
from leap.api.schema.wiki import (
    WikiNavigateRequestSchema,
    WikiNavigateResponse,
    WikiPlayResponse,
    WikiPlayTerminalResponse,
    wiki_navigate_to_response,
    wiki_play_to_response,
)
from leap.games.wiki.service import WikiSpeedRunService
from leap.service.container import ServiceContainer
from leap.types.player import CurrentPlayer

router = APIRouter()


def _wiki_svc(container: ServiceContainer) -> WikiSpeedRunService:
    return container.wiki_speed_run


@router.post(
    "/play", response_model=WikiPlayResponse, summary="Start or resume Wikipedia Speed Run"
)
async def play(
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> WikiPlayResponse:
    payload = await _wiki_svc(container).play(player.id)
    return wiki_play_to_response(payload)


@router.post(
    "/timeout",
    response_model=WikiPlayResponse,
    summary="Server-authoritative puzzle timeout / timer correction",
)
async def wiki_timeout(
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> WikiPlayResponse:
    payload = await _wiki_svc(container).timeout(player.id)
    return wiki_play_to_response(payload)


@router.post(
    "/navigate",
    response_model=WikiNavigateResponse,
    summary="Record a forward wiki navigation step",
)
async def navigate(
    body: WikiNavigateRequestSchema,
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> WikiNavigateResponse:
    payload = await _wiki_svc(container).navigate(player.id, body.title)
    return wiki_navigate_to_response(payload)


@router.post(
    "/back",
    response_model=WikiNavigateResponse,
    summary="Record an in-game back navigation step (feature-flagged)",
)
async def wiki_back(
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> WikiNavigateResponse:
    payload = await _wiki_svc(container).back(player.id)
    return wiki_navigate_to_response(payload)


@router.post(
    "/abandon",
    response_model=WikiPlayTerminalResponse,
    summary="Abandon Wikipedia Speed Run (navigation guard)",
)
async def wiki_abandon(
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> WikiPlayTerminalResponse:
    payload = await _wiki_svc(container).abandon(player.id)
    return wiki_play_to_response(payload)
