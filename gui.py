"""Tkinter view for the Student Result Management System."""
from __future__ import annotations

import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Callable

from controller import Controller
from models import Student, Subject
from report_generator import ReportGenerator
from statistics_manager import StatisticsManager
from utils import ensure_reports_dir


class LoginScreen:
    """First-run administrator setup and local sign-in screen."""

    def __init__(self, root: tk.Tk, controller: Controller, on_success: Callable[[], None]) -> None:
        self.root, self.controller, self.on_success = root, controller, on_success
        root.title("Student Results Portal | Sign in")
        root.geometry("720x650")
        root.minsize(620, 560)
        root.configure(background="#0B1220")
        self.setup_mode = not controller.has_administrator()
        self.frame = tk.Frame(root, bg="#0B1220")
        self.frame.pack(fill="both", expand=True)
        card = tk.Frame(self.frame, bg="#111B2C", highlightbackground="#263750", highlightthickness=1, padx=42, pady=38)
        card.place(relx=0.5, rely=0.48, anchor="center", width=460)
        tk.Label(card, text="CAMPUS  /  ACADEMIC SERVICES", bg="#111B2C", fg="#5EEAD4", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(card, text="Student Results Portal", bg="#111B2C", fg="#F1F5FB", font=("Segoe UI", 23, "bold")).pack(anchor="w", pady=(12, 4))
        heading = "Create administrator account" if self.setup_mode else "Welcome back"
        helper = "Set the login details for this local installation." if self.setup_mode else "Sign in to manage academic records."
        tk.Label(card, text=heading, bg="#111B2C", fg="#DCE5F2", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(16, 2))
        tk.Label(card, text=helper, bg="#111B2C", fg="#8295AF", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 18))
        self.login_entry = self._field(card, "LOGIN ID")
        self.password_entry = self._field(card, "PASSWORD", password=True)
        self.confirm_entry = self._field(card, "CONFIRM PASSWORD", password=True) if self.setup_mode else None
        action = "Create account and enter" if self.setup_mode else "Sign in"
        tk.Button(card, text=action, command=self.submit, bg="#2DD4BF", fg="#07131D", activebackground="#5EEAD4", activeforeground="#07131D", relief="flat", cursor="hand2", font=("Segoe UI", 10, "bold"), padx=12, pady=12).pack(fill="x", pady=(12, 0))
        tk.Label(card, text="Your password is stored locally as a salted hash.", bg="#111B2C", fg="#62758F", font=("Segoe UI", 8)).pack(anchor="w", pady=(16, 0))
        self.login_entry.focus_set()
        self.login_entry.bind("<Return>", lambda _event: self.password_entry.focus_set())
        self.password_entry.bind("<Return>", lambda _event: self.confirm_entry.focus_set() if self.confirm_entry else self.submit())
        if self.confirm_entry:
            self.confirm_entry.bind("<Return>", lambda _event: self.submit())

    @staticmethod
    def _field(parent: tk.Widget, label: str, password: bool = False) -> tk.Entry:
        tk.Label(parent, text=label, bg="#111B2C", fg="#9CB0C9", font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(9, 5))
        entry = tk.Entry(parent, bg="#0C1524", fg="#E5EDF7", insertbackground="#E5EDF7", relief="flat", highlightthickness=1, highlightbackground="#2B3C55", highlightcolor="#2DD4BF", font=("Segoe UI", 11), show="●" if password else "")
        entry.pack(fill="x", ipady=11)
        return entry

    def submit(self) -> None:
        try:
            if self.setup_mode:
                assert self.confirm_entry is not None
                self.controller.create_administrator(self.login_entry.get(), self.password_entry.get(), self.confirm_entry.get())
            elif not self.controller.authenticate(self.login_entry.get(), self.password_entry.get()):
                raise ValueError("Login ID or password is incorrect.")
        except (ValueError, sqlite3.IntegrityError) as error:
            messagebox.showerror("Sign in", str(error), parent=self.root)
            self.password_entry.delete(0, tk.END)
            if self.confirm_entry:
                self.confirm_entry.delete(0, tk.END)
            return
        self.frame.destroy()
        self.on_success()


