from itertools import product


def f(x: str) -> int | None:
    try:
        return int(x)
    except ValueError:
        return None
