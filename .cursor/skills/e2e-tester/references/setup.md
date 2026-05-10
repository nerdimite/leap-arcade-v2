# E2E Folder Setup Guide

Interactive guide for scaffolding an `e2e/` test folder in a new or existing project. Follows the opinionated structure from the main SKILL.md.

## Before You Begin

Gather answers to these questions from the user (use AskQuestion when available):

### Required Questions

1. **Package manager**: What package manager does the project use?
   - Options: `uv`, `pip`, `poetry`, `pdm`, other (free-form)
   - Affects: dependency installation commands in docs

2. **Auth provider**: What auth provider does the project use?
   - Options: `Clerk` (default), `Auth0`, `Supabase Auth`, `Firebase Auth`, `Custom JWT`, other (free-form)
   - Affects: `auth.py` implementation, token generation flow

3. **API base path**: What is the API prefix?
   - Options: `/api/v1` (default), `/v1`, `/api`, other (free-form)
   - Affects: client wrapper default paths

4. **Multi-tenancy model**: How does the app isolate tenant data?
   - Options: `org-based` (default — separate orgs with ABAC), `user-based` (each user is isolated), `none`, other (free-form)
   - Affects: persona configuration, ABAC test class generation

5. **Existing test directory**: Does a `tests/` directory already exist?
   - Options: `yes`, `no`, other (free-form — e.g. custom path like `test/` or `spec/`)
   - Affects: whether to create `tests/` or just `tests/e2e/`

### Optional Questions (propose defaults)

6. **Number of orgs**: How many test organizations? Default: 2
7. **Roles per org**: What roles exist? Default: `admin`, `member`
8. **Personas per org**: How many users per org? Default: 2 (one per role)
9. **Custom cleanup**: Does the project need custom teardown logic (e.g., FHIR reset, DB truncation)?
   - Default: basic teardown stub

## Scaffolding Checklist

After gathering answers, create files in this order:

```
Task Progress:
- [ ] Step 1: Install dependencies
- [ ] Step 2: Create .env.test
- [ ] Step 3: Create config/personas.json
- [ ] Step 4: Create state.py
- [ ] Step 5: Create clients/api_client.py
- [ ] Step 6: Create auth.py
- [ ] Step 7: Create setup.py
- [ ] Step 8: Create teardown.py
- [ ] Step 9: Create conftest.py
- [ ] Step 10: Create scenarios/test_smoke.py
- [ ] Step 11: Add pytest markers and config
```

---

## Step 1: Install Dependencies

```bash
# Using uv (recommended)
uv add --dev pytest pytest-asyncio httpx python-dotenv pydantic

# Using pip
pip install pytest pytest-asyncio httpx python-dotenv pydantic
```

If using Clerk as auth provider:
```bash
uv add --dev clerk-backend-api  # or the project's existing Clerk client
```

## Step 2: Create .env.test

```env
E2E_API_BASE_URL=http://localhost:8080

# Auth provider credentials (Clerk example)
CLERK_SECRET_KEY=sk_test_...

# If your app uses an internal admin token for setup/teardown
INTERNAL_ADMIN_TOKEN=...

# JWT template name (Clerk-specific)
CLERK_JWT_TEMPLATE_NAME=api-jwt
```

Add `.env.test` to `.gitignore` if it contains real secrets. For CI, use environment variables directly.

## Step 3: Create config/personas.json

Generate based on user answers. Minimum viable config (2 orgs, 2 roles):

```json
{
  "orgs": [
    { "name": "org_alpha", "slug": "test-org-alpha", "display_name": "Alpha Hospital" },
    { "name": "org_beta",  "slug": "test-org-beta",  "display_name": "Beta Clinic" }
  ],
  "users": [
    {
      "name": "jane",
      "first_name": "Jane",
      "last_name": "Smith",
      "email": "jane@test.example.com",
      "phone": "+15555550100",
      "role": "admin",
      "org": "org_alpha"
    },
    {
      "name": "john",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@test.example.com",
      "phone": "+15555550101",
      "role": "member",
      "org": "org_alpha"
    },
    {
      "name": "alice",
      "first_name": "Alice",
      "last_name": "Brown",
      "email": "alice@test.example.com",
      "phone": "+15555550102",
      "role": "admin",
      "org": "org_beta"
    },
    {
      "name": "bob",
      "first_name": "Bob",
      "last_name": "Carter",
      "email": "bob@test.example.com",
      "phone": "+15555550103",
      "role": "member",
      "org": "org_beta"
    }
  ]
}
```

Adapt field names to match the auth provider's user model. The `name` field is the persona key used in tests (`clients["jane"]`).

## Step 4: Create state.py

In-memory state model holding IDs created during setup. Adapt fields to your auth provider:

