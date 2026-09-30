"""Manual binary-search implementation for roll numbers."""
from typing import Any


def binary_search_by_roll(records: list[dict[str, Any]], roll_no: str) -> dict[str, Any] | None:
    """Find an exact roll number in an ascending roll-number sequence."""
    low, high = 0, len(records) - 1
    target = roll_no.casefold()
    while low <= high:
        middle = (low + high) // 2
        value = str(records[middle]["roll_no"]).casefold()
        if value == target:
            return records[middle]
        if value < target:
            low = middle + 1
        else:
            high = middle - 1
    return None
