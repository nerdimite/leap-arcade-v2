from fastapi import APIRouter

router = APIRouter()


@router.get("/challenge", summary="Get Picture Illustration challenge")
async def get_challenge():
    """Returns image refs and hint metadata for the picture game."""
    # TODO: implement
    raise NotImplementedError
