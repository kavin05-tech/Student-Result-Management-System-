"""Manual linear-search implementation."""
from typing import Any


def linear_search(records: list[dict[str, Any]], field: str, query: str) -> list[dict[str, Any]]:
    """Return records whose field contains *query*, case-insensitively."""
    needle = query.strip().casefold()
    matches: list[dict[str, Any]] = []
    for record in records:
        if needle in str(record.get(field, "")).casefold():
            matches.append(record)
    return matches
