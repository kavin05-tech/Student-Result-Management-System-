"""Optional deterministic seed data for demonstrations and testing."""
from pathlib import Path

from controller import Controller
from database import DatabaseManager
from models import Student, Subject


def seed() -> None:
    """Populate an empty database with representative data."""
    db = DatabaseManager(Path(__file__).with_name("student_results.db")); controller = Controller(db)
    if controller.students():
        print("Database already contains students; no seed data added."); return
    subjects = [("CS101", "Data Structures", 4), ("CS102", "Database Systems", 4), ("MA101", "Discrete Mathematics", 3)]
    subject_ids = [controller.add_subject(Subject(*item)) for item in subjects]
    people = [("CSE001", "Aisha Khan", "Computer Science", 1), ("CSE002", "Rohan Patel", "Computer Science", 1), ("ECE001", "Meera Das", "Electronics", 1)]
    marks = [(92, 88, 95), (78, 74, 88), (55, 61, 75)]
    for person, values in zip(people, marks):
        student_id = controller.add_student(Student(*person))
        for subject_id, value in zip(subject_ids, values):
            controller.record_mark(student_id, subject_id, value - 5, value + 5, 85)
    db.close(); print("Sample data inserted.")


if __name__ == "__main__":
    seed()
