# ABAC (Attribute-Based Access Control)

## Overview

The ABAC system enforces row-level security through JSON policies. It has 5 components:

| Component | Purpose |
|-----------|---------|
| `types.py` | `UserContext`, `ABACAction` enum, policy type models |
| `providers.py` | `JSONPolicyProvider` — loads `policies.json` |
| `guard.py` | `AccessControlGuard` — orchestrates authorization |
| `compiler.py` | Converts rules → SQLAlchemy WHERE clauses (for READ/LIST) |
| `evaluator.py` | Evaluates rules against dicts in-memory (for CREATE) |

## Policy File Structure

`config/policies.json`:

```json
{
  "admin": {
    "orders": {
      "create": [{ "org_id": { "$eq": "$org.id" } }],
      "read":   [{ "org_id": { "$eq": "$org.id" } }],
      "list":   [{ "org_id": { "$eq": "$org.id" } }],
      "update": [{ "org_id": { "$eq": "$org.id" } }],
      "delete": [{ "org_id": { "$eq": "$org.id" } }]
    }
  },
  "member": {
    "orders": {
      "read": [{ "org_id": { "$eq": "$org.id" } }],
      "list": [{ "org_id": { "$eq": "$org.id" } }]
    }
  }
}
```

**Hierarchy:** `role → resource (plural) → action → [rules]`

### Rule Syntax

| Operator | Meaning | Example |
|----------|---------|---------|
| `$eq` | Equals | `{ "org_id": { "$eq": "$org.id" } }` |
| `$neq` | Not equals | `{ "status": { "$neq": "deleted" } }` |
| `$in` | In list | `{ "role": { "$in": ["admin", "manager"] } }` |
| `$nin` | Not in list | `{ "status": { "$nin": ["archived"] } }` |
| `$gt`, `$gte`, `$lt`, `$lte` | Comparisons | `{ "amount": { "$lt": 1000 } }` |
| `$null` | Is null/not null | `{ "deleted_at": { "$null": true } }` |
| `$or` | Logical OR | `{ "$or": [rule1, rule2] }` |
| `$and` | Logical AND | `{ "$and": [rule1, rule2] }` |

### Context Variables

| Variable | Resolves To |
|----------|-------------|
| `$user.id` | `context.id` (authenticated user ID) |
| `$org.id` | `context.org.id` (active org ID) |
| `$user.email` | `context.user.email` |

## AccessControlGuard

The single entry point for all authorization checks:

```python
class AccessControlGuard:
    def __init__(self, context: UserContext, policy_provider: PolicyProvider):
        self.context = context
        self.policy_provider = policy_provider
        self.compiler = ABACCompiler(context)
        self.evaluator = ABACEvaluator(context)

    def authorize_create(self, resource: str, payload: dict):
        """Evaluate rules against payload. Raises PermissionError if denied."""
        for role in self.context.roles:
            rules = self.policy_provider.get_rules(role, resource, "create")
            if rules is not None and self.evaluator.evaluate(rules, payload):
                return
        raise PermissionError(f"Access denied: create {resource}")

    def get_authorized_filters(self, model, action) -> Optional[list]:
        """Compile rules into SQLAlchemy conditions. Returns None if denied."""
        all_conditions = []
        for role in self.context.roles:
            rules = self.policy_provider.get_rules(role, resource, action)
            if rules is not None:
                conditions = self.compiler.compile(model, rules)
                all_conditions.extend(conditions)
        return all_conditions if all_conditions or has_any_rule else None

    def ensure_access(self, resource: str, action: str):
        """Simple check — raises if no rules found for any role."""
```

## How ABAC Flows

### For CREATE operations:
```
Service → guard.authorize_create("orders", {"org_id": "org_123"})
  → ABACEvaluator checks payload against rules
  → PermissionError if no role grants access
```

### For READ/LIST/UPDATE/DELETE:
```
DAO._apply_abac_filters(query, action="read")
  → guard.get_authorized_filters(Model, "read")
  → ABACCompiler converts rules to SQLAlchemy WHERE conditions
  → query.where(or_(*conditions))
  → Only matching rows are returned
```

## ABACCompiler (SQL)

Converts JSON rules to SQLAlchemy expressions:

- `{ "org_id": { "$eq": "$org.id" } }` → `Model.org_id == "actual_org_id"`
- `{ "$or": [...] }` → `or_(condition1, condition2)`
- Dot notation for relationships: `"schedule.org_id"` → `Model.schedule.has(Schedule.org_id == ...)`

## ABACEvaluator

In-memory rule evaluation for CREATE:

- Same operator set as compiler
- Evaluates against plain Python dicts
- Returns `True` if payload satisfies the rules
- An empty rule `{}` means "allow unconditionally"

## Adding ABAC to a New Resource

1. Add policies to `policies.json` for each role
2. Pass `guard=self.guard` when creating DAOs in the service
3. Call `guard.authorize_create()` explicitly for create operations
4. DAO automatically applies filters for read/list/update/delete
