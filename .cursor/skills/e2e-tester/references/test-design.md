# E2E Test Design Patterns

Patterns and principles for writing robust, maintainable E2E test scenarios.

## The Three Test Classes

Every feature endpoint should be covered by three test classes in a single `test_<feature>.py` file:

| Class                   | Purpose                                        | Primary persona |
| ----------------------- | ---------------------------------------------- | --------------- |
| `TestFeatureHappy`      | Operations that should succeed                 | `jane` (admin)  |
| `TestFeatureFailure`    | Validation errors, permission denials          | `john` (member) |
| `TestFeatureAbac`       | Cross-org data isolation                       | `alice` / `bob` |

This is not a rigid rule — some features need additional classes (e.g., `TestFeatureEdgeCases`, `TestFeaturePagination`). But the three-class structure is the starting point.

## Happy Path Design

### Principles

- **Test the full CRUD cycle** in order: Create → Read → Update → Read (verify) → Delete (if applicable).
- **Assert response shape**, not just status code. Validate key fields in the response body.
- **Use env_state for ID assertions** when you need to verify returned IDs match expected orgs/users.

### Pattern: Idempotent Creation

Tests that create resources should handle the case where the resource already exists:

```python
async def test_admin_creates_resource(
    self, clients: dict[str, E2EApiClient], env_state: TestEnvState
) -> None:
    get_resp = await clients["jane"].get("/api/v1/resources")
    if get_resp.status_code == 200:
        pytest.skip("Resource already exists — skipping create test")

    resp = await clients["jane"].post("/api/v1/resources", json={...})
    assert resp.status_code == 201
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["id"] is not None
```

### Pattern: Sequential Dependency

When tests depend on prior state (e.g., update depends on create), use test ordering within the same class. pytest runs methods in definition order by default:

```python
class TestFeatureHappy:
    async def test_01_create(self, clients, env_state): ...
    async def test_02_read(self, clients, env_state): ...
    async def test_03_update(self, clients): ...
    async def test_04_delete(self, clients): ...
```

Alternatively, rely on the idempotent guard pattern so each test is self-sufficient.

## Failure Path Design

### What to Test

1. **Missing required fields** → 422 (validation error)
2. **Invalid field values** (wrong type, out of range) → 422
3. **Role-based denial** (member attempting admin action) → 403
4. **Duplicate creation** → 400 or 409
5. **Not found** (valid auth, missing resource) → 404
6. **Invalid JSON body** → 422

### Pattern: Validation Errors

```python
async def test_create_missing_required_field(
    self, clients: dict[str, E2EApiClient]
) -> None:
    resp = await clients["jane"].post("/api/v1/resources", json={})
    assert resp.status_code == 422
```

### Pattern: Role-Based Denial

```python
async def test_member_cannot_create(
    self, clients: dict[str, E2EApiClient]
) -> None:
    """Members lack resources.create permission."""
    resp = await clients["john"].post("/api/v1/resources", json={"name": "Test"})
    assert resp.status_code == 403
```

### Pattern: Descriptive Assertion Messages

Always include context in assertion messages to speed up debugging:

```python
assert resp.status_code == 200, (
    f"Expected 200, got {resp.status_code}: {resp.text}"
)
```

## ABAC / Cross-Org Isolation

This is the most critical test category for multi-tenant systems. The goal: **org_beta personas must never read, modify, or infer the existence of org_alpha resources**.

### What to Test

1. **Cross-org read**: alice reads org_alpha's resources → 403 or 404
2. **Cross-org write**: alice creates/updates org_alpha's resources → server must use JWT's org, not request body
3. **Cross-org list**: alice lists resources → must only see org_beta's data
4. **Identity spoofing**: alice tries to claim org_alpha's ID in the request body → server ignores it

### Pattern: Read Isolation

```python
async def test_cross_org_read_denied(
    self, clients: dict[str, E2EApiClient], env_state: TestEnvState
) -> None:
    """alice (org_beta) must not see org_alpha's resources."""
    resp = await clients["alice"].get("/api/v1/resources")
    if resp.status_code == 200:
        returned_org = resp.json()["data"]["orgId"]
        assert returned_org == env_state.orgs["org_beta"].provider_org_id, (
            "alice received org_alpha's data — cross-org isolation FAILED"
        )
    else:
        assert resp.status_code in (403, 404)
```

### Pattern: Write Isolation

```python
async def test_cross_org_create_uses_jwt_org(
    self, clients: dict[str, E2EApiClient], env_state: TestEnvState
) -> None:
    """Server must use org from JWT, not from request body."""
    resp = await clients["alice"].post(
        "/api/v1/resources", json={"name": "Attempted Hijack"}
    )
    if resp.status_code == 201:
        created_org = resp.json()["data"]["orgId"]
        assert created_org == env_state.orgs["org_beta"].provider_org_id
        assert created_org != env_state.orgs["org_alpha"].provider_org_id
    else:
        assert resp.status_code in (400, 403, 409)
```

## Multi-Effect Endpoint Testing

Endpoints that produce multiple side effects (create parent + child resources, trigger async jobs, fire webhooks) need special attention.

### Principles

1. **Assert each side effect independently** — don't rely on the primary response alone.
2. **Use read endpoints** to verify downstream resources exist.
3. **Test the negative case** — if a side effect is conditional, verify it doesn't happen for unprivileged callers.
4. **Never rely on a downstream test** to catch a missing side effect.

### Example

