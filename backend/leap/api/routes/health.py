from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health(request: Request) -> dict:
    """Check API and database health."""
    db_ok = await request.app.state.context_manager.health_check()
    return {
        "status": "ok",
        "db": "ok" if db_ok else "error",
    }
