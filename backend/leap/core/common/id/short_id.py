import hashlib

from .snowflake import SnowflakeIDGenerator

BASE62_CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE62_LENGTH = 62

# Global singleton generator instance
_generator = SnowflakeIDGenerator()


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with an optional prefix.

    Args:
        prefix: The prefix to prepend to the generated ID.

    Returns:
        A unique ID string with the format "{prefix}_{short_id}".
    """
    return prefix + "_" + get_short_id()


def get_short_id() -> str:
    """Generate a short ID using base62 encoding of a snowflake ID.

    Returns:
        A base62-encoded string representation of the snowflake ID.
    """
    global _generator
    return int_to_base62(_generator.generate_id())


def int_to_base62(snowflake_int: int) -> str:
    """Convert a positive integer into a base62 string.

    Args:
        snowflake_int: A non-negative integer to convert to base62.

    Returns:
        A base62-encoded string representation of the input integer.

    Raises:
        AssertionError: If snowflake_int is negative.
    """
    assert snowflake_int >= 0

    if snowflake_int == 0:
        return BASE62_CHARS[0]

    base62_string = []
    while snowflake_int > 0:
        snowflake_int, remainder = divmod(snowflake_int, BASE62_LENGTH)
        base62_string.append(BASE62_CHARS[remainder])
    return "".join(reversed(base62_string))
