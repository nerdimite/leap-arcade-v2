from fastapi import APIRouter

router = APIRouter()


@router.get("/question", summary="Get Rapid Fire question batch")
async def get_questions():
    """Returns the next question(s) for the rapid fire quiz."""
    # TODO: implement
    raise NotImplementedError
