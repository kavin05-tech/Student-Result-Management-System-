"""Manual bubble-sort implementation."""
from typing import Any, Callable


def bubble_sort(
    records: list[dict[str, Any]], key: str | Callable[[dict[str, Any]], Any], reverse: bool = False
) -> list[dict[str, Any]]:
    """Return a bubble-sorted copy of records without using ``sorted``."""
    items = records[:]
    getter = key if callable(key) else lambda row: row.get(key, 0)
    for end in range(len(items) - 1, 0, -1):
        swapped = False
        for index in range(end):
            left, right = getter(items[index]), getter(items[index + 1])
            should_swap = left < right if reverse else left > right
            if should_swap:
                items[index], items[index + 1] = items[index + 1], items[index]
                swapped = True
        if not swapped:
            break
    return items
