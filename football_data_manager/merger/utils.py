from datetime import UTC, datetime, timedelta


def is_updated_within(entity, hours: int = 6) -> bool:
    """
    Check if the entity was updated within the given number of hours.

    :param entity: Entity with an ``updated_at`` attribute (naive UTC datetime)
    :param hours: Number of hours to look back from now
    :returns: True if ``updated_at`` is within the window, False otherwise
    """
    updated_at = getattr(entity, "updated_at", None)
    if updated_at is None:
        return False
    threshold = datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=hours)
    return updated_at > threshold
