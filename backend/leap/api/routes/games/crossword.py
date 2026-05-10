from fastapi import APIRouter

router = APIRouter()


@router.get("/puzzle", summary="Get crossword puzzle")
async def get_puzzle():
    """Returns grid and clues for the crossword game."""
    # TODO: implement
    raise NotImplementedError
