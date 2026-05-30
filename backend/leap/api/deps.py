"""FastAPI dependency functions shared across routes.

- ``get_current_player`` — decodes the JWT and returns a ``CurrentPlayer`` value object.
  No DB fetch per request — identity comes from claims (``sub`` + ``display_name``).
- ``get_container`` — returns the application-wide ``ServiceContainer`` from ``app.state``.
"""

import secrets

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer

from leap.config.settings import get_settings
from leap.core.auth import decode_token
from leap.service.container import ServiceContainer
from leap.types.player import CurrentPlayer

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=True)

_admin_api_key_scheme = APIKeyHeader(name="X-Admin-API-Key", auto_error=False)


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


async def require_admin_api_key(api_key: str | None = Depends(_admin_api_key_scheme)) -> None:
    """Guard admin-only routes behind a shared API key sent in ``X-Admin-API-Key``.

    Uses a constant-time comparison to avoid leaking the key via timing. Returns
    401 when the header is missing or does not match ``ADMIN_API_KEY``.
    """
    expected = get_settings().ADMIN_API_KEY
    if not api_key or not secrets.compare_digest(api_key, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin API key",
        )
