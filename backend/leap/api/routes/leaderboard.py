from fastapi import APIRouter

router = APIRouter()


@router.get("", summary="Get leaderboard")
async def get_leaderboard():
    """Returns ranked player scores across all completed game sessions."""
    # TODO: implement
    raise NotImplementedError
