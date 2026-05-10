# Auth Dependency Scaffold

## app/api/dependencies/auth.py

```python
from typing import Annotated, Optional

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.dependencies.auth_exceptions import AuthenticationException
from app.config.settings import get_settings
from app.core.abac.types import UserContext
from app.core.context.app_context import get_app_context
from app.types.auth.jwt_claims import (
    JWTOrgClaims,
    JWTOrgMembershipClaims,
    JWTUserClaims,
)

settings = get_settings()
app_context = get_app_context()

bearer_scheme = HTTPBearer(auto_error=False)


async def get_auth_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> UserContext:
    if credentials is None:
        raise AuthenticationException.missing_token()

    token = credentials.credentials

    try:
        jwks_client = app_context._state.get("jwks_client")
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=[settings.JWKS_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise AuthenticationException.expired_token()
    except (jwt.InvalidTokenError, Exception):
        raise AuthenticationException.invalid_token()

    user_data = payload.get("user", {})
    org_data = payload.get("org", {})
    membership_data = payload.get("org_membership", {})

    user_claims = JWTUserClaims(**user_data)
    org_claims = JWTOrgClaims(**org_data)
    membership_claims = JWTOrgMembershipClaims(**membership_data)

    roles = []
    if membership_claims.public_metadata and membership_claims.public_metadata.org_roles:
        roles = membership_claims.public_metadata.org_roles

    return UserContext(
        id=user_claims.id,
        roles=roles,
        user=user_claims,
        org=org_claims,
        org_membership=membership_claims,
    )


CurrentUser = Annotated[UserContext, Depends(get_auth_user)]
```

## app/api/dependencies/auth_exceptions.py

```python
from app.config.errors import ErrorCodes, ErrorHttpStatus, ErrorMessages
from app.service.exceptions import BaseServiceException


class AuthenticationException(BaseServiceException):
    @classmethod
    def unauthorized(cls):
        return cls(
            error_code=ErrorCodes.UNAUTHORIZED,
            message=ErrorMessages.UNAUTHORIZED,
            http_status=ErrorHttpStatus.UNAUTHORIZED,
        )

    @classmethod
    def forbidden(cls):
        return cls(
            error_code=ErrorCodes.FORBIDDEN,
            message=ErrorMessages.FORBIDDEN,
            http_status=ErrorHttpStatus.FORBIDDEN,
        )

    @classmethod
    def invalid_token(cls):
        return cls(
            error_code=ErrorCodes.INVALID_TOKEN,
            message=ErrorMessages.INVALID_TOKEN,
            http_status=ErrorHttpStatus.INVALID_TOKEN,
        )

    @classmethod
    def expired_token(cls):
        return cls(
            error_code=ErrorCodes.EXPIRED_TOKEN,
            message=ErrorMessages.EXPIRED_TOKEN,
            http_status=ErrorHttpStatus.EXPIRED_TOKEN,
        )

    @classmethod
    def missing_token(cls):
        return cls(
            error_code=ErrorCodes.MISSING_TOKEN,
            message=ErrorMessages.MISSING_TOKEN,
            http_status=ErrorHttpStatus.MISSING_TOKEN,
        )
```

## app/types/auth/jwt_claims.py

```python
from typing import Optional

from pydantic import BaseModel, Field


class OrgMembershipPublicMetadata(BaseModel):
    org_roles: list[str] = Field(default_factory=list)
    employee_id: Optional[str] = Field(default=None)


class JWTUserClaims(BaseModel):
    id: str
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default=None)
    image_url: Optional[str] = Field(default=None)


class JWTOrgClaims(BaseModel):
    id: str
    name: Optional[str] = Field(default=None)
    slug: Optional[str] = Field(default=None)


class JWTOrgMembershipClaims(BaseModel):
    role: Optional[str] = Field(default=None)
    public_metadata: Optional[OrgMembershipPublicMetadata] = Field(default=None)
```
