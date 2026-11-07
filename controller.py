"""Business logic and SQL-backed orchestration."""
from __future__ import annotations

import csv
import sqlite3
from pathlib import Path
from typing import Any

from algorithms.grading import calculate_gpa, grade_for_mark
from algorithms.statistics import mean, percentage
from database import DatabaseManager
from models import Student, Subject


class Controller:
    """Application service layer; queries and ordering are performed by SQLite."""
    def __init__(self, database: DatabaseManager) -> None:
        self.db = database

    @staticmethod
    def _require(*values: object) -> None:
        if any(str(value).strip() == "" for value in values):
            raise ValueError("All required fields must be completed.")

    def add_student(self, student: Student) -> int:
        self._require(student.roll_no, student.name, student.department, student.semester)
        return self.db.execute("INSERT INTO students(roll_no,name,department,semester,email,phone) VALUES(?,?,?,?,?,?)", (student.roll_no.strip(), student.name.strip(), student.department.strip(), student.semester, student.email, student.phone))

    def update_student(self, student_id: int, student: Student) -> None:
        self._require(student.roll_no, student.name, student.department, student.semester)
        self.db.execute("UPDATE students SET roll_no=?,name=?,department=?,semester=?,email=?,phone=? WHERE student_id=?", (student.roll_no.strip(), student.name.strip(), student.department.strip(), student.semester, student.email, student.phone, student_id))

    def delete_student(self, student_id: int) -> None:
        self.db.execute("DELETE FROM students WHERE student_id=?", (student_id,))

    def students(self) -> list[dict[str, Any]]:
        return self.db.fetch_all("SELECT * FROM students ORDER BY roll_no COLLATE NOCASE")

    def add_subject(self, subject: Subject) -> int:
        self._require(subject.subject_code, subject.subject_name, subject.credits)
        return self.db.execute("INSERT INTO subjects(subject_code,subject_name,credits) VALUES(?,?,?)", (subject.subject_code.strip(), subject.subject_name.strip(), subject.credits))

    def update_subject(self, subject_id: int, subject: Subject) -> None:
        self.db.execute("UPDATE subjects SET subject_code=?,subject_name=?,credits=? WHERE subject_id=?", (subject.subject_code, subject.subject_name, subject.credits, subject_id))

    def delete_subject(self, subject_id: int) -> None:
        self.db.execute("DELETE FROM subjects WHERE subject_id=?", (subject_id,))

    def subjects(self) -> list[dict[str, Any]]:
        return self.db.fetch_all("SELECT * FROM subjects ORDER BY subject_code COLLATE NOCASE")

    def assign_subject(self, student_id: int, subject_id: int) -> None:
        self.db.execute("INSERT OR IGNORE INTO student_subjects(student_id,subject_id) VALUES(?,?)", (student_id, subject_id))

    def record_mark(self, student_id: int, subject_id: int, internal: float, external: float, attendance: float) -> None:
        if not all(0 <= value <= 100 for value in (internal, external, attendance)):
            raise ValueError("Marks and attendance must be between 0 and 100.")
        self.assign_subject(student_id, subject_id)
        total = round((internal + external) / 2, 2)
        self.db.execute("""INSERT INTO marks(student_id,subject_id,internal_marks,external_marks,total_marks,grade) VALUES(?,?,?,?,?,?) ON CONFLICT(student_id,subject_id) DO UPDATE SET internal_marks=excluded.internal_marks,external_marks=excluded.external_marks,total_marks=excluded.total_marks,grade=excluded.grade""", (student_id, subject_id, internal, external, total, grade_for_mark(total)))
        self.db.execute("""INSERT INTO attendance(student_id,subject_id,attendance_percentage) VALUES(?,?,?) ON CONFLICT(student_id,subject_id) DO UPDATE SET attendance_percentage=excluded.attendance_percentage""", (student_id, subject_id, attendance))

    def search_students(self, field: str, query: str) -> list[dict[str, Any]]:
        allowed = {"name", "roll_no", "department"}
        if field not in allowed:
            raise ValueError("Search by name, roll number, or department.")
        return self.db.fetch_all(f"SELECT * FROM students WHERE {field} LIKE ? COLLATE NOCASE ORDER BY roll_no COLLATE NOCASE", (f"%{query.strip()}%",))

    def import_csv(self, source: str | Path, data_type: str) -> int:
        """Import a CSV with one of the documented student, subject, or marks schemas."""
        schemas = {
            "students": {"roll_no", "name", "department", "semester"},
            "subjects": {"subject_code", "subject_name", "credits"},
            "marks": {"roll_no", "subject_code", "internal_marks", "external_marks", "attendance_percentage"},
        }
        if data_type not in schemas:
            raise ValueError("Choose students, subjects, or marks as the CSV type.")
        count = 0
        try:
            with open(source, "r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)
                if not reader.fieldnames or not schemas[data_type].issubset(set(reader.fieldnames)):
                    raise ValueError(f"CSV needs these columns: {', '.join(sorted(schemas[data_type]))}")
                connection = self.db.connection
                with connection:
                    for line, row in enumerate(reader, start=2):
                        try:
                            if data_type == "students":
                                connection.execute("INSERT INTO students(roll_no,name,department,semester,email,phone) VALUES(?,?,?,?,?,?)", (row["roll_no"].strip(), row["name"].strip(), row["department"].strip(), int(row["semester"]), row.get("email", "").strip(), row.get("phone", "").strip()))
                            elif data_type == "subjects":
                                connection.execute("INSERT INTO subjects(subject_code,subject_name,credits) VALUES(?,?,?)", (row["subject_code"].strip(), row["subject_name"].strip(), int(row["credits"])))
                            else:
                                student = connection.execute("SELECT student_id FROM students WHERE roll_no=? COLLATE NOCASE", (row["roll_no"].strip(),)).fetchone()
                                subject = connection.execute("SELECT subject_id FROM subjects WHERE subject_code=? COLLATE NOCASE", (row["subject_code"].strip(),)).fetchone()
                                if not student or not subject:
                                    raise ValueError("roll_no or subject_code was not found")
                                internal, external, attendance = float(row["internal_marks"]), float(row["external_marks"]), float(row["attendance_percentage"])
                                if not all(0 <= value <= 100 for value in (internal, external, attendance)):
                                    raise ValueError("marks and attendance must be between 0 and 100")
                                connection.execute("INSERT OR IGNORE INTO student_subjects(student_id,subject_id) VALUES(?,?)", (student[0], subject[0]))
                                total = round((internal + external) / 2, 2)
                                connection.execute("INSERT INTO marks(student_id,subject_id,internal_marks,external_marks,total_marks,grade) VALUES(?,?,?,?,?,?) ON CONFLICT(student_id,subject_id) DO UPDATE SET internal_marks=excluded.internal_marks,external_marks=excluded.external_marks,total_marks=excluded.total_marks,grade=excluded.grade", (student[0], subject[0], internal, external, total, grade_for_mark(total)))
                                connection.execute("INSERT INTO attendance(student_id,subject_id,attendance_percentage) VALUES(?,?,?) ON CONFLICT(student_id,subject_id) DO UPDATE SET attendance_percentage=excluded.attendance_percentage", (student[0], subject[0], attendance))
                            count += 1
                        except (ValueError, TypeError, sqlite3.IntegrityError) as error:
                            raise ValueError(f"CSV row {line}: {error}") from error
        except UnicodeDecodeError as error:
            raise ValueError("CSV must be saved as UTF-8.") from error
        return count

    def attendance_records(self) -> list[dict[str, Any]]:
        return self.db.fetch_all("""SELECT st.roll_no,st.name,s.subject_code,s.subject_name,a.attendance_percentage
            FROM attendance a JOIN students st ON st.student_id=a.student_id
            JOIN subjects s ON s.subject_id=a.subject_id
            ORDER BY st.roll_no COLLATE NOCASE,s.subject_code COLLATE NOCASE""")
    def report_data(self, student_id: int) -> dict[str, Any] | None:
        student = self.db.fetch_one("SELECT * FROM students WHERE student_id=?", (student_id,))
        if not student: return None
        rows = self.db.fetch_all("""SELECT s.subject_code,s.subject_name,s.credits,m.internal_marks,m.external_marks,m.total_marks,m.grade,COALESCE(a.attendance_percentage,0) attendance_percentage FROM student_subjects ss JOIN subjects s ON s.subject_id=ss.subject_id LEFT JOIN marks m ON m.student_id=ss.student_id AND m.subject_id=ss.subject_id LEFT JOIN attendance a ON a.student_id=ss.student_id AND a.subject_id=ss.subject_id WHERE ss.student_id=? ORDER BY s.subject_code COLLATE NOCASE""", (student_id,))
        completed = [row for row in rows if row["total_marks"] is not None]
        total, average = sum(row["total_marks"] for row in completed), mean([row["total_marks"] for row in completed])
        gpa = calculate_gpa(completed); ranks = self.rankings(student["department"])
        rank_row = next((row for row in ranks if row["student_id"] == student_id), None)
        return {"student": student, "subjects": rows, "total": round(total, 2), "average": average, "gpa": gpa, "cgpa": gpa, "rank": rank_row["rank"] if rank_row else "—", "status": "PASS" if completed and all(row["grade"] != "F" for row in completed) else "FAIL"}

    def rankings(self, department: str | None = None) -> list[dict[str, Any]]:
        where, args = (" WHERE s.department=?", (department,)) if department else ("", ())
        rows = self.db.fetch_all("SELECT s.student_id,s.roll_no,s.name,s.department,COALESCE(AVG(m.total_marks),0) average,COALESCE(SUM(m.total_marks),0) total_marks FROM students s LEFT JOIN marks m ON m.student_id=s.student_id" + where + " GROUP BY s.student_id ORDER BY average DESC, s.roll_no COLLATE NOCASE ASC", args)
        for rank, row in enumerate(rows, 1): row["rank"] = rank; row["cgpa"] = round(min(10, row["average"] / 10), 2)
        return rows

    def dashboard_statistics(self) -> dict[str, Any]:
        ranks = self.rankings(); values = [row["average"] for row in ranks]; passed = sum(value >= 40 for value in values)
        departments = self.db.fetch_all("SELECT department,AVG(total_marks) average FROM students JOIN marks USING(student_id) GROUP BY department ORDER BY department COLLATE NOCASE")
        subject_averages = self.db.fetch_all("SELECT subject_name,AVG(total_marks) average FROM subjects JOIN marks USING(subject_id) GROUP BY subject_id ORDER BY subject_name COLLATE NOCASE")
        return {"highest": max(values, default=0), "lowest": min(values, default=0), "average": mean(values), "pass_percentage": percentage(passed, len(values)), "fail_percentage": percentage(len(values)-passed, len(values)), "top_students": ranks[:10], "departments": departments, "subject_averages": subject_averages}






