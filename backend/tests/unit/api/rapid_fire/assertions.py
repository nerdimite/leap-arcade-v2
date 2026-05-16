"""HTTP-level helpers for Rapid Fire API tests."""

from typing import Any


def assert_no_correct_option_index_in_payload(payload: Any) -> None:
    """``correct_option_index`` must never appear in serialized question objects."""
    if isinstance(payload, dict):
        assert "correct_option_index" not in payload
        for v in payload.values():
            assert_no_correct_option_index_in_payload(v)
    elif isinstance(payload, list):
        for item in payload:
            assert_no_correct_option_index_in_payload(item)
