"""Academic-grade and GPA rules."""


def grade_for_mark(mark: float) -> str:
    """Map a percentage to a letter grade."""
    if mark >= 90:
        return "A+"
    if mark >= 80:
        return "A"
    if mark >= 70:
        return "B+"
    if mark >= 60:
        return "B"
    if mark >= 50:
        return "C"
    if mark >= 40:
        return "D"
    return "F"


def grade_points(grade: str) -> float:
    """Return grade points on a 10-point scale."""
    return {"A+": 10, "A": 9, "B+": 8, "B": 7, "C": 6, "D": 5, "F": 0}.get(grade, 0)


def calculate_gpa(mark_rows: list[dict]) -> float:
    """Calculate weighted GPA from subject mark rows."""
    credits = sum(float(row["credits"]) for row in mark_rows)
    if not credits:
        return 0.0
    points = sum(grade_points(row["grade"]) * float(row["credits"]) for row in mark_rows)
    return round(points / credits, 2)
