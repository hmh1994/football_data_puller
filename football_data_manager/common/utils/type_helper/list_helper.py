from typing import TypeVar, Callable

T = TypeVar("T")
K = TypeVar("K")


def remove_duplicates(entities: list[T], key: Callable[[T], K]) -> list[T]:
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
        if entity is not None and (k := key(entity)) not in seen_keys:
            seen_keys.add(k)
            unique_entities.append(entity)
    return unique_entities


def partition(
    iterable: list[T], predicate: Callable[[T], bool]
) -> tuple[list[T], list[T]]:
    """
    Iterates through an iterable and partitions its elements into two lists based on a predicate function.
    :param iterable: An iterable object containing elements to be partitioned.
    :param predicate: A function that takes an element and returns True or False.
    :return: (first, second) where `first` contains elements for which the predicate is True,
             and `second` contains elements for which the predicate is False.
    """
    first = []
    second = []
    for item in iterable:
        if predicate(item):
            first.append(item)
        else:
            second.append(item)
    return first, second


def find_first(items: list[T], predicate: Callable[[T], bool]) -> T | None:
    """
    Find the first element in `items` for which `predicate` returns True.
    :param items: An iterable of items.
    :param predicate: A function that takes an item and returns True if it matches, False otherwise.
    :returns: The first matching item, or None if no item matches.
    """
    return next(filter(predicate, items), None)
