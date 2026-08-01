"""Domain objects for the Student Result Management System."""
from dataclasses import dataclass


@dataclass(slots=True)
class Student:
    roll_no: str
    name: str
    department: str
    semester: int
    email: str = ""
    phone: str = ""
    student_id: int | None = None


@dataclass(slots=True)
class Subject:
    subject_code: str
    subject_name: str
    credits: int
    subject_id: int | None = None


@dataclass(slots=True)
class Marks:
    student_id: int
    subject_id: int
    internal_marks: float
    external_marks: float
    total_marks: float = 0.0
    grade: str = "F"


@dataclass(slots=True)
class Attendance:
    student_id: int
    subject_id: int
    attendance_percentage: float
