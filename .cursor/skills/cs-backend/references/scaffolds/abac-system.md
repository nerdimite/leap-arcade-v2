# ABAC System Scaffold

## app/core/abac/__init__.py

```python
from .guard import AccessControlGuard
from .providers import JSONPolicyProvider
from .types import ABACAction, UserContext

__all__ = ["AccessControlGuard", "JSONPolicyProvider", "ABACAction", "UserContext"]
```

## app/core/abac/types.py

```python
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.types.auth.jwt_claims import (
    JWTOrgClaims,
    JWTOrgMembershipClaims,
    JWTUserClaims,
)


class ABACAction(str, Enum):
    CREATE = "create"
    READ = "read"
    LIST = "list"
    UPDATE = "update"
    DELETE = "delete"


class UserContext(BaseModel):
    id: str
    roles: List[str] = Field(default_factory=list)
    user: JWTUserClaims
    org: JWTOrgClaims
    org_membership: Optional[JWTOrgMembershipClaims] = Field(default=None)

    def get(self, path: str, default=None):
        """Dot-notation accessor for ABAC variable resolution."""
        parts = path.split(".")
        obj: Any = self
        for part in parts:
            if isinstance(obj, BaseModel):
                obj = getattr(obj, part, None)
            elif isinstance(obj, dict):
                obj = obj.get(part)
            else:
                return default
            if obj is None:
                return default
        return obj
```

## app/core/abac/providers.py

```python
import json
from typing import Any, Dict, List, Optional


class JSONPolicyProvider:
    """Loads and serves ABAC policies from a JSON file."""

    def __init__(self, filepath: str):
        with open(filepath, "r") as f:
            self._policies: Dict[str, Any] = json.load(f)

    def get_rules(
        self, role: str, resource: str, action: str
    ) -> Optional[List[Dict[str, Any]]]:
        role_policies = self._policies.get(role)
        if role_policies is None:
            return None
        resource_policies = role_policies.get(resource)
        if resource_policies is None:
            return None
        return resource_policies.get(action)

    def get_all_policies(self) -> Dict[str, Any]:
        return self._policies
```

## app/core/abac/guard.py

```python
from typing import Any, Dict, List, Optional, Type

from app.core.abac.compiler import ABACCompiler
from app.core.abac.evaluator import ABACEvaluator
from app.core.abac.providers import JSONPolicyProvider
from app.core.abac.types import UserContext
from app.service.exceptions import AuthorizationException


class AccessControlGuard:
    """Single entry point for all authorization checks."""

    def __init__(self, context: UserContext, policy_provider: JSONPolicyProvider):
        self.context = context
        self.policy_provider = policy_provider
        self.compiler = ABACCompiler(context)
        self.evaluator = ABACEvaluator(context)

    def authorize_create(self, resource: str, payload: Dict[str, Any]) -> None:
        """Check if the user can create this resource with the given payload."""
        for role in self.context.roles:
            rules = self.policy_provider.get_rules(role, resource, "create")
            if rules is not None:
                if any(self.evaluator.evaluate(rule, payload) for rule in rules):
                    return
        raise AuthorizationException(
            message=f"Not authorized to create {resource}",
            details={"resource": resource, "action": "create"},
        )

    def get_authorized_filters(
        self, model: Type, action: str
    ) -> Optional[List]:
        """Compile ABAC rules into SQLAlchemy WHERE conditions.

        Returns:
            List of conditions (may be empty = allow all)
            None = access completely denied
        """
        resource = model.__tablename__
        all_conditions = []
        has_any_rule = False

        for role in self.context.roles:
            rules = self.policy_provider.get_rules(role, resource, action)
            if rules is not None:
                has_any_rule = True
                for rule in rules:
                    if not rule:
                        return []  # Empty rule = allow all
                    conditions = self.compiler.compile(model, rule)
                    all_conditions.extend(conditions)

        if not has_any_rule:
            return None

        return all_conditions

    def ensure_access(self, resource: str, action: str) -> None:
        """Simple check — raises if no rules found for any of the user's roles."""
        for role in self.context.roles:
            rules = self.policy_provider.get_rules(role, resource, action)
            if rules is not None:
                return
        raise AuthorizationException(
            message=f"Not authorized: {action} on {resource}",
            details={"resource": resource, "action": action},
        )
```

## app/core/abac/compiler.py