class ApplicationGUI:
    """Tkinter UI. All business behaviour is delegated to Controller."""

    def __init__(self, root: tk.Tk, controller: Controller) -> None:
        self.root, self.controller = root, controller
        self.root.title("Student Result Management System")
        self.root.geometry("1280x820")
        self.root.minsize(1020, 680)
        self.root.configure(background="#0B1220")
        self.selected_student_id: int | None = None
        self._style()

        header = tk.Frame(root, bg="#0A1020", height=92, highlightbackground="#20304A", highlightthickness=1)
        header.pack(fill="x")
        header.pack_propagate(False)
        brand = tk.Frame(header, bg="#0A1020")
        brand.pack(side="left", padx=28, pady=16)
        tk.Label(brand, text="CAMPUS  /  ACADEMIC SERVICES", bg="#0A1020", fg="#5F7698", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(brand, text="Student Results Portal", bg="#0A1020", fg="#F1F5FB", font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(3, 0))
        tk.Label(header, text="RECORDS   ·   RESULTS   ·   ATTENDANCE", bg="#0A1020", fg="#90A3BC", font=("Segoe UI", 9, "bold")).pack(side="right", padx=28)

        content = ttk.Frame(root, style="App.TFrame", padding=(22, 18, 22, 20))
        content.pack(fill="both", expand=True)
        self.tabs = ttk.Notebook(content, style="Portal.TNotebook")
        self.tabs.pack(fill="both", expand=True)
        self._students_tab()
        self._subjects_tab()
        self._marks_tab()
        self._dashboard_tab()

    def _style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("App.TFrame", background="#0B1220")
        style.configure("TFrame", background="#111B2C")
        style.configure("TLabel", background="#111B2C", foreground="#DCE5F2", font=("Segoe UI", 10))
        style.configure("Title.TLabel", background="#111B2C", foreground="#F1F5FB", font=("Segoe UI", 21, "bold"))
        style.configure("Subtitle.TLabel", background="#111B2C", foreground="#8295AF", font=("Segoe UI", 10))
        style.configure("Section.TLabelframe", background="#111B2C", bordercolor="#263750", relief="solid")
        style.configure("Section.TLabelframe.Label", background="#111B2C", foreground="#AFC3DE", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=(12, 8), background="#1B2940", foreground="#C9D6E7", borderwidth=0)
        style.map("TButton", background=[("active", "#293B58"), ("pressed", "#324866")], foreground=[("disabled", "#66758A")])
        style.configure("Primary.TButton", background="#2DD4BF", foreground="#07131D")
        style.map("Primary.TButton", background=[("active", "#5EEAD4"), ("pressed", "#14B8A6")])
        style.configure("Danger.TButton", background="#3A202D", foreground="#F2A7B2")
        style.map("Danger.TButton", background=[("active", "#512936")])
        style.configure("TEntry", padding=9, fieldbackground="#0C1524", foreground="#E5EDF7", bordercolor="#2B3C55", insertcolor="#E5EDF7")
        style.configure("TCombobox", padding=8, fieldbackground="#0C1524", foreground="#E5EDF7", bordercolor="#2B3C55", arrowcolor="#9CB0C9")
        style.map("TCombobox", fieldbackground=[("readonly", "#0C1524")], foreground=[("readonly", "#E5EDF7")], selectbackground=[("readonly", "#0C1524")], selectforeground=[("readonly", "#E5EDF7")])
        style.configure("Portal.TNotebook", background="#0B1220", borderwidth=0, tabmargins=(0, 0, 0, 0))
        style.configure("Portal.TNotebook.Tab", background="#111B2C", foreground="#8092AA", padding=(20, 13), font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("Portal.TNotebook.Tab", background=[("selected", "#16243A"), ("active", "#1C2B42")], foreground=[("selected", "#5EEAD4"), ("active", "#D9E5F2")])
        style.configure("Treeview", rowheight=34, font=("Segoe UI", 10), background="#111B2C", fieldbackground="#111B2C", foreground="#D7E1EE", borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#1A2940", foreground="#9DB1CA", padding=10, relief="flat")
        style.map("Treeview", background=[("selected", "#20485A")], foreground=[("selected", "#F0FDFA")])

    def _tree(self, parent: tk.Widget, columns: tuple[str, ...], widths: list[int]) -> ttk.Treeview:
        tree = ttk.Treeview(parent, columns=columns, show="headings", selectmode="browse")
        for column, width in zip(columns, widths):
            tree.heading(column, text=column.replace("_", " ").title())
            tree.column(column, width=width, anchor="center")
        tree.tag_configure("odd", background="#142137")
        tree.tag_configure("pass", foreground="#5EEAD4")
        tree.tag_configure("fail", foreground="#F2A7B2")
        return tree

    @staticmethod
    def _clear(entries: list[tk.Entry]) -> None:
        for entry in entries:
            entry.delete(0, tk.END)

    def _run(self, action: Callable[[], None]) -> None:
        try:
            action()
        except (ValueError, sqlite3.IntegrityError) as error:
            messagebox.showerror("Validation", str(error))
        except Exception as error:  # GUI boundary: show actionable errors.
            messagebox.showerror("Operation failed", str(error))

    def _students_tab(self) -> None:
        page = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(page, text="Students")
        ttk.Label(page, text="Student Management", style="Title.TLabel").pack(anchor="w", pady=(2, 2))
        ttk.Label(page, text="Maintain profiles, search records, and generate report cards.", style="Subtitle.TLabel").pack(anchor="w")
        form = ttk.LabelFrame(page, text="Student details", padding=14, style="Section.TLabelframe")
        form.pack(fill="x", pady=10)
        names = ("Roll No", "Name", "Department", "Semester", "Email", "Phone")
        self.student_entries: dict[str, tk.Entry] = {}
        for i, name in enumerate(names):
            row, column = divmod(i, 3)
            column *= 2
            ttk.Label(form, text=name).grid(row=row * 2, column=column, sticky="w", padx=(4, 10), pady=(4, 2))
            entry = ttk.Entry(form, width=24)
            entry.grid(row=row * 2 + 1, column=column + 1, sticky="ew", padx=(0, 14), pady=(0, 8))
            form.columnconfigure(column + 1, weight=1)
            self.student_entries[name] = entry
        buttons = ttk.Frame(page)
        buttons.pack(fill="x")
        for label, command in [("Add Student", self.add_student), ("Update Student", self.update_student),
                               ("Delete Student", self.delete_student), ("Generate Report", self.show_report), ("Import Students CSV", lambda: self.import_csv("students")), ("Refresh", self.refresh_students)]:
            ttk.Button(buttons, text=label, style=("Primary.TButton" if label == "Add Student" else "Danger.TButton" if label == "Delete Student" else "TButton"), command=lambda cmd=command: self._run(cmd)).pack(side="left", padx=(0, 8), pady=8)
        search = ttk.Frame(page); search.pack(fill="x", pady=4)
        self.search_query = ttk.Entry(search, width=26); self.search_query.pack(side="left", padx=3)
        self.search_field = ttk.Combobox(search, values=("name", "roll_no", "department"), state="readonly", width=14); self.search_field.set("name"); self.search_field.pack(side="left")
        ttk.Button(search, text="Search", style="Primary.TButton", command=lambda: self._run(self.search_students)).pack(side="left", padx=3)
        columns = ("student_id", "roll_no", "name", "department", "semester", "email", "phone")
        self.student_tree = self._tree(page, columns, [80, 110, 170, 140, 90, 180, 130])
        self.student_tree.configure(height=7)
        self.student_tree.pack(fill="x", expand=False, pady=(6, 8))
        self.student_tree.bind("<<TreeviewSelect>>", self.select_student)
        self.student_details_label = ttk.Label(page, text="Select a student to view enrolled subjects and marks.", style="Subtitle.TLabel")
        self.student_details_label.pack(anchor="w", pady=(4, 8))
        self.student_academic_tree = self._tree(page, ("subject_code", "subject_name", "credits", "internal_marks", "external_marks", "total_marks", "grade", "attendance_percentage"), [110, 210, 70, 100, 100, 90, 70, 130])
        self.student_academic_tree.pack(fill="both", expand=True)
        self.refresh_students()

    def _subjects_tab(self) -> None:
        page = ttk.Frame(self.tabs, padding=12); self.tabs.add(page, text="Subjects")
        ttk.Label(page, text="Subject Catalog", style="Title.TLabel").pack(anchor="w", pady=(2, 2))
        ttk.Label(page, text="Manage courses and credit values used in student results.", style="Subtitle.TLabel").pack(anchor="w")
        form = ttk.Frame(page); form.pack(fill="x", pady=12)
        self.subject_entries: list[tk.Entry] = []
        for i, name in enumerate(("Code", "Subject Name", "Credits")):
            ttk.Label(form, text=name).grid(row=0, column=i * 2, padx=3)
            entry = ttk.Entry(form, width=24); entry.grid(row=0, column=i * 2 + 1, padx=8, pady=6); self.subject_entries.append(entry)
        self.selected_subject_id: int | None = None
        for label, command in [("Add Subject", self.add_subject), ("Update Subject", self.update_subject), ("Delete Subject", self.delete_subject), ("Import Subjects CSV", lambda: self.import_csv("subjects")), ("Refresh", self.refresh_subjects)]:
            style = "Primary.TButton" if label == "Add Subject" else "Danger.TButton" if label == "Delete Subject" else "TButton"
            ttk.Button(page, text=label, style=style, command=lambda cmd=command: self._run(cmd)).pack(side="left", padx=(0, 8), pady=5)
        self.subject_tree = self._tree(page, ("subject_id", "subject_code", "subject_name", "credits"), [120, 180, 350, 120])
        self.subject_tree.configure(height=7)
        self.subject_tree.pack(fill="x", expand=False, pady=(10, 8))
        self.subject_tree.bind("<<TreeviewSelect>>", self.select_subject)
        self.subject_students_label = ttk.Label(page, text="Select a subject to view enrolled students.", style="Subtitle.TLabel")
        self.subject_students_label.pack(anchor="w", pady=(4, 8))
        self.subject_students_tree = self._tree(page, ("roll_no", "name", "department", "semester", "internal_marks", "external_marks", "total_marks", "grade", "attendance_percentage"), [110, 170, 150, 80, 100, 100, 90, 70, 130])
        self.subject_students_tree.pack(fill="both", expand=True)
        self.refresh_subjects()

    def _marks_tab(self) -> None:
        page = ttk.Frame(self.tabs, padding=12); self.tabs.add(page, text="Marks & Attendance")
        ttk.Label(page, text="Marks & Attendance", style="Title.TLabel").pack(anchor="w", pady=(2, 2))
        ttk.Label(page, text="Record assessment results and review attendance by student and subject.", style="Subtitle.TLabel").pack(anchor="w")
        form = ttk.LabelFrame(page, text="Select student and subject", padding=12); form.pack(fill="x", pady=10)
        self.mark_student = ttk.Combobox(form, state="readonly", width=35); self.mark_student.grid(row=0, column=1, padx=5)
        self.mark_subject = ttk.Combobox(form, state="readonly", width=35); self.mark_subject.grid(row=0, column=3, padx=5)
        ttk.Label(form, text="Student").grid(row=0, column=0); ttk.Label(form, text="Subject").grid(row=0, column=2)
        self.mark_entries: list[tk.Entry] = []
        for i, label in enumerate(("Internal (0-100)", "External (0-100)", "Attendance %")):
            ttk.Label(form, text=label).grid(row=1, column=i * 2, pady=8)
            entry = ttk.Entry(form, width=14); entry.grid(row=1, column=i * 2 + 1, padx=6, pady=8); self.mark_entries.append(entry)
        ttk.Button(form, text="Save Marks", style="Primary.TButton", command=lambda: self._run(self.save_mark)).grid(row=2, column=0, columnspan=3, pady=6)
        ttk.Button(form, text="Import Marks CSV", command=lambda: self._run(lambda: self.import_csv("marks"))).grid(row=2, column=3, columnspan=3, pady=6)
        self.refresh_mark_choices()
        attendance_frame = ttk.LabelFrame(page, text="Recorded attendance", padding=12, style="Section.TLabelframe")
        attendance_frame.pack(fill="both", expand=True, pady=8)
        self.attendance_tree = self._tree(attendance_frame, ("roll_no", "name", "subject_code", "subject_name", "attendance_percentage"), [120, 190, 140, 300, 160])
        self.attendance_tree.pack(fill="both", expand=True)
        ttk.Button(attendance_frame, text="Refresh Attendance", command=lambda: self._run(self.refresh_attendance)).pack(anchor="e", pady=4)
        self.refresh_attendance()

    def _dashboard_tab(self) -> None:
        page = ttk.Frame(self.tabs, padding=12); self.tabs.add(page, text="Dashboard")
        ttk.Label(page, text="Academic Overview", style="Title.TLabel").pack(anchor="w", pady=(2, 2))
        ttk.Label(page, text="A snapshot of performance across current student records.", style="Subtitle.TLabel").pack(anchor="w")
        actions = ttk.Frame(page); actions.pack(anchor="w", pady=8)
        ttk.Button(actions, text="Refresh Dashboard", command=lambda: self._run(self.refresh_dashboard)).pack(side="left")
        ttk.Button(actions, text="Generate Charts", command=lambda: self._run(self.generate_charts)).pack(side="left", padx=5)
        metrics = ttk.Frame(page, style="App.TFrame")
        metrics.pack(fill="x", pady=(8, 14))
        self.metric_values: dict[str, tk.Label] = {}
        for index, (key, label, accent) in enumerate((("highest", "HIGHEST AVERAGE", "#2463A6"), ("average", "OVERALL AVERAGE", "#17846A"), ("pass_percentage", "PASS RATE", "#17846A"), ("fail_percentage", "FAIL RATE", "#B74550"), ("lowest", "LOWEST AVERAGE", "#B2762C"))):
            card = tk.Frame(metrics, bg="#111B2C", highlightbackground="#263750", highlightthickness=1, padx=16, pady=12)
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 7, 0))
            metrics.columnconfigure(index, weight=1)
            tk.Label(card, text=label, bg="#111B2C", fg="#8295AF", font=("Segoe UI", 8, "bold")).pack(anchor="w")
            value = tk.Label(card, text="—", bg="#111B2C", fg=accent, font=("Segoe UI", 21, "bold"))
            value.pack(anchor="w", pady=(5, 0))
            self.metric_values[key] = value
        self.rank_tree = self._tree(page, ("rank", "roll_no", "name", "department", "total_marks", "average", "cgpa"), [70, 120, 180, 150, 120, 120, 100])
        self.rank_tree.pack(fill="both", expand=True, pady=10)
        self.refresh_dashboard()

    def _fill_tree(self, tree: ttk.Treeview, rows: list[dict]) -> None:
        tree.delete(*tree.get_children())
        for index, row in enumerate(rows):
            tag = "odd" if index % 2 else ""
            if "status" in row: tag = "pass" if row["status"] == "PASS" else "fail"
            tree.insert("", "end", values=[row.get(column, "") for column in tree["columns"]], tags=(tag,))

    def refresh_attendance(self) -> None:
        rows = self.controller.attendance_records()
        for row in rows: row["attendance_percentage"] = f"{row['attendance_percentage']:.1f}%"
        self._fill_tree(self.attendance_tree, rows)

    @staticmethod
    def _format_academic_rows(rows: list[dict]) -> list[dict]:
        for row in rows:
            for field in ("internal_marks", "external_marks", "total_marks"):
                value = row.get(field)
                row[field] = "—" if value is None else f"{value:.1f}"
            row["attendance_percentage"] = f"{row['attendance_percentage']:.1f}%"
        return rows

    def refresh_student_academics(self, student_id: int | None) -> None:
        if student_id is None:
            self.student_details_label.config(text="Select a student to view enrolled subjects and marks.")
            self._fill_tree(self.student_academic_tree, [])
            return
        student = self.controller.student(student_id)
        if not student:
            self.refresh_student_academics(None)
            return
        rows = self.controller.student_academic_records(student_id)
        self.student_details_label.config(text=f"SUBJECTS & RESULTS  /  {student['roll_no']}  ·  {student['name']}  ·  {len(rows)} enrolled")
        self._fill_tree(self.student_academic_tree, self._format_academic_rows(rows))

    def refresh_subject_students(self, subject_id: int | None) -> None:
        if subject_id is None:
            self.subject_students_label.config(text="Select a subject to view enrolled students.")
            self._fill_tree(self.subject_students_tree, [])
            return
        subject = self.controller.subject(subject_id)
        if not subject:
            self.refresh_subject_students(None)
            return
        rows = self.controller.subject_students(subject_id)
        self.subject_students_label.config(text=f"ENROLLED STUDENTS  /  {subject['subject_code']}  ·  {subject['subject_name']}  ·  {len(rows)} students")
        self._fill_tree(self.subject_students_tree, self._format_academic_rows(rows))

    def refresh_students(self) -> None:
        self._fill_tree(self.student_tree, self.controller.students()); self.refresh_mark_choices()
        if hasattr(self, "student_academic_tree") and self.selected_student_id is not None:
            self.refresh_student_academics(self.selected_student_id)

    def refresh_subjects(self) -> None:
        self._fill_tree(self.subject_tree, self.controller.subjects()); self.refresh_mark_choices()
        if hasattr(self, "subject_students_tree") and self.selected_subject_id is not None:
            self.refresh_subject_students(self.selected_subject_id)

    def refresh_mark_choices(self) -> None:
        students = self.controller.students(); subjects = self.controller.subjects()
        if hasattr(self, "mark_student"):
            self.mark_student["values"] = [f"{row['student_id']} | {row['roll_no']} | {row['name']}" for row in students]
            self.mark_subject["values"] = [f"{row['subject_id']} | {row['subject_code']} | {row['subject_name']}" for row in subjects]

    def add_student(self) -> None:
        e = self.student_entries
        self.controller.add_student(Student(e["Roll No"].get(), e["Name"].get(), e["Department"].get(), int(e["Semester"].get()), e["Email"].get(), e["Phone"].get()))
        self._clear(list(e.values())); self.refresh_students()

    def update_student(self) -> None:
        if self.selected_student_id is None: raise ValueError("Select a student first.")
        e = self.student_entries
        self.controller.update_student(self.selected_student_id, Student(e["Roll No"].get(), e["Name"].get(), e["Department"].get(), int(e["Semester"].get()), e["Email"].get(), e["Phone"].get()))
        self.refresh_students()

    def delete_student(self) -> None:
        if self.selected_student_id is None: raise ValueError("Select a student first.")
        if messagebox.askyesno("Confirm deletion", "Delete selected student and academic records?"):
            self.controller.delete_student(self.selected_student_id); self.selected_student_id = None; self.refresh_students(); self.refresh_student_academics(None)

    def select_student(self, _: object) -> None:
        selection = self.student_tree.selection()
        if selection:
            values = self.student_tree.item(selection[0])["values"]; self.selected_student_id = int(values[0])
            for entry, value in zip(self.student_entries.values(), values[1:]): entry.delete(0, tk.END); entry.insert(0, value)
            self.refresh_student_academics(self.selected_student_id)

    def search_students(self) -> None:
        results = self.controller.search_students(self.search_field.get(), self.search_query.get())
        self._fill_tree(self.student_tree, results)

    def import_csv(self, data_type: str) -> None:
        path = filedialog.askopenfilename(title="Select CSV data file", filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        count = self.controller.import_csv(path, data_type)
        self.refresh_students()
        self.refresh_subjects()
        self.refresh_attendance()
        self.refresh_dashboard()
        messagebox.showinfo("Import complete", f"Imported {count} {data_type} rows.")

    def add_subject(self) -> None:
        code, name, credits = (entry.get() for entry in self.subject_entries)
        self.controller.add_subject(Subject(code, name, int(credits))); self._clear(self.subject_entries); self.refresh_subjects()

    def update_subject(self) -> None:
        if self.selected_subject_id is None: raise ValueError("Select a subject first.")
        code, name, credits = (entry.get() for entry in self.subject_entries)
        self.controller.update_subject(self.selected_subject_id, Subject(code, name, int(credits))); self.refresh_subjects()

    def delete_subject(self) -> None:
        if self.selected_subject_id is None: raise ValueError("Select a subject first.")
        if messagebox.askyesno("Confirm deletion", "Delete selected subject?"):
            self.controller.delete_subject(self.selected_subject_id); self.selected_subject_id = None; self.refresh_subjects(); self.refresh_subject_students(None)

    def select_subject(self, _: object) -> None:
        selection = self.subject_tree.selection()
        if selection:
            values = self.subject_tree.item(selection[0])["values"]; self.selected_subject_id = int(values[0])
            for entry, value in zip(self.subject_entries, values[1:]): entry.delete(0, tk.END); entry.insert(0, value)
            self.refresh_subject_students(self.selected_subject_id)

    def save_mark(self) -> None:
        student_id = int(self.mark_student.get().split(" | ")[0]); subject_id = int(self.mark_subject.get().split(" | ")[0])
        internal, external, attendance = (float(entry.get()) for entry in self.mark_entries)
        self.controller.record_mark(student_id, subject_id, internal, external, attendance)
        self._clear(self.mark_entries); messagebox.showinfo("Saved", "Marks and attendance saved."); self.refresh_attendance(); self.refresh_dashboard()
        self.refresh_student_academics(self.selected_student_id)
        self.refresh_subject_students(self.selected_subject_id)

    def show_report(self) -> None:
        if self.selected_student_id is None: raise ValueError("Select a student first.")
        data = self.controller.report_data(self.selected_student_id)
        window = tk.Toplevel(self.root); window.title("Report Card"); window.geometry("800x570")
        window.configure(background="#0B1220")
        text = tk.Text(window, font=("Consolas", 10), wrap="none", bg="#111B2C", fg="#DCE5F2", insertbackground="#DCE5F2", relief="flat", padx=16, pady=16); text.insert("1.0", ReportGenerator.to_text(data)); text.config(state="disabled"); text.pack(fill="both", expand=True, padx=12, pady=12)
        def export() -> None:
            default = ensure_reports_dir() / f"report_{data['student']['roll_no']}.pdf"
            path = filedialog.asksaveasfilename(initialfile=default.name, initialdir=default.parent, defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
            if path: ReportGenerator().export_pdf(data, path); messagebox.showinfo("Exported", f"PDF saved to {path}")
        ttk.Button(window, text="Export PDF", command=lambda: self._run(export)).pack(pady=6)

    def refresh_dashboard(self) -> None:
        stats = self.controller.dashboard_statistics()
        for key in ("highest", "average", "lowest"):
            self.metric_values[key].config(text=f"{stats[key]:.1f}")
        for key in ("pass_percentage", "fail_percentage"):
            self.metric_values[key].config(text=f"{stats[key]:.1f}%")
        self._fill_tree(self.rank_tree, stats["top_students"])

    def generate_charts(self) -> None:
        paths = StatisticsManager(self.controller).generate_charts()
        messagebox.showinfo("Charts created", "Saved charts:\n" + "\n".join(str(path) for path in paths))

