```python
class TestMultiEffectHappy:
    async def test_admin_create_triggers_child_resource(
        self, clients: dict[str, E2EApiClient]
    ) -> None:
        # Primary action
        resp = await clients["jane"].post("/api/v1/parents", json={...})
        assert resp.status_code == 201
        parent_id = resp.json()["data"]["id"]

        # Verify side effect: child resource was created
        children = await clients["jane"].get(f"/api/v1/parents/{parent_id}/children")
        assert children.status_code == 200
        assert len(children.json()["data"]) >= 1


class TestMultiEffectFailure:
    async def test_member_create_skips_conditional_side_effect(
        self, clients: dict[str, E2EApiClient]
    ) -> None:
        resp = await clients["john"].post(
            "/api/v1/parents", json={..., "auto_create_child": True}
        )
        assert resp.status_code == 201
        parent_id = resp.json()["data"]["id"]

        # Verify side effect did NOT happen (member lacks permission)
        children = await clients["john"].get(f"/api/v1/parents/{parent_id}/children")
        assert children.json()["data"] == []
```

## State Management Strategies

### Strategy 1: Idempotent Guard (preferred)

Check if the resource exists before creating. Skip if it does. No cleanup needed:

```python
get_resp = await clients["jane"].get("/api/v1/resources")
if get_resp.status_code == 200:
    pytest.skip("Resource already exists")
```

**Best for**: resources that are expensive to create and safe to leave around.

### Strategy 2: Create + Delete in Same Test

Create the resource, assert, then delete it:

```python
async def test_create_and_delete(self, clients):
    resp = await clients["jane"].post("/api/v1/resources", json={...})
    assert resp.status_code == 201
    resource_id = resp.json()["data"]["id"]

    # ... assertions ...

    delete_resp = await clients["jane"].delete(f"/api/v1/resources/{resource_id}")
    assert delete_resp.status_code in (200, 204)
```

**Best for**: tests that need a clean state and the resource has a delete endpoint.

### Strategy 3: Session Teardown

Use the `conftest.py` teardown phase to reset state after all tests complete. This is appropriate for batch cleanup (truncate tables, reset FHIR state, etc.).

**Best for**: projects with an internal admin reset endpoint or direct DB access.

### Strategy 4: Fixture-Based Cleanup

Use pytest fixtures with yield for per-class or per-function cleanup:

```python
@pytest.fixture
async def temp_resource(clients):
    resp = await clients["jane"].post("/api/v1/resources", json={...})
    resource_id = resp.json()["data"]["id"]
    yield resource_id
    await clients["jane"].delete(f"/api/v1/resources/{resource_id}")
```

**Best for**: tests that each need an isolated resource instance.

## Fixture Design Principles

### Keep the Chain Shallow

The ideal fixture graph is three levels deep: `env_state → tokens → clients`. Avoid deeply nested fixture chains — they're hard to debug when something breaks.

### Session Scope for Auth

Auth fixtures (state, tokens, clients) should always be session-scoped. Re-creating users and generating JWTs per test is too slow for E2E suites.

### Function Scope for Mutable State

If a fixture creates mutable resources that tests modify, scope it to `function` or `class` so each test gets a clean copy.

### Avoid Fixture Coupling

Fixtures should not depend on test execution order. If `test_update` needs the resource from `test_create`, either:
- Put them in the same class (in-order execution) and use idempotent guards
- Use a shared fixture that creates the resource

## Parametrization

Use `pytest.mark.parametrize` for testing the same behavior across personas or inputs:

```python
@pytest.mark.parametrize("persona", ["jane", "john", "alice", "bob"])
async def test_all_personas_can_read_health(
    self, persona: str, clients: dict[str, E2EApiClient]
) -> None:
    resp = await clients[persona].get("/health")
    assert resp.status_code == 200
```

Useful for:
- Verifying all personas pass auth (smoke tests)
- Testing multiple invalid inputs against a validation endpoint
- Checking pagination with different page sizes

## Assertion Anti-Patterns

### Never assert `!= 401` without context

A 401 means the JWT is broken — this is always a test infrastructure bug, not product behavior. If you see it, fix `auth.py`, don't write a test that expects it.

### Don't assert just the status code

```python
# Bad — passes even if the response body is wrong
assert resp.status_code == 200

# Good — validates both status and shape
assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
data = resp.json()
assert data["success"] is True
assert data["data"]["id"] is not None
```

### Don't over-assert

```python
# Bad — brittle, breaks if any field is added or formatting changes
assert resp.json() == {"success": True, "data": {"id": "123", "name": "Test", ...}}

# Good — assert only the fields that matter for this test
data = resp.json()["data"]
assert data["name"] == "Test"
assert data["id"] is not None
```

## Writing Test Plan Docs

For complex features, write a test plan in `tests/e2e/docs/test_<feature>.md` before coding tests. Structure:

```markdown
# <Feature> E2E Test Plan

## Endpoints Under Test
- POST /api/v1/...
- GET  /api/v1/...
- PATCH /api/v1/...

## Happy Paths
1. Admin creates resource with valid payload → 201
2. Admin reads resource → 200 with correct data
3. Member reads resource → 200 (if permitted)

## Failure Paths
1. Missing required field → 422
2. Member attempts admin action → 403
3. Duplicate creation → 409

## ABAC / Cross-Org
1. alice reads org_alpha resource → 403 or 404
2. alice creates with spoofed org ID → server uses JWT org

## State Dependencies
- Depends on org existing (created in test_organization.py or idempotent guard)

## Open Questions
- Should members be able to list this resource?
```

This doc serves as a contract between the test author and reviewer, and helps the agent understand what tests to generate.