```python
"""In-memory state for the E2E test session."""

from typing import Optional
from pydantic import BaseModel, Field


class OrgState(BaseModel):
    name: str = Field(..., description="Internal key (e.g. 'org_alpha')")
    provider_org_id: str = Field(..., description="Auth provider's org ID")
    slug: Optional[str] = Field(default=None)
    display_name: str = Field(...)


class PersonaState(BaseModel):
    name: str = Field(..., description="Persona key (e.g. 'jane')")
    provider_user_id: str = Field(..., description="Auth provider's user ID")
    email: str = Field(...)
    org: str = Field(..., description="Org key this persona belongs to")
    role: str = Field(..., description="App-level role (e.g. 'admin', 'member')")


class TestEnvState(BaseModel):
    orgs: dict[str, OrgState] = Field(default_factory=dict)
    users: dict[str, PersonaState] = Field(default_factory=dict)
```

Add domain-specific fields as needed (e.g., `practitioner_id` for healthcare, `workspace_id` for SaaS).

## Step 5: Create clients/api_client.py

Thin wrapper around `httpx.AsyncClient`. Status codes are NOT auto-raised — tests assert exact codes:

```python
"""Authenticated HTTP client for E2E scenarios."""

from types import TracebackType
from typing import Any, Optional
import httpx


class E2EApiClient:
    def __init__(self, jwt: str, base_url: str) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {jwt}"},
            timeout=30.0,
        )

    async def get(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self._client.get(path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self._client.post(path, **kwargs)

    async def patch(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self._client.patch(path, **kwargs)

    async def put(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self._client.put(path, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> httpx.Response:
        return await self._client.delete(path, **kwargs)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "E2EApiClient":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.aclose()
```

### Customization Points

- **API key auth** instead of JWT: change `Authorization` header format
- **Cookie-based auth**: use `httpx.AsyncClient(cookies=...)` instead
- **Custom headers**: add project-specific headers (e.g., `X-Org-Id`)

## Step 6: Create auth.py

JWT generation varies by auth provider. Implement `generate_tokens(state) -> dict[str, str]`.

### Clerk (default)

```python
"""JWT generation for E2E personas using Clerk."""

import os
from tests.e2e.state import TestEnvState

DEFAULT_JWT_TEMPLATE = "api-jwt"


async def generate_tokens(
    state: TestEnvState,
    template_name: str = DEFAULT_JWT_TEMPLATE,
) -> dict[str, str]:
    """Generate a JWT for each persona by creating/reusing Clerk sessions."""
    from your_app.auth_client import AuthClient  # adapt import

    client = AuthClient(api_key=os.getenv("CLERK_SECRET_KEY"))
    tokens: dict[str, str] = {}

    for persona_name, persona in state.users.items():
        org_state = state.orgs[persona.org]
        session = await client.create_session(
            user_id=persona.provider_user_id,
            active_organization_id=org_state.provider_org_id,
        )
        token = await client.get_session_token(
            session_id=session.id,
            template=template_name,
        )
        tokens[persona_name] = token

    return tokens
```

### Custom JWT (no auth provider SDK)

```python
"""JWT generation using PyJWT for projects with custom auth."""

import jwt
import os
from datetime import datetime, timedelta, timezone
from tests.e2e.state import TestEnvState


async def generate_tokens(state: TestEnvState) -> dict[str, str]:
    secret = os.getenv("JWT_SECRET")
    tokens: dict[str, str] = {}

    for persona_name, persona in state.users.items():
        org = state.orgs[persona.org]
        payload = {
            "sub": persona.provider_user_id,
            "org_id": org.provider_org_id,
            "role": persona.role,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }
        tokens[persona_name] = jwt.encode(payload, secret, algorithm="HS256")

    return tokens
```

## Step 7: Create setup.py

Idempotent creation of orgs and users. Adapt to your auth provider's API:

```python
"""Idempotent E2E environment setup."""

import json
from pathlib import Path
from typing import Any
from tests.e2e.state import OrgState, PersonaState, TestEnvState

CONFIG_PATH = Path(__file__).parent / "config" / "personas.json"


def load_personas_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text())


async def setup_orgs(auth_client, config: dict, state: TestEnvState) -> None:
    """Create orgs that don't already exist. Populate state.orgs."""
    # Adapt: list existing orgs from your auth provider
    existing = await auth_client.list_organizations()
    by_slug = {org.slug: org for org in existing}

    for org_def in config["orgs"]:
        slug = org_def["slug"]
        if slug in by_slug:
            org = by_slug[slug]
        else:
            org = await auth_client.create_organization(
                name=org_def["display_name"], slug=slug
            )
        state.orgs[org_def["name"]] = OrgState(
            name=org_def["name"],
            provider_org_id=org.id,
            slug=org.slug,
            display_name=org_def["display_name"],
        )


async def setup_personas(auth_client, config: dict, state: TestEnvState) -> None:
    """Create users that don't already exist, add to orgs, set roles."""
    for persona in config["users"]:
        user = await auth_client.get_or_create_user(
            email=persona["email"],
            first_name=persona.get("first_name"),
            last_name=persona.get("last_name"),
        )
        org_state = state.orgs[persona["org"]]
        await auth_client.add_user_to_org(
            org_id=org_state.provider_org_id,
            user_id=user.id,
            role=persona["role"],
        )
        state.users[persona["name"]] = PersonaState(
            name=persona["name"],
            provider_user_id=user.id,
            email=persona["email"],
            org=persona["org"],
            role=persona["role"],
        )
```

