from fastapi import APIRouter

router = APIRouter()


@router.post("/login", summary="Player login")
async def login():
    """Authenticate a player with corp_id and event_code. Returns JWT."""
    # TODO: implement
    raise NotImplementedError
