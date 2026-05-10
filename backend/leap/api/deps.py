"""FastAPI dependency functions shared across routes.

- ``get_current_player`` — decodes the JWT and returns a ``CurrentPlayer`` value object.
  No DB fetch per request — identity comes from claims (``sub`` + ``display_name``).
- ``get_container`` — returns the application-wide ``ServiceContainer`` from ``app.state``.
"""

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer

from leap.core.auth import decode_token
from leap.service.container import ServiceContainer
from leap.types.player import CurrentPlayer

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=True)


async def get_current_player(token: str = Depends(_oauth2_scheme)) -> CurrentPlayer:
    """Decode the bearer token and return the authenticated player.

    Raises:
        InvalidTokenException: token is missing, malformed, or expired.
    """
    claims = decode_token(token)
    return CurrentPlayer(id=claims["sub"], display_name=claims["display_name"])


def get_container(request: Request) -> ServiceContainer:
    """Return the application-wide ``ServiceContainer`` set on ``app.state`` at startup."""
    return request.app.state.container
