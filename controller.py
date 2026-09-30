"""Business logic and orchestration between GUI, algorithms, and database."""
from __future__ import annotations

from typing import Any

from algorithms.binary_search import binary_search_by_roll
from algorithms.bubble_sort import bubble_sort
from algorithms.grading import calculate_gpa, grade_for_mark
from algorithms.linear_search import linear_search
from algorithms.statistics import mean, percentage
from database import DatabaseManager
from models import Student, Subject


class Controller:
    """Application service layer; GUI never issues SQL directly."""

    def __init__(self, database: DatabaseManager) -> None:
        self.db = database

    @staticmethod
    def _require(*values: object) -> None:
        if any(str(value).strip() == "" for value in values):
            raise ValueError("All required fields must be completed.")

    def add_student(self, student: Student) -> int:
        self._require(student.roll_no, student.name, student.department, student.semester)
        return self.db.execute("INSERT INTO students(roll_no,name,department,semester,email,phone) VALUES(?,?,?,?,?,?)",
                               (student.roll_no, student.name, student.department, student.semester, student.email, student.phone))

    def update_student(self, student_id: int, student: Student) -> None:
        self._require(student.roll_no, student.name, student.department, student.semester)
        self.db.execute("UPDATE students SET roll_no=?,name=?,department=?,semester=?,email=?,phone=? WHERE student_id=?",
                        (student.roll_no, student.name, student.department, student.semester, student.email, student.phone, student_id))

    def delete_student(self, student_id: int) -> None:
        self.db.execute("DELETE FROM students WHERE student_id=?", (student_id,))

    def students(self) -> list[dict[str, Any]]:
        return self.db.fetch_all("SELECT * FROM students")

    def add_subject(self, subject: Subject) -> int:
        self._require(subject.subject_code, subject.subject_name, subject.credits)
        return self.db.execute("INSERT INTO subjects(subject_code,subject_name,credits) VALUES(?,?,?)",
                               (subject.subject_code, subject.subject_name, subject.credits))

    def update_subject(self, subject_id: int, subject: Subject) -> None:
        self.db.execute("UPDATE subjects SET subject_code=?,subject_name=?,credits=? WHERE subject_id=?",
                        (subject.subject_code, subject.subject_name, subject.credits, subject_id))

    def delete_subject(self, subject_id: int) -> None:
        self.db.execute("DELETE FROM subjects WHERE subject_id=?", (subject_id,))

    def subjects(self) -> list[dict[str, Any]]:
        return self.db.fetch_all("SELECT * FROM subjects")

    def assign_subject(self, student_id: int, subject_id: int) -> None:
        self.db.execute("INSERT OR IGNORE INTO student_subjects(student_id,subject_id) VALUES(?,?)", (student_id, subject_id))

    def record_mark(self, student_id: int, subject_id: int, internal: float, external: float, attendance: float) -> None:
        if not all(0 <= value <= 100 for value in (internal, external, attendance)):
            raise ValueError("Marks and attendance must be between 0 and 100.")
        self.assign_subject(student_id, subject_id)
        total = round((internal + external) / 2, 2)
        self.db.execute("""INSERT INTO marks(student_id,subject_id,internal_marks,external_marks,total_marks,grade)
            VALUES(?,?,?,?,?,?) ON CONFLICT(student_id,subject_id) DO UPDATE SET
            internal_marks=excluded.internal_marks, external_marks=excluded.external_marks,
            total_marks=excluded.total_marks, grade=excluded.grade""",
            (student_id, subject_id, internal, external, total, grade_for_mark(total)))
        self.db.execute("""INSERT INTO attendance(student_id,subject_id,attendance_percentage) VALUES(?,?,?)
            ON CONFLICT(student_id,subject_id) DO UPDATE SET attendance_percentage=excluded.attendance_percentage""",
            (student_id, subject_id, attendance))

    def search_students(self, field: str, query: str, binary: bool = False) -> list[dict[str, Any]]:
        records = self.students()
        if binary and field == "roll_no":
            by_roll = bubble_sort(records, lambda row: str(row["roll_no"]).casefold())
            match = binary_search_by_roll(by_roll, query)
            return [match] if match else []
        return linear_search(records, field, query)

    def report_data(self, student_id: int) -> dict[str, Any] | None:
        student = self.db.fetch_one("SELECT * FROM students WHERE student_id=?", (student_id,))
        if not student:
            return None
        rows = self.db.fetch_all("""SELECT s.subject_code,s.subject_name,s.credits,m.internal_marks,m.external_marks,
              m.total_marks,m.grade,COALESCE(a.attendance_percentage,0) attendance_percentage
              FROM student_subjects ss JOIN subjects s ON s.subject_id=ss.subject_id
              LEFT JOIN marks m ON m.student_id=ss.student_id AND m.subject_id=ss.subject_id
              LEFT JOIN attendance a ON a.student_id=ss.student_id AND a.subject_id=ss.subject_id
              WHERE ss.student_id=?""", (student_id,))
        completed = [row for row in rows if row["total_marks"] is not None]
        total, average = sum(row["total_marks"] for row in completed), mean([row["total_marks"] for row in completed])
        gpa = calculate_gpa(completed)
        ranks = self.rankings(student["department"])
        rank_row = next((row for row in ranks if row["student_id"] == student_id), None)
        return {"student": student, "subjects": rows, "total": round(total, 2), "average": average,
                "gpa": gpa, "cgpa": gpa, "rank": rank_row["rank"] if rank_row else "—",
                "status": "PASS" if completed and all(row["grade"] != "F" for row in completed) else "FAIL"}

    def rankings(self, department: str | None = None) -> list[dict[str, Any]]:
        filter_sql, args = (" WHERE s.department=?", (department,)) if department else ("", ())
        records = self.db.fetch_all("""SELECT s.student_id,s.roll_no,s.name,s.department,
            COALESCE(AVG(m.total_marks),0) average, COALESCE(SUM(m.total_marks),0) total_marks
            FROM students s LEFT JOIN marks m ON m.student_id=s.student_id""" + filter_sql + " GROUP BY s.student_id", args)
        ordered = bubble_sort(records, "average", reverse=True)
        for position, row in enumerate(ordered, start=1):
            row["rank"] = position
            row["cgpa"] = round(min(10, row["average"] / 10), 2)
        return ordered

    def dashboard_statistics(self) -> dict[str, Any]:
        ranks = self.rankings()
        values = [row["average"] for row in ranks]
        passed = sum(1 for value in values if value >= 40)
        departments = self.db.fetch_all("SELECT department, AVG(total_marks) average FROM students JOIN marks USING(student_id) GROUP BY department")
        return {"highest": max(values, default=0), "lowest": min(values, default=0), "average": mean(values),
                "pass_percentage": percentage(passed, len(values)), "fail_percentage": percentage(len(values) - passed, len(values)),
                "top_students": ranks[:10], "departments": departments,
                "subject_averages": self.db.fetch_all("SELECT subject_name,AVG(total_marks) average FROM subjects JOIN marks USING(subject_id) GROUP BY subject_id")}
