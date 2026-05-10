# Authentication Patterns

## Overview

Authentication uses **Clerk JWT tokens** verified via JWKS. The auth dependency extracts a `UserContext` from the Bearer token and makes it available to the entire request chain.

## Flow

```
Client → Authorization: Bearer <token>
  → HTTPBearer extracts token
  → PyJWKClient fetches signing key from JWKS URL
  → jwt.decode() verifies signature, expiry, issuer
  → Extract claims: user, org, org_membership
  → Build UserContext(id, roles, user, org, org_membership)
```

## JWT Claims Structure

The JWT payload contains custom claims (configured in the auth provider's JWT template):

```python
class JWTUserClaims(BaseModel):
    id: str                    # Auth provider user ID
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    image_url: Optional[str]

class JWTOrgClaims(BaseModel):
    id: str                    # Auth provider org ID
    name: Optional[str]
    slug: Optional[str]

class JWTOrgMembershipClaims(BaseModel):
    role: Optional[str]
    public_metadata: Optional[OrgMembershipPublicMetadata]
    # roles extracted from public_metadata.org_roles
```

## UserContext

The central identity object propagated through the entire request:

```python
class UserContext(BaseModel):
    id: str                    # User ID
    roles: List[str]           # Org roles (e.g., ["admin"])
    user: JWTUserClaims
    org: JWTOrgClaims
    org_membership: Optional[JWTOrgMembershipClaims]
```

Used by ABAC (policy evaluation), services (org scoping), and DAOs (audit fields).

## Auth Dependency

```python
bearer_scheme = HTTPBearer(auto_error=False)

async def get_auth_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> UserContext:
    if credentials is None:
        raise AuthenticationException.missing_token()

    token = credentials.credentials
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(token, signing_key.key, algorithms=[settings.JWKS_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise AuthenticationException.expired_token()
    except jwt.InvalidTokenError:
        raise AuthenticationException.invalid_token()

    # Extract claims and build UserContext
    user_claims = JWTUserClaims(**payload.get("user", {}))
    org_claims = JWTOrgClaims(**payload.get("org", {}))
    membership = JWTOrgMembershipClaims(**payload.get("org_membership", {}))
    roles = membership.public_metadata.org_roles if membership.public_metadata else []

    return UserContext(
        id=user_claims.id,
        roles=roles,
        user=user_claims,
        org=org_claims,
        org_membership=membership,
    )
```

## Convenience Type Alias

```python
CurrentUser = Annotated[UserContext, Depends(get_auth_user)]
```

Use in routes for cleaner signatures:
```python
@router.get("/me")
async def get_profile(user: CurrentUser): ...
```

## Public Endpoints

For endpoints that don't require auth (e.g., health checks, webhook receivers):
- Don't include `Depends(get_service_container)` — it requires auth
- Use separate dependencies or no auth at all

## Internal/Admin Endpoints

For admin-only endpoints (migrations, data resets):
- Use a separate `X-Admin-Token` header, not JWT
- Gate behind `ENVIRONMENT != "prod"`
- Hide from OpenAPI docs: `include_in_schema=False`

## Auth Exception Pattern

```python
class AuthenticationException(BaseServiceException):
    @classmethod
    def unauthorized(cls): ...       # 401
    @classmethod
    def forbidden(cls): ...          # 403
    @classmethod
    def invalid_token(cls): ...      # 401
    @classmethod
    def expired_token(cls): ...      # 401
    @classmethod
    def missing_token(cls): ...      # 401
```

Factory classmethods pull codes/messages from `ErrorCodes`/`ErrorMessages`.
