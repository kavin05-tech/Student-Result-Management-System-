# Student Result Management System

A Python desktop application for managing student records, subjects, marks, and attendance. Built with Tkinter and SQLite, it supports academic reports, PDF export, search, and performance summaries.

## Features

- Create, view, update, and delete students and subjects.
- Create a local administrator login on first launch and sign in on later launches.
- Record internal marks, external marks, and attendance for each student–subject pair.
- Calculate total marks, letter grades, and credit-weighted GPA.
- Generate student report cards and export them as PDFs.
- Search students by name, roll number, or department.
- View merit rankings and a dashboard of academic statistics.
- Select a subject to view its enrolled students, or a student to view subjects and marks.
- Generate performance charts using Matplotlib through the Python service.

## Technology

| Component | Technology |
| --- | --- |
| Language | Python |
| Desktop interface | Tkinter / ttk |
| Database | SQLite |
| PDF export | ReportLab |
| Charts | Matplotlib |

Tkinter and SQLite are Python standard-library modules. Tk support must be installed with your Python distribution.

## Quick start

Use Python 3.12+ and a desktop environment.

```bash
git clone https://github.com/kavin05-tech/Student-Result-Management-System-.git
cd Student-Result-Management-System-
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies and launch:

```bash
python -m pip install -r requirements.txt
python main.py
```

The application creates `student_results.db` beside `main.py` automatically. A fresh clone starts with an empty database.

**Existing users:** before switching to this layout, back up your database from
`student Result Management System/StudentResultSystem/student_results.db`.
To retain your records, copy that backup beside the new root-level `main.py`.
Database files are excluded from future commits.

### Optional demo data

Run this before opening the application:

```bash
python sample_data.py
```

This adds three fictional students, three subjects, marks, and attendance. If any students already exist, the script skips seeding. It is intended for an empty database.

## Using the application

1. On first launch, create an administrator login ID and password. Later launches show the sign-in screen first. Login IDs must have at least 3 characters; passwords need at least 8.
2. Add a student in **Students** and a subject in **Subjects**, or import them from CSV.
3. Select a student to see their enrolled subjects, marks, grades, and attendance. Select a subject to see its enrolled students and their results.
4. Use **Marks & Attendance** to enter marks and attendance from 0–100. Attendance is also shown in the student's details and the attendance table.
5. Select a student in **Students** and choose **Generate Report** to view or export a PDF report card.
6. Search students by name, roll number, or department; SQLite performs filtering and sorting. Open **Dashboard** to view performance metrics and rankings.

To generate chart files separately, run this from the repository root:

```python
from pathlib import Path
from controller import Controller
from database import DatabaseManager
from statistics_manager import StatisticsManager

database = DatabaseManager(Path("student_results.db"))
try:
    paths = StatisticsManager(Controller(database)).generate_charts()
    print(paths)
finally:
    database.close()
```

Charts are saved under `reports/`. Local reports and database files are ignored by Git.

## Project structure

| Path | Responsibility |
| --- | --- |
| `main.py` | Start the application and close the database on exit |
| `gui.py` | Tkinter forms, tables, dashboard, and report window |
| `controller.py` | Record management, validation, calculations, and SQL orchestration |
| `database.py` | SQLite connection, schema creation, and query helpers |
| `models.py` | Student, Subject, Marks, and Attendance dataclasses |
| `report_generator.py` | Text report rendering and PDF export |
| `statistics_manager.py` | Performance chart generation |
| `algorithms/` | Grading and statistics helpers |
| `sample_data.py` | Optional fictional demo records |
| `utils.py` | Application-relative paths and report directory creation |
| `requirements.txt` | Third-party dependencies |

The GUI delegates operations to the controller, which uses the database layer and calculation helpers. Report and chart generation are handled by separate services.

## Database design

| Table | Stores |
| --- | --- |
| `students` | Student details and a unique roll number |
| `subjects` | Subject codes, names, and credits |
| `student_subjects` | Student–subject assignments |
| `marks` | Internal/external marks, total, and grade |
| `attendance` | Attendance for a student–subject pair |

Foreign keys are enabled. Deleting a student or subject cascades to its dependent records. User values are passed through parameterized SQL queries.

## Calculation rules and current limitations

- Total marks are calculated as `(internal + external) / 2`.
- Grades follow the project's own rules: A+ ≥90, A ≥80, B+ ≥70, B ≥60, C ≥50, D ≥40, and F <40.
- GPA uses grade points weighted by subject credits. These are demonstration rules, not an official university grading implementation.
- The report's **CGPA** currently repeats GPA. Semester history and true cumulative CGPA are not implemented.
- Merit rankings use average marks. The ranking/chart field called **CGPA** is an approximation of `average / 10`, rather than credit-weighted cumulative GPA.
- Dashboard pass percentage uses student averages ≥40. An individual report requires all recorded subject grades to be non-F; the two summaries can differ.
- Missing marks are excluded from GPA and averages. A report may show PASS for recorded subjects while other assigned subjects are incomplete.
- Rankings do not separate semesters or account for different subject sets. Attendance is displayed but does not affect pass/fail.
- This is a local desktop application; authentication and a web API are future improvements.

## SQL queries

Student search, ordering, and merit rankings use parameterized SQLite queries and SQL `ORDER BY`.

## Suggested improvements

- Store results by semester and calculate cumulative GPA consistently.
- Use consistent result rules across reports and dashboards.
- Add transaction handling for related marks and attendance writes.
- Add automated tests and stronger field validation.
- Add CSV export and database backups.

## CSV imports

Use **Import Students CSV** on the Students tab, **Import Subjects CSV** on the Subjects tab, and **Import Marks CSV** on the Marks & Attendance tab. Each button opens a CSV file picker for that data type. Import students and subjects before importing marks. Save files as UTF-8. Each file is imported transactionally: if a row is invalid or refers to a duplicate/missing record, the import rolls back and reports the row number.

- Students: required headers `roll_no,name,department,semester`; optional `email,phone`.
- Subjects: required headers `subject_code,subject_name,credits`.
- Marks: required headers `roll_no,subject_code,internal_marks,external_marks,attendance_percentage`. Students and subjects must already exist. Marks and attendance are saved together.

Headers must use these exact names. Example student file:

```csv
roll_no,name,department,semester,email,phone
CSE001,Aisha Khan,Computer Science,1,aisha@example.com,5550101
```


Attendance can be viewed directly in the **Marks & Attendance** tab in the Recorded attendance table. Use **Refresh Attendance** after changes; saving marks or importing a marks CSV refreshes it automatically.

The desktop interface uses a dark portal-style layout with a performance dashboard, searchable records, and student/subject detail tables. The administrator login is local to this database; passwords are stored as salted PBKDF2 hashes, not plain text. This is a local desktop application, not a hosted web portal, and it does not include password reset or multiple user roles.

