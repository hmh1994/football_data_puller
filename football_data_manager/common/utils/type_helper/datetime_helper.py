from datetime import datetime, UTC
from enum import Enum

from football_data_manager.common.utils.constants import BST, KST


class TimeZone(Enum):
    BST = BST
    KST = KST
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
