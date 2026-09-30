"""Statistics facade and matplotlib chart generation."""
from __future__ import annotations

from pathlib import Path

from controller import Controller
from utils import ensure_reports_dir


class StatisticsManager:
    """Create dashboard charts from controller-calculated statistics."""

    def __init__(self, controller: Controller) -> None:
        self.controller = controller

    def generate_charts(self, output_dir: Path | None = None) -> list[Path]:
        """Save the required matplotlib charts and return their paths."""
        try:
            import matplotlib.pyplot as plt
        except ImportError as error:
            raise RuntimeError("Charts require matplotlib: pip install matplotlib") from error
        output = output_dir or ensure_reports_dir()
        stats, ranks = self.controller.dashboard_statistics(), self.controller.rankings()
        paths: list[Path] = []
        charts = [
            ("marks_distribution.png", "Marks Distribution", [row["average"] for row in ranks], "Average Mark"),
            ("cgpa_distribution.png", "CGPA Distribution", [row["cgpa"] for row in ranks], "CGPA"),
        ]
        for filename, title, values, label in charts:
            fig, axis = plt.subplots(figsize=(7, 4)); axis.hist(values, bins=10, color="#357ABD", edgecolor="white")
            axis.set(title=title, xlabel=label, ylabel="Students"); fig.tight_layout()
            path = output / filename; fig.savefig(path, dpi=150); plt.close(fig); paths.append(path)
        department = stats["departments"]
        fig, axis = plt.subplots(figsize=(7, 4)); axis.bar([x["department"] for x in department], [x["average"] for x in department], color="#4A9C6D")
        axis.set(title="Department-wise Performance", ylabel="Average Mark"); fig.tight_layout()
        path = output / "department_performance.png"; fig.savefig(path, dpi=150); plt.close(fig); paths.append(path)
        top = ranks[:10]
        fig, axis = plt.subplots(figsize=(8, 4)); axis.bar([x["roll_no"] for x in top], [x["average"] for x in top], color="#2C6EAA")
        axis.set(title="Top Students", ylabel="Average Mark"); fig.tight_layout()
        path = output / "top_students.png"; fig.savefig(path, dpi=150); plt.close(fig); paths.append(path)
        return paths
