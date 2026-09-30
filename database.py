"""SQLite persistence layer. Parameterized queries protect all user input."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class DatabaseManager:
    """Own and initialize the SQLite database connection."""

    def __init__(self, database_path: str | Path = "student_results.db") -> None:
        self.connection = sqlite3.connect(database_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.create_tables()

    def create_tables(self) -> None:
        """Create normalized core and student-subject assignment tables."""
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY, roll_no TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL, department TEXT NOT NULL, semester INTEGER NOT NULL,
                email TEXT, phone TEXT
            );
            CREATE TABLE IF NOT EXISTS subjects (
                subject_id INTEGER PRIMARY KEY, subject_code TEXT UNIQUE NOT NULL,
                subject_name TEXT NOT NULL, credits INTEGER NOT NULL CHECK(credits > 0)
            );
            CREATE TABLE IF NOT EXISTS student_subjects (
                student_id INTEGER NOT NULL, subject_id INTEGER NOT NULL,
                PRIMARY KEY(student_id, subject_id),
                FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                FOREIGN KEY(subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS marks (
                mark_id INTEGER PRIMARY KEY, student_id INTEGER NOT NULL, subject_id INTEGER NOT NULL,
                internal_marks REAL NOT NULL CHECK(internal_marks BETWEEN 0 AND 100),
                external_marks REAL NOT NULL CHECK(external_marks BETWEEN 0 AND 100),
                total_marks REAL NOT NULL, grade TEXT NOT NULL,
                UNIQUE(student_id, subject_id),
                FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                FOREIGN KEY(subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id INTEGER PRIMARY KEY, student_id INTEGER NOT NULL, subject_id INTEGER NOT NULL,
                attendance_percentage REAL NOT NULL CHECK(attendance_percentage BETWEEN 0 AND 100),
                UNIQUE(student_id, subject_id),
                FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                FOREIGN KEY(subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE
            );
        """)
        self.connection.commit()

    def execute(self, query: str, parameters: tuple[Any, ...] = ()) -> int:
        """Run a mutation and return its last inserted row id."""
        cursor = self.connection.execute(query, parameters)
        self.connection.commit()
        return cursor.lastrowid

    def fetch_all(self, query: str, parameters: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        """Fetch result rows as dictionaries."""
        return [dict(row) for row in self.connection.execute(query, parameters).fetchall()]

    def fetch_one(self, query: str, parameters: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        """Fetch one result row as a dictionary."""
        row = self.connection.execute(query, parameters).fetchone()
        return dict(row) if row else None

    def close(self) -> None:
        self.connection.close()
