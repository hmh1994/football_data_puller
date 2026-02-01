from typing import Any


def convert_float_to_int(value: Any) -> int:
    """
    Convert float to int.
    :param value: Value to convert.
    :return: Converted value.
    """
    if isinstance(value, float):
        return int(value)
    elif isinstance(value, str):
        return int(float(value))
    else:
        return value
