"""JWT sign/verify and event-code comparison.

Pure functions; no DB access. The auth boundary of the application.

- ``encode_token(corp_id, display_name)`` — issue a fresh access token.
- ``decode_token(token)`` — verify signature and expiry, return claims dict.
- ``verify_event_code(submitted)`` — constant-time compare against ``EVENT_CODE``.
"""

import secrets
from datetime import timedelta
from typing import Any, Dict

import jwt

from leap.config.settings import get_settings
from leap.core.common.time import utc_now
from leap.core.exceptions import InvalidTokenException


_JWT_ALGORITHM = "HS256"


def encode_token(corp_id: str, display_name: str) -> str:
    """Sign and return a fresh JWT for the given player identity."""
    settings = get_settings()
    now = utc_now()
    payload: Dict[str, Any] = {
        "sub": corp_id,
        "display_name": display_name,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=settings.JWT_EXPIRE_HOURS)).timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=_JWT_ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Verify a JWT and return its claims.

    Raises:
        InvalidTokenException: token is missing required claims, malformed,
            has an invalid signature, or has expired.
    """
    settings = get_settings()
    try:
        payload: Dict[str, Any] = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[_JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise InvalidTokenException("Token has expired")
    except jwt.PyJWTError as exc:
        raise InvalidTokenException(f"Invalid token: {exc}")

    if "sub" not in payload or "display_name" not in payload:
        raise InvalidTokenException("Token missing required claims")
    return payload


def verify_event_code(submitted: str) -> bool:
    """Constant-time compare the submitted event code against ``settings.EVENT_CODE``."""
    settings = get_settings()
    return secrets.compare_digest(submitted, settings.EVENT_CODE)
