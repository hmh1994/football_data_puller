from datetime import datetime, UTC
from enum import Enum
from zoneinfo import ZoneInfo

from football_data_manager.common.utils.constants import BST, KST, CET, WET, UTC_ZONE


class TimeZone(Enum):
    BST = BST
    KST = KST
    CET = CET
    WET = WET
    UTC = UTC


def create_utc_datetime(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
    microsecond: int = 0,
    timezone: TimeZone = TimeZone.UTC,
) -> datetime:
    """
    Create a UTC datetime object from the given parameters.
    :param year: The year.
    :param month: The month (1-12).
    :param day: The day of the month (1-31).
    :param hour: The hour (0-23).
    :param minute: The minute (0-59).
    :param second: The second (0-59).
    :param microsecond: The microsecond (0-999999).
    :param timezone: The time zone to convert to.
    :return: A datetime object in the given time zone.
    """
    return (
        datetime(
            year, month, day, hour, minute, second, microsecond, tzinfo=timezone.value
        )
        .astimezone(UTC)
        .replace(tzinfo=None)
    )


def create_utc_now() -> datetime:
    """
    Create a UTC datetime object for the current time.
    :return: A datetime object in UTC.
    """
    return datetime.now(UTC).replace(tzinfo=None)


def create_utc_from_string(timestamp: str, timezone_abbr: str) -> datetime:
    """
    Convert kickoff time string to UTC datetime using timezone abbreviation.

    Handles common timezone abbreviations used in football match data,
    particularly from PulseLive API responses. Supports UK and European
    timezone abbreviations with proper conversion to UTC.

    :param timestamp: Kickoff time string in ISO format (e.g., "2024-08-16 20:00:00")
    :param timezone_abbr: Timezone abbreviation (e.g., 'BST', 'GMT', 'CET')
    :returns: Datetime object converted to UTC
    :raises ValueError: If timezone abbreviation is not recognized

    Example:
        >>> create_utc_from_string("2024-08-16 20:00:00", "BST")
        datetime.datetime(2024, 8, 16, 19, 0)
    """
    # Parse the kickoff time (handle both with and without timezone suffix)
    timestamp_clean = timestamp.replace("Z", "+00:00")
    timestamp_dt = datetime.fromisoformat(timestamp_clean)

    # Map timezone abbreviations to ZoneInfo objects
    timezone_mapping = {
        "BST": BST,  # British Summer Time (UTC+1)
        "GMT": UTC_ZONE,  # Greenwich Mean Time (UTC+0)
        "UTC": UTC_ZONE,  # Coordinated Universal Time
        "CET": CET,  # Central European Time (UTC+1)
        "CEST": CET,  # Central European Summer Time (UTC+2, handled by Europe/Paris)
        "WET": WET,  # Western European Time (UTC+0)
        "WEST": WET,  # Western European Summer Time (UTC+1, handled by Europe/Lisbon)
    }

    # Get the timezone object
    timezone_obj = timezone_mapping.get(timezone_abbr)
    if timezone_obj is None:
        raise ValueError(f"Unsupported timezone abbreviation: {timezone_abbr}")

    # If the datetime doesn't have timezone info, assume it's in the local timezone
    if timestamp_dt.tzinfo is None:
        timestamp_dt = timestamp_dt.replace(tzinfo=timezone_obj)

    # Convert to UTC and return without timezone info (naive datetime in UTC)
    return timestamp_dt.astimezone(UTC_ZONE).replace(tzinfo=None)


def parse_timezone_abbreviation(timezone_abbr: str) -> ZoneInfo:
    """
    Parse timezone abbreviation to ZoneInfo object.

    Provides a mapping from common timezone abbreviations to their
    corresponding ZoneInfo objects for accurate timezone handling.

    :param timezone_abbr: Timezone abbreviation string
    :returns: ZoneInfo object for the timezone
    :raises ValueError: If timezone abbreviation is not supported

    Example:
        >>> parse_timezone_abbreviation("BST")
        ZoneInfo(key='Europe/London')
    """
    timezone_mapping = {
        "BST": BST,  # British Summer Time
        "GMT": UTC_ZONE,  # Greenwich Mean Time
        "UTC": UTC_ZONE,  # Coordinated Universal Time
        "CET": CET,  # Central European Time
        "CEST": CET,  # Central European Summer Time
        "WET": WET,  # Western European Time
        "WEST": WET,  # Western European Summer Time
        "KST": KST,  # Korea Standard Time
    }

    timezone_obj = timezone_mapping.get(timezone_abbr)
    if timezone_obj is None:
        raise ValueError(f"Unsupported timezone abbreviation: {timezone_abbr}")

    return timezone_obj


def parse_date_string_to_utc(date_string: str, date_format: str = "%Y-%m-%d") -> datetime:
    """
    Parse date string to UTC datetime object.
    
    Parses a date string (without time component) and converts it to a UTC datetime
    object with time set to midnight UTC. Commonly used for birth dates and other
    date-only fields that need to be stored as datetime objects.
    
    :param date_string: Date string to parse (e.g., "1995-09-15")
    :param date_format: Date format string (default: "%Y-%m-%d")
    :returns: Naive datetime object in UTC (midnight)
    
    Example:
        >>> parse_date_string_to_utc("1995-09-15")
        datetime.datetime(1995, 9, 15, 0, 0)
    """
    parsed_date = datetime.strptime(date_string, date_format)
    # Replace timezone info with UTC and then make it naive
    return parsed_date.replace(tzinfo=UTC).astimezone(UTC).replace(tzinfo=None)