## Step 8: Create teardown.py

Stub teardown — adapt to your project's cleanup needs:

```python
"""E2E environment teardown. Adapt to your data layer."""


async def teardown_env(config: dict) -> None:
    """Reset test data created during the session."""
    # Examples of what to clean up:
    # - Truncate test DB tables
    # - Delete FHIR resources tagged with test org IDs
    # - Remove objects from S3/blob storage
    # - Call an internal admin reset endpoint
    pass
```

## Step 9: Create conftest.py

Wire the fixture graph together:

```python
"""Session-scoped fixtures for E2E tests."""

import os
from pathlib import Path
from typing import AsyncGenerator

import pytest
from dotenv import load_dotenv

from tests.e2e import auth
from tests.e2e.clients.api_client import E2EApiClient
from tests.e2e.setup import load_personas_config, setup_orgs, setup_personas
from tests.e2e.state import TestEnvState
from tests.e2e.teardown import teardown_env

_env_file = Path(".env.test")
if _env_file.exists():
    load_dotenv(_env_file, override=True)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Auto-apply e2e marker to tests in this package."""
    for item in items:
        if "tests/e2e" in str(item.fspath) or "tests\\e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)


@pytest.fixture(scope="session")
async def env_state() -> AsyncGenerator[TestEnvState, None]:
    config = load_personas_config()
    state = TestEnvState()

    # Adapt: instantiate your auth provider client
    auth_client = ...
    await setup_orgs(auth_client, config, state)
    await setup_personas(auth_client, config, state)

    yield state

    await teardown_env(config)


@pytest.fixture(scope="session")
async def tokens(env_state: TestEnvState) -> dict[str, str]:
    return await auth.generate_tokens(env_state)


@pytest.fixture(scope="session")
async def clients(
    tokens: dict[str, str],
) -> AsyncGenerator[dict[str, E2EApiClient], None]:
    base_url = os.getenv("E2E_API_BASE_URL", "http://localhost:8080")
    api_clients = {
        persona: E2EApiClient(jwt=jwt, base_url=base_url)
        for persona, jwt in tokens.items()
    }
    yield api_clients
    for c in api_clients.values():
        await c.aclose()
```

### Event Loop Gotcha

Session-scoped async fixtures and test methods **must** share the same event loop. Always decorate test classes with:

```python
@pytest.mark.asyncio(loop_scope="session")
```

Without this, `httpx` transports will throw `RuntimeError: Event loop is closed`.

## Step 10: Create scenarios/test_smoke.py

Every project should start with a smoke test that validates server reachability and the auth pipeline:

```python
"""Smoke tests — verify server is up and auth pipeline works."""

import pytest
from tests.e2e.clients.api_client import E2EApiClient


@pytest.mark.asyncio(loop_scope="session")
class TestSmoke:
    async def test_health(self, clients: dict[str, E2EApiClient]) -> None:
        client = next(iter(clients.values()))
        resp = await client.get("/health")  # adapt to your health endpoint
        assert resp.status_code == 200

    @pytest.mark.parametrize("persona", ["jane", "john", "alice", "bob"])
    async def test_auth_accepted(
        self, persona: str, clients: dict[str, E2EApiClient]
    ) -> None:
        """Hit an authenticated endpoint with each persona. 401 = broken infra."""
        resp = await clients[persona].get("/api/v1/...")  # adapt path
        assert resp.status_code != 401, (
            f"Auth failed for {persona} — JWT is broken, fix test infra"
        )
```

## Step 11: Add Pytest Markers

In `pyproject.toml` (or `pytest.ini`):

```toml
[tool.pytest.ini_options]
markers = [
    "e2e: end-to-end tests that require a running server",
]
asyncio_mode = "auto"
```

Run E2E tests separately from unit tests:

```bash
# Run only E2E tests
uv run pytest -m e2e

# Run everything except E2E
uv run pytest -m "not e2e"
```

## CI Integration Notes

- Run E2E tests in a separate CI job after the server is deployed to a staging environment.
- Use `.env.test` values as CI environment variables (never commit secrets).
- Consider adding a `--timeout` flag to avoid hung test sessions blocking CI.
- If using Clerk test mode, use `+clerk_test_` email suffixes to avoid real email delivery.
