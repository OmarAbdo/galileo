from typing import Any


def flatten(nested: list[Any]) -> list[int]:
    flat: list[int] = []
    for part in nested:
        flat.extend(flatten(part) if isinstance(part, list) else [part])
    return flat


def depth(nested: list[Any]) -> int:
    return 1 + max((depth(part) for part in nested if isinstance(part, list)), default=0)
