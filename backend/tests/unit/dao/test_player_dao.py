"""Tests for PlayerDAO.get_by_id.

The DAO unit tests are intentionally thin — PlayerDAO wraps SQLAlchemy and its
correct behaviour can only be verified against a real DB. Unit-level tests of
the ORM query logic would just duplicate SQLAlchemy internals.

Real integration tests live in tests/integration/ (not yet scaffolded).
The executor should add those when wiring up the test DB fixture.
"""

import pytest

from leap.dao.player_dao import PlayerDAO

# TODO (executor): add integration tests using a real async session + test DB:
# - get_by_id returns PlayerDTO for a seeded player
# - get_by_id returns None for an unknown corp_id
# - get_by_id is exact match (service normalises before calling DAO)
