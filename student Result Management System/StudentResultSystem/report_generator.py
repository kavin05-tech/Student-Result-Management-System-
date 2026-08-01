"""Text report rendering and PDF export service."""
from __future__ import annotations

from pathlib import Path
from typing import Any


class ReportGenerator:
    """Turn controller report data into a readable report card."""

    @staticmethod
    def to_text(data: dict[str, Any]) -> str:
        student = data["student"]
        lines = ["STUDENT RESULT MANAGEMENT SYSTEM", "=" * 58,
                 f"Name: {student['name']}    Roll No: {student['roll_no']}",
                 f"Department: {student['department']}    Semester: {student['semester']}", "",
                 "Code       Subject                     Int  Ext  Total Grade Attendance",
                 "-" * 72]
        for row in data["subjects"]:
            total = "—" if row["total_marks"] is None else f"{row['total_marks']:.1f}"
            internal = "—" if row["internal_marks"] is None else f"{row['internal_marks']:.1f}"
            external = "—" if row["external_marks"] is None else f"{row['external_marks']:.1f}"
            grade = row["grade"] or "—"
            lines.append(f"{row['subject_code']:<10} {row['subject_name'][:26]:<26} {internal:>4} {external:>4} {total:>6} {grade:>5} {row['attendance_percentage']:>8.1f}%")
        lines += ["", "-" * 72, f"Total: {data['total']:.2f}    Average: {data['average']:.2f}",
                  f"GPA: {data['gpa']:.2f}    CGPA: {data['cgpa']:.2f}    Rank: {data['rank']}",
                  f"Result: {data['status']}"]
        return "\n".join(lines)

    def export_pdf(self, data: dict[str, Any], destination: str | Path) -> Path:
        """Export report card to PDF using reportlab when installed."""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfgen import canvas
        except ImportError as error:
            raise RuntimeError("PDF export requires reportlab: pip install reportlab") from error
        path = Path(destination)
        canvas_pdf = canvas.Canvas(str(path), pagesize=A4)
        width, height = A4
        canvas_pdf.setTitle("Student Report Card")
        canvas_pdf.setFont("Helvetica", 10)
        y = height - 45
        for line in self.to_text(data).splitlines():
            if y < 45:
                canvas_pdf.showPage()
                canvas_pdf.setFont("Helvetica", 10)
                y = height - 45
            canvas_pdf.drawString(35, y, line)
            y -= 15
        canvas_pdf.save()
        return path
