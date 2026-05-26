"""HTTP-level helpers for Four Pics API tests."""

from typing import Any


def assert_no_odd_one_out_index_in_payload(payload: Any) -> None:
    """``odd_one_out_index`` must never appear in serialized responses."""
    if isinstance(payload, dict):
        assert "odd_one_out_index" not in payload
        for value in payload.values():
            assert_no_odd_one_out_index_in_payload(value)
    elif isinstance(payload, list):
        for item in payload:
            assert_no_odd_one_out_index_in_payload(item)
