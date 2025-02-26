from typing import TypeVar, Callable

T = TypeVar("T")
K = TypeVar("K")


def remove_duplicates(entities: T, key: Callable[[T], K]) -> T:
    """
    Remove duplicates from a list of entities based on a key.
    :param entities: An iterable object of entities.
    :param key: A function that returns the key to compare.
    :return: A list containing only the first occurrence of each unique entity.
    :example:
    >>> remove_duplicates([
    ... {"id": 1, "name": "Alice"},
    ... {"id": 2, "name": "Bob"},
    ... {"id": 1, "name": "Alice"}
    ... ], key=lambda x: x["id"])
    [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
    """
    seen_keys = set()
    unique_entities = []
    for entity in entities:
        if (k := key(entity)) not in seen_keys:
            seen_keys.add(k)
            unique_entities.append(entity)
    return unique_entities
