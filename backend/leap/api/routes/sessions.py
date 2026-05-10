from fastapi import APIRouter

router = APIRouter()


@router.post("/{game_id}/start", summary="Start a game session")
async def start_session(game_id: str):
    """Creates a new game session for the authenticated player. 409 if already started."""
    # TODO: implement
    raise NotImplementedError


@router.get("/{game_id}", summary="Rehydrate game session")
async def get_session(game_id: str):
    """Returns the current session state for the authenticated player."""
    # TODO: implement
    raise NotImplementedError
