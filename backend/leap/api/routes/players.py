"""Player routes — authenticated player profile utilities."""

from typing import List

from fastapi import APIRouter, Depends

from leap.api.deps import get_container, get_current_player
from leap.api.schema.players import PlayerSessionItem
from leap.service.container import ServiceContainer
from leap.types.player import CurrentPlayer

router = APIRouter()


@router.get(
    "/me/sessions",
    response_model=List[PlayerSessionItem],
    summary="List game sessions for the authenticated player",
)
async def get_my_sessions(
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> List[PlayerSessionItem]:
    """Return `{ game_id, status, score }` for each game this player has a row for.

    Omits games with no session row. ``score`` is always ``null`` while ``status``
    is ``active``.
    """
    rows = await container.player_sessions.list_my_sessions(player)
    return [
        PlayerSessionItem(
            game_id=r.game_id,
            status=r.status.value,
            score=r.score,
        )
        for r in rows
    ]
