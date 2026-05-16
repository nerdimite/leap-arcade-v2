from fastapi import APIRouter, Depends

from leap.api.deps import get_container, get_current_player
from leap.api.schema.leaderboard import LeaderboardEntrySchema, LeaderboardResponse
from leap.service.container import ServiceContainer
from leap.types.player import CurrentPlayer

router = APIRouter()


@router.get("", response_model=LeaderboardResponse, summary="Get leaderboard")
async def get_leaderboard(
    _player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> LeaderboardResponse:
    """Returns ranked player scores across all players (including zero-score rows)."""
    result = await container.leaderboard.get_leaderboard()
    return LeaderboardResponse(
        entries=[
            LeaderboardEntrySchema(
                rank=entry.rank,
                player_id=entry.player_id,
                display_name=entry.display_name,
                total_score=entry.total_score,
                games_completed=entry.games_completed,
            )
            for entry in result.entries
        ],
        total_players=result.total_players,
    )
