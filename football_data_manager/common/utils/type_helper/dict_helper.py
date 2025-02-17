from typing import Any


def lower_keys(target: dict[str, Any]) -> dict[str, Any]:
    """
    Convert all keys in a dictionary to lowercase.
    :param target: The dictionary to convert.
    :return: A new dictionary with lowercase keys.
    :example:
    >>> lower_keys({"Key1": "value1", "Key2": "value2"})
    {'key1': 'value1', 'key2': 'value2'}
    """
    return {k.lower(): v for k, v in target.items()}


def extract_without_key(prefix: str, target: dict[str, Any]) -> dict[str, Any]:
    """
    Extract dictionary elements whose keys start with the given prefix, and return
    a new dictionary where the prefix is removed from the keys.
    :param prefix: The prefix to search for.
    :param target: The dictionary to extract from.
    :return: A dictionary with the same values but without the prefix in the keys.
    :example:
    >>> extract_without_key("prefix", {"prefix_key": "value1", "other_key": "value2"})
    {'key': 'value1'}
    """
    length = len(prefix) + 1
    return {k[length:]: v for k, v in target.items() if k.startswith(f"{prefix}_")}
