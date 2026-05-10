---
name: e2e-tester
description: Scaffold and write E2E tests for API services using pytest. Covers folder setup, persona-based auth, fixture design, happy/failure/ABAC test classes, and state management. Use when setting up E2E tests for a new project, writing new E2E scenario files, or asking how to test API endpoints end-to-end.
---

# E2E Test Generation

Opinionated framework for writing end-to-end tests against live API services. Uses pytest + pytest-asyncio with persona-based authentication and multi-org isolation.

## When to Use This Skill

- **New project**: setting up an `e2e/` test folder from scratch — see [references/setup.md](references/setup.md)
- **New scenario**: writing E2E tests for an API endpoint
- **Test design questions**: how to structure happy/failure/ABAC tests, manage state, design fixtures

## Core Philosophy

1. **Tests hit the real server** — no mocking of HTTP, DB, or auth. Mocks are only for external side-effects (email, SMS, webhooks).
2. **Personas, not raw tokens** — each test operates as a named persona (`jane`, `alice`) with a fixed role and org. Tests read like user stories.
3. **Multi-org isolation is a first-class test category** — every resource endpoint needs cross-org denial tests, not just RBAC checks within a single org.
4. **Session-scoped fixtures** — auth setup runs once per `pytest` invocation. Tests share personas and clients for speed.
5. **Idempotent by default** — tests that create state should guard against re-creation (skip if exists) or clean up after themselves.

## File Layout

```
tests/e2e/
├── conftest.py              # Session fixtures: env_state → tokens → clients
├── config/
│   └── personas.json        # Declarative org + user definitions
├── clients/
│   └── api_client.py        # Authenticated HTTP client wrapper
├── state.py                 # Pydantic models for in-memory test state
├── auth.py                  # JWT generation from auth provider
├── setup.py                 # Idempotent org + user creation
├── teardown.py              # Cleanup (FHIR reset, state wipe, etc.)
├── scenarios/
│   ├── test_smoke.py        # Server reachability + auth pipeline
│   └── test_<feature>.py    # Feature-specific scenarios
└── docs/                    # Optional: test plan docs per feature
    └── test_<feature>.md
```

## Persona Model

Define personas declaratively in `config/personas.json`:

```json
{
  "orgs": [
    {
      "name": "org_alpha",
      "slug": "test-org-alpha",
      "display_name": "Alpha Hospital"
    },
    {
      "name": "org_beta",
      "slug": "test-org-beta",
      "display_name": "Beta Clinic"
    }
  ],
  "users": [
    {
      "name": "jane",
      "role": "admin",
      "org": "org_alpha",
      "email": "jane@test.example.com"
    },
    {
      "name": "john",
      "role": "member",
      "org": "org_alpha",
      "email": "john@test.example.com"
    },
    {
      "name": "alice",
      "role": "admin",
      "org": "org_beta",
      "email": "alice@test.example.com"
    },
    {
      "name": "bob",
      "role": "member",
      "org": "org_beta",
      "email": "bob@test.example.com"
    }
  ]
}
```

**Minimum viable persona set**: 2 orgs x 2 roles = 4 personas. This covers admin vs. member permissions AND cross-org isolation.

| Persona | Role   | Org       | Primary use                        |
| ------- | ------ | --------- | ---------------------------------- |
| jane    | admin  | org_alpha | Happy paths, admin-only operations |
| john    | member | org_alpha | Member paths, permission denials   |
| alice   | admin  | org_beta  | Cross-org ABAC denial tests        |
| bob     | member | org_beta  | Cross-org member denial tests      |

**Rule of thumb:** `jane` = primary happy path actor. `alice` = cross-org attacker.

## Fixture Hierarchy

```
.env.test
    └── env_state (session)       setup orgs + users → in-memory state
            └── tokens (session)  generate JWTs per persona
                    └── clients (session)  build authenticated HTTP clients
```

All three are session-scoped — they run once, not per test.

```python
@pytest.fixture(scope="session")
async def env_state() -> AsyncGenerator[TestEnvState, None]:
    config = load_personas_config()
    state = TestEnvState()
    await setup_orgs(auth_client, config, state)
    await setup_personas(auth_client, config, state)
    yield state
    await teardown(config)

@pytest.fixture(scope="session")
async def tokens(env_state: TestEnvState) -> dict[str, str]:
    return await generate_tokens(env_state)

@pytest.fixture(scope="session")
async def clients(tokens: dict[str, str]) -> AsyncGenerator[dict[str, E2EApiClient], None]:
    base_url = os.getenv("E2E_API_BASE_URL", "http://localhost:8080")
    api_clients = {
        persona: E2EApiClient(jwt=jwt, base_url=base_url)
        for persona, jwt in tokens.items()
    }
    yield api_clients
    for c in api_clients.values():
        await c.aclose()
```

## Scenario File Structure

Every scenario file groups tests into three classes. Always use `@pytest.mark.asyncio(loop_scope="session")`:

```python
import pytest
from tests.e2e.clients.api_client import E2EApiClient

@pytest.mark.asyncio(loop_scope="session")
class TestFeatureHappy:
    """Happy path — things that should succeed."""

    async def test_admin_can_create(self, clients: dict[str, E2EApiClient]) -> None:
        resp = await clients["jane"].post("/api/v1/...", json={...})
        assert resp.status_code == 201
        assert resp.json()["success"] is True


@pytest.mark.asyncio(loop_scope="session")
class TestFeatureFailure:
    """Expected failures — wrong inputs, missing fields, permission denials."""

    async def test_member_cannot_create(self, clients: dict[str, E2EApiClient]) -> None:
        resp = await clients["john"].post("/api/v1/...", json={...})
        assert resp.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
class TestFeatureAbac:
    """Cross-org isolation — alice/bob must never access org_alpha resources."""

    async def test_cross_org_read_denied(self, clients: dict[str, E2EApiClient]) -> None:
        resp = await clients["alice"].get("/api/v1/...")
        assert resp.status_code in (403, 404)
```

## Assertion Semantics

| Status | Meaning                                                    |
| ------ | ---------------------------------------------------------- |
| 200    | Success — resource exists and was returned                 |
| 201    | Resource created                                           |
| 401    | Auth failed — bad or missing JWT (**test infra bug**)      |
| 403    | ABAC/RBAC denied — correct behavior for wrong role/org     |
| 404    | Auth passed, resource not found (expected if no seed data) |
| 422    | Validation error — check request body schema               |

**Key rule:** a 401 always means broken test infrastructure, not product behavior. If you see it, fix the auth setup before writing more tests.

## Multi-Effect Endpoints

When an endpoint has side effects beyond its primary response:

1. **Assert each side effect independently** — not just the HTTP status.
2. **Use read endpoints to verify** each downstream resource was created.
3. **Test the negative case** — if a side effect is conditional (e.g., admin-only), verify it does NOT happen for unprivileged callers.

## State Management

Personas are shared across all tests in a session. For tests that mutate state:

- **Idempotent guard**: check if resource exists, `pytest.skip()` if so.
- **Create + delete in same test**: POST then DELETE within one test method.
- **Session teardown**: reset state in `conftest.py` teardown phase.

## References

- **Setting up E2E tests for a new project**: [references/setup.md](references/setup.md)
- **Test design patterns and best practices**: [references/test-design.md](references/test-design.md)
