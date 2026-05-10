from fastapi import APIRouter

router = APIRouter()


@router.get("/challenge", summary="Get Four Pics One Lie challenge")
async def get_challenge():
    """Returns four image refs and category for the odd-one-out game."""
    # TODO: implement
    raise NotImplementedError
