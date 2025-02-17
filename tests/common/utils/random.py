from random import choices, randint
from string import ascii_letters, digits

from pydantic import HttpUrl


def random_string(n: int) -> str:
    """
    Create a random string with length n.
    :param n: The length of the string.
    :return: The random string with length n.
    :example:
    >>> random_string(10)
    "fkjndfjndf"
    """
    chars = ascii_letters + digits
    return "".join(choices(chars, k=n))


def random_number(n: int) -> int:
    """
    Create a random number with length n.
    :param n: The length of the number. Must be one or more.
    :return: The random number with length n.
    (10 ** (n - 1) <= number < 10 ** n)
    :raises ValueError: If the length of the number is less than 1.
    :example:
    >>> random_number(10)
    9573498573
    """
    if n < 1:
        raise ValueError("The length of the number must be 1 or more.")
    min_val = pow(10, n - 1) if n > 1 else 1
    max_val = pow(10, n) - 1
    return randint(min_val, max_val)


def random_url(n: int) -> HttpUrl:
    """
    Create a random URL with domain length n.
    :param n: The length of the domain.
    :return: The random URL with domain length n.
    :example:
    >>> random_url(10)
    "https://pknfkxndje.com"
    """
    domain = random_string(n)
    return HttpUrl(f"https://{domain}.com")
