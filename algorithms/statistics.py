"""Small statistical helpers with no third-party dependency."""


def mean(values: list[float]) -> float:
    """Return mean, or 0 for no observations."""
    return round(sum(values) / len(values), 2) if values else 0.0


def percentage(part: int, total: int) -> float:
    """Return percentage safely."""
    return round((part / total) * 100, 2) if total else 0.0
