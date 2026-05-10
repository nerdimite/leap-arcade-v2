"""
Timezone utilities for consistent datetime handling across the application.
"""

import datetime

import pytz


def utc_now() -> datetime.datetime:
    """
    Get current UTC datetime with timezone awareness.

    Returns:
        datetime.datetime: Current UTC time with timezone info
    """
    return datetime.datetime.now(pytz.UTC)


def local_now(timezone_name: str = "UTC") -> datetime.datetime:
    """
    Get current datetime in specified timezone.

    Args:
        timezone_name (str): Timezone name (e.g., 'US/Eastern', 'Europe/London')

    Returns:
        datetime.datetime: Current time in specified timezone
    """
    tz = pytz.timezone(timezone_name)
    return datetime.datetime.now(tz)


def format_iso(dt: datetime.datetime) -> str:
    """
    Format datetime as ISO 8601 string.

    Args:
        dt (datetime.datetime): Datetime to format

    Returns:
        str: ISO 8601 formatted datetime string
    """
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)

    return dt.isoformat()


def parse_iso(iso_string: str) -> datetime.datetime:
    """
    Parse ISO 8601 datetime string to timezone-aware datetime.

    Args:
        iso_string (str): ISO 8601 formatted datetime string

    Returns:
        datetime.datetime: Parsed datetime with timezone info
    """
    dt = datetime.datetime.fromisoformat(iso_string.replace("Z", "+00:00"))

    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)

    return dt
