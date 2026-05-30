"""Auth routes — login and logout."""

from fastapi import APIRouter, Depends

from leap.api.deps import get_container, get_current_player
from leap.api.schema.auth import LoginRequest, LoginResponse
from leap.service.container import ServiceContainer
from leap.types.player import CurrentPlayer

router = APIRouter()


@router.post("/login", response_model=LoginResponse, summary="Player login")
async def login(
    body: LoginRequest,
    container: ServiceContainer = Depends(get_container),
) -> LoginResponse:
    """Authenticate with corp_id + event_code. Returns a signed JWT."""
    result = await container.auth.login(body.corp_id, body.event_code)
    return LoginResponse(
        access_token=result.access_token,
        token_type=result.token_type,
        player=result.player,
    )


@router.post("/logout", status_code=204, summary="Player logout")
async def logout(
    _player: CurrentPlayer = Depends(get_current_player),
) -> None:
    """No-op server-side. Client is responsible for discarding the token."""
    return None
