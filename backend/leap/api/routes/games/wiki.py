from fastapi import APIRouter

router = APIRouter()


@router.get("/challenge", summary="Get Wikipedia Speed Run challenge")
async def get_challenge():
    """Returns start/target pages for the wiki game."""
    # TODO: implement
    raise NotImplementedError
