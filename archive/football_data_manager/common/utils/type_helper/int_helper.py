def compare_ints(a: int, b: int) -> int:
    """
    Compare two integers and return:
    - 1 if a > b
    - 0 if a == b
    - -1 if a < b
    """
    return (a > b) - (a < b)