```python
from typing import Any, Dict, List

from sqlalchemy import or_

from app.core.abac.types import UserContext


class ABACCompiler:
    """Compiles JSON ABAC rules into SQLAlchemy WHERE clauses."""

    OPERATORS = {"$eq", "$neq", "$gt", "$gte", "$lt", "$lte", "$in", "$nin", "$null"}
    LOGICAL = {"$or", "$and", "$not"}

    def __init__(self, context: UserContext):
        self.context = context

    def compile(self, model, rule: Dict[str, Any]) -> List:
        conditions = []
        for field, expr in rule.items():
            if field in self.LOGICAL:
                conditions.append(self._compile_logical(model, field, expr))
            elif isinstance(expr, dict):
                for op, value in expr.items():
                    value = self._resolve_value(value)
                    column = getattr(model, field)
                    conditions.append(self._compile_operator(column, op, value))
            else:
                column = getattr(model, field)
                conditions.append(column == self._resolve_value(expr))
        return conditions

    def _compile_operator(self, column, op: str, value):
        if op == "$eq":
            return column == value
        elif op == "$neq":
            return column != value
        elif op == "$gt":
            return column > value
        elif op == "$gte":
            return column >= value
        elif op == "$lt":
            return column < value
        elif op == "$lte":
            return column <= value
        elif op == "$in":
            return column.in_(value)
        elif op == "$nin":
            return ~column.in_(value)
        elif op == "$null":
            return column.is_(None) if value else column.isnot(None)
        raise ValueError(f"Unknown operator: {op}")

    def _compile_logical(self, model, op: str, rules):
        if op == "$or":
            return or_(*[c for r in rules for c in self.compile(model, r)])
        elif op == "$and":
            from sqlalchemy import and_
            return and_(*[c for r in rules for c in self.compile(model, r)])
        raise ValueError(f"Unknown logical operator: {op}")

    def _resolve_value(self, value):
        if isinstance(value, str) and value.startswith("$"):
            path = value[1:]  # Remove $
            return self.context.get(path)
        return value
```

## app/core/abac/evaluator.py

```python
from typing import Any, Dict

from app.core.abac.types import UserContext


class ABACEvaluator:
    """Evaluates ABAC rules against a payload dict (used for CREATE checks)."""

    def __init__(self, context: UserContext):
        self.context = context

    def evaluate(self, rule: Dict[str, Any], payload: Dict[str, Any]) -> bool:
        if not rule:
            return True  # Empty rule = allow

        for field, expr in rule.items():
            if field == "$or":
                if not any(self.evaluate(r, payload) for r in expr):
                    return False
            elif field == "$and":
                if not all(self.evaluate(r, payload) for r in expr):
                    return False
            elif isinstance(expr, dict):
                actual = payload.get(field)
                for op, expected in expr.items():
                    expected = self._resolve_value(expected)
                    if not self._eval_operator(actual, op, expected):
                        return False
            else:
                actual = payload.get(field)
                expected = self._resolve_value(expr)
                if actual != expected:
                    return False
        return True

    def _eval_operator(self, actual, op: str, expected) -> bool:
        if op == "$eq":
            return actual == expected
        elif op == "$neq":
            return actual != expected
        elif op == "$in":
            return actual in expected
        elif op == "$nin":
            return actual not in expected
        elif op == "$gt":
            return actual > expected
        elif op == "$gte":
            return actual >= expected
        elif op == "$lt":
            return actual < expected
        elif op == "$lte":
            return actual <= expected
        elif op == "$null":
            return (actual is None) == expected
        return False

    def _resolve_value(self, value):
        if isinstance(value, str) and value.startswith("$"):
            return self.context.get(value[1:])
        return value
```

## app/config/policies.json

```json
{
  "admin": {
    "items": {
      "create": [{ "org_id": { "$eq": "$org.id" } }],
      "read":   [{ "org_id": { "$eq": "$org.id" } }],
      "list":   [{ "org_id": { "$eq": "$org.id" } }],
      "update": [{ "org_id": { "$eq": "$org.id" } }],
      "delete": [{ "org_id": { "$eq": "$org.id" } }]
    }
  },
  "member": {
    "items": {
      "read": [{ "org_id": { "$eq": "$org.id" } }],
      "list": [{ "org_id": { "$eq": "$org.id" } }]
    }
  }
}
```

## Integration with ContextManager

Add to `ContextManager`:

```python
from app.core.abac.providers import JSONPolicyProvider
from app.config.constants import ABAC_POLICIES_FILEPATH

class ContextManager:
    def __init__(self):
        # ... other providers ...
        self._policy_provider: Optional[JSONPolicyProvider] = None

    def get_policy_provider(self) -> JSONPolicyProvider:
        if self._policy_provider is None:
            self._policy_provider = JSONPolicyProvider(ABAC_POLICIES_FILEPATH)
        return self._policy_provider
```
