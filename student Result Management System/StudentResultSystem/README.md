# Student Result Management System

A desktop application for managing academic records, built with Python, Tkinter, and SQLite. It demonstrates clean layered design, OOP domain models, normalized relational data, custom algorithms, report-card generation, and data visualisation.

## Features

- Student and subject CRUD with input validation and duplicate-roll-number protection.
- Student-to-subject assignment, marks and attendance entry, automatic total, grade, GPA/CGPA, result status, and merit ranking.
- Report cards with subject-wise marks, attendance, total, average, rank, and PDF export.
- Search by name, roll number, or department; exact roll lookup uses manual binary search after manual bubble sort.
- Dashboard for highest/lowest/average marks, pass/fail percentage, merit list, and matplotlib charts.

## Architecture

`gui.py` is the Tkinter View, `controller.py` is the application/service Controller, and `models.py` supplies domain objects. `database.py` is the persistence layer. The `algorithms/` package contains manual linear search, binary search, bubble sort, grading, and statistics helpers. `report_generator.py` and `statistics_manager.py` produce outputs without mixing those responsibilities into the UI.

## Database schema

| Table | Purpose |
|---|---|
| `students` | Student profile including a unique roll number |
| `subjects` | Subject catalogue and credits |
| `student_subjects` | Many-to-many subject assignments |
| `marks` | Internal/external marks, calculated total and grade |
| `attendance` | Per-student, per-subject attendance percentage |

Foreign keys enforce referential integrity, and cascade deletion removes dependent academic records.

## Installation and run

Requires Python 3.12+ with Tk support.

```bash
cd StudentResultSystem
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
python main.py
```

On Linux/macOS activate with `source .venv/bin/activate`. SQLite is included with Python; `matplotlib` is needed for charts and `reportlab` for PDF export.

## Populate sample data

From the project folder run:

```bash
python sample_data.py
```

It creates three students, three subjects, and marks in `student_results.db`. It intentionally will not add data if students already exist.

## Testing the application

1. Add a student in **Students** and a subject in **Subjects**.
2. Select values in **Marks & Attendance**, enter values from 0–100, and save.
3. Select the student row and click **Generate Report**; export a PDF from the report window.
4. Search by name/department using linear search, or use **Binary Roll Search** for an exact roll number.
5. Open **Dashboard**, refresh it, and inspect the merit list. In Python, call `StatisticsManager(controller).generate_charts()` to save the four charts under `reports/`.
6. Verify validation by attempting blank fields, duplicate rolls, invalid marks, or deleting a selected record.

## Algorithms used

- **Linear search:** manual scan for partial name, roll, and department searches.
- **Binary search:** manual low/middle/high exact lookup of roll numbers after bubble sorting them.
- **Bubble sort:** manual stable sort for merit ranking by average; it can also sort records by total marks, average, CGPA, or rank through its key argument.

## Screenshots

_Add application screenshots here after running the app (for example, dashboard, marks entry, and report-card windows)._

## GitHub packaging

Commit source code, `README.md`, and `requirements.txt`; add `student_results.db`, generated PDFs, and PNG charts to `.gitignore` if they contain local or sensitive academic data. Create the repository from this directory, then run `git init`, `git add .`, `git commit -m "Initial Student Result Management System"`, add your GitHub remote, and push.

## Resume highlights

- Designed an MVC-style Python desktop system using Tkinter and SQLite with normalized relational schema and foreign-key integrity.
- Implemented custom linear search, binary search, and bubble sort to support academic lookup and merit ranking.
- Automated grades, GPA/CGPA, result status, report-card PDF exports, and data-driven statistical visualisations.

## Future enhancements

Role-based authentication, semester history for true multi-semester CGPA, CSV import/export, printable institutional templates, automated backups, and a larger analytics dashboard.
