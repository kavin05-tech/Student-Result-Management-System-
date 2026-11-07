# Student Result Management System

A Python desktop application for managing student records, subjects, marks, attendance, and academic reports. It uses Tkinter/ttk for the interface and SQLite for local storage.

## Features

- Add, view, update, and delete student and subject records.
- Search students by name, roll number, or department using SQLite queries.
- Record internal and external marks and attendance for a student–subject pair.
- Import student, subject, and marks data from CSV files.
- View recorded attendance in the Marks & Attendance screen.
- Calculate totals, grades, credit-weighted GPA, rankings, and dashboard statistics.
- Generate report cards and export them as PDFs.
- Create performance charts with Matplotlib.
- Portal-style desktop layout with a dashboard, clear sections, and summary cards.

## Technology

| Component | Technology |
| --- | --- |
| Language | Python 3.12+ |
| Desktop interface | Tkinter / ttk |
| Database | SQLite |
| PDF export | ReportLab |
| Charts | Matplotlib |

Tkinter and SQLite are part of Python's standard library. Your Python installation must include Tk support.

## Quick start

```bash
git clone https://github.com/kavin05-tech/Student-Result-Management-System-.git
cd Student-Result-Management-System-
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install the dependencies and launch the application:

```bash
python -m pip install -r requirements.txt
python main.py
```

The application creates `student_results.db` beside `main.py` automatically. A fresh installation starts with an empty database.

### Optional demo data

Run `python sample_data.py` before opening the application to add three fictional students, three subjects, marks, and attendance. The script skips seeding if students are already present.

## Using the application

1. Add students in **Students** and courses in **Subjects**, or use the CSV import buttons.
2. In **Marks & Attendance**, choose a student and subject and enter internal marks, external marks, and attendance from 0 to 100.
3. Review the recorded attendance table in **Marks & Attendance**. Saving marks and importing a marks CSV refreshes the table.
4. Select a student in **Students** and choose **Generate Report** to view the report card or export it as a PDF.
5. Open **Dashboard** to review summary metrics and merit rankings.

## Import data from CSV

Each data screen has its own import button:

- **Import Students CSV** on the Students screen.
- **Import Subjects CSV** on the Subjects screen.
- **Import Marks CSV** on the Marks & Attendance screen.

Choose a UTF-8 CSV file. Column headers must use the names shown below. Import students and subjects before importing marks. Each file is processed as a transaction; if a row is invalid, duplicates a unique record, or references a missing student or subject, the import is rolled back and the error includes the CSV row number.

### Students CSV

Required columns: `roll_no,name,department,semester`. Optional columns: `email,phone`.

```csv
roll_no,name,department,semester,email,phone
CSE001,Aisha Khan,Computer Science,1,aisha@example.com,5550101
```

### Subjects CSV

Required columns: `subject_code,subject_name,credits`.

```csv
subject_code,subject_name,credits
CS101,Data Structures,4
```

### Marks and attendance CSV

Required columns: `roll_no,subject_code,internal_marks,external_marks,attendance_percentage`. The roll number and subject code must already exist in the database. Importing an existing student–subject pair updates its marks and attendance.

```csv
roll_no,subject_code,internal_marks,external_marks,attendance_percentage
CSE001,CS101,88,92,95
```

## Project structure

| Path | Responsibility |
| --- | --- |
| `main.py` | Start the application and close the database on exit |
| `gui.py` | Portal-style Tkinter screens, tables, dashboard, and report window |
| `controller.py` | Validation, SQL queries, CSV imports, calculations, and application operations |
| `database.py` | SQLite connection, schema creation, and query helpers |
| `models.py` | Student, Subject, Marks, and Attendance data classes |
| `report_generator.py` | Text report rendering and PDF export |
| `statistics_manager.py` | Performance chart generation |
| `algorithms/` | Grading and statistics helpers |
| `sample_data.py` | Optional fictional demo records |
| `utils.py` | Application paths and report directory creation |
| `requirements.txt` | Third-party dependencies |

Student search, ordering, and merit ranking use parameterized SQLite queries and SQL `ORDER BY`. The GUI delegates application operations to the controller; report and chart generation use separate services.

## Database design

| Table | Stores |
| --- | --- |
| `students` | Student details and unique roll numbers |
| `subjects` | Subject codes, names, and credits |
| `student_subjects` | Student–subject assignments |
| `marks` | Internal/external marks, total, and grade |
| `attendance` | Attendance percentage for a student–subject pair |

Foreign keys are enabled. Deleting a student or subject cascades to dependent records. User input is passed through parameterized SQL queries.

## Calculation rules and limitations

- Total marks are calculated as `(internal + external) / 2`.
- Grades use the project's demonstration rules: A+ ≥90, A ≥80, B+ ≥70, B ≥60, C ≥50, D ≥40, and F <40.
- GPA is weighted by subject credits. These rules are not an official university grading policy.
- The report's CGPA currently repeats GPA. Semester history and true cumulative CGPA are not implemented.
- Merit rankings use average marks. The field labelled CGPA in rankings/charts is an approximation of `average / 10`.
- Dashboard pass percentage uses student averages ≥40. An individual report requires all recorded subject grades to be non-F.
- Missing marks are excluded from GPA and averages. Attendance is displayed but does not affect pass/fail.
- The application is a local desktop app. Authentication and a web API are not implemented.

Charts are saved under `reports/`. Local reports and database files are ignored by Git.
