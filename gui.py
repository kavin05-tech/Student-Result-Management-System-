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


class ApplicationGUI:
    """Tkinter UI. All business behaviour is delegated to Controller."""

    def __init__(self, root: tk.Tk, controller: Controller) -> None:
        self.root, self.controller = root, controller
        self.root.title("Student Result Management System")
        self.root.geometry("1280x820")
        self.root.minsize(1020, 680)
        self.root.configure(background="#F3F6FB")
        self.selected_student_id: int | None = None
        self._style()

        header = tk.Frame(root, bg="#142B4A", height=92)
        header.pack(fill="x")
        header.pack_propagate(False)
        brand = tk.Frame(header, bg="#142B4A")
        brand.pack(side="left", padx=28, pady=16)
        tk.Label(brand, text="CAMPUS   /   ACADEMIC SERVICES", bg="#142B4A", fg="#AFC5E2", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(brand, text="Student Results Portal", bg="#142B4A", fg="white", font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(3, 0))
        tk.Label(header, text="RECORDS  •  RESULTS  •  ATTENDANCE", bg="#142B4A", fg="#C9D7E8", font=("Segoe UI", 9, "bold")).pack(side="right", padx=28)

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
        style.configure("App.TFrame", background="#F3F6FB")
        style.configure("TFrame", background="#FFFFFF")
        style.configure("TLabel", background="#FFFFFF", foreground="#34445A", font=("Segoe UI", 10))
        style.configure("Title.TLabel", background="#FFFFFF", foreground="#172B4D", font=("Segoe UI", 21, "bold"))
        style.configure("Subtitle.TLabel", background="#FFFFFF", foreground="#718096", font=("Segoe UI", 10))
        style.configure("Section.TLabelframe", background="#FFFFFF", bordercolor="#DCE4EF", relief="solid")
        style.configure("Section.TLabelframe.Label", background="#FFFFFF", foreground="#233B5D", font=("Segoe UI", 10, "bold"))
        style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=(12, 8), background="#E8EEF6", foreground="#233B5D", borderwidth=0)
        style.map("TButton", background=[("active", "#D8E4F2"), ("pressed", "#C6D6E9")])
        style.configure("Primary.TButton", background="#2463A6", foreground="white")
        style.map("Primary.TButton", background=[("active", "#1B528E"), ("pressed", "#17477B")])
        style.configure("Danger.TButton", background="#FCEBEC", foreground="#A8323E")
        style.map("Danger.TButton", background=[("active", "#F7DADD")])
        style.configure("TEntry", padding=8, fieldbackground="#FFFFFF", bordercolor="#CBD5E1")
        style.configure("TCombobox", padding=7, fieldbackground="#FFFFFF", bordercolor="#CBD5E1")
        style.configure("Portal.TNotebook", background="#F3F6FB", borderwidth=0, tabmargins=(0, 0, 0, 0))
        style.configure("Portal.TNotebook.Tab", background="#E7EDF5", foreground="#52647C", padding=(20, 12), font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("Portal.TNotebook.Tab", background=[("selected", "#FFFFFF"), ("active", "#D9E4F1")], foreground=[("selected", "#1D5D9B")])
        style.configure("Treeview", rowheight=34, font=("Segoe UI", 10), background="#FFFFFF", fieldbackground="#FFFFFF", foreground="#34445A", borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#EAF0F7", foreground="#48617F", padding=10, relief="flat")
        style.map("Treeview", background=[("selected", "#D8E9FC")], foreground=[("selected", "#172B4D")])

    def _tree(self, parent: tk.Widget, columns: tuple[str, ...], widths: list[int]) -> ttk.Treeview:
        tree = ttk.Treeview(parent, columns=columns, show="headings", selectmode="browse")
        for column, width in zip(columns, widths):
            tree.heading(column, text=column.replace("_", " ").title())
            tree.column(column, width=width, anchor="center")
        tree.tag_configure("odd", background="#EDF3F9")
        tree.tag_configure("pass", foreground="#218739")
        tree.tag_configure("fail", foreground="#C62828")
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
            ttk.Label(form, text=name).grid(row=0, column=i * 2, sticky="w", padx=3)
            entry = ttk.Entry(form, width=18)
            entry.grid(row=0, column=i * 2 + 1, padx=3)
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
        self.student_tree.pack(fill="both", expand=True); self.student_tree.bind("<<TreeviewSelect>>", self.select_student)
        self.refresh_students()

    def _subjects_tab(self) -> None:
        page = ttk.Frame(self.tabs, padding=12); self.tabs.add(page, text="Subjects")
        ttk.Label(page, text="Subject Catalog", style="Title.TLabel").pack(anchor="w", pady=(2, 2))
        ttk.Label(page, text="Manage courses and credit values used in student results.", style="Subtitle.TLabel").pack(anchor="w")
        form = ttk.Frame(page); form.pack(fill="x", pady=12)
        self.subject_entries: list[tk.Entry] = []
        for i, name in enumerate(("Code", "Subject Name", "Credits")):
            ttk.Label(form, text=name).grid(row=0, column=i * 2, padx=3)
            entry = ttk.Entry(form, width=24); entry.grid(row=0, column=i * 2 + 1, padx=3); self.subject_entries.append(entry)
        self.selected_subject_id: int | None = None
        for label, command in [("Add Subject", self.add_subject), ("Update Subject", self.update_subject), ("Delete Subject", self.delete_subject), ("Import Subjects CSV", lambda: self.import_csv("subjects")), ("Refresh", self.refresh_subjects)]:
            ttk.Button(page, text=label, command=lambda cmd=command: self._run(cmd)).pack(side="left", padx=3)
        self.subject_tree = self._tree(page, ("subject_id", "subject_code", "subject_name", "credits"), [120, 180, 350, 120])
        self.subject_tree.pack(fill="both", expand=True, pady=10); self.subject_tree.bind("<<TreeviewSelect>>", self.select_subject)
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
            entry = ttk.Entry(form, width=14); entry.grid(row=1, column=i * 2 + 1); self.mark_entries.append(entry)
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
            card = tk.Frame(metrics, bg="white", highlightbackground="#DCE4EF", highlightthickness=1, padx=16, pady=12)
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 7, 0))
            metrics.columnconfigure(index, weight=1)
            tk.Label(card, text=label, bg="white", fg="#718096", font=("Segoe UI", 8, "bold")).pack(anchor="w")
            value = tk.Label(card, text="—", bg="white", fg=accent, font=("Segoe UI", 21, "bold"))
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

    def refresh_students(self) -> None:
        self._fill_tree(self.student_tree, self.controller.students()); self.refresh_mark_choices()

    def refresh_subjects(self) -> None:
        self._fill_tree(self.subject_tree, self.controller.subjects()); self.refresh_mark_choices()

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
            self.controller.delete_student(self.selected_student_id); self.selected_student_id = None; self.refresh_students()

    def select_student(self, _: object) -> None:
        selection = self.student_tree.selection()
        if selection:
            values = self.student_tree.item(selection[0])["values"]; self.selected_student_id = int(values[0])
            for entry, value in zip(self.student_entries.values(), values[1:]): entry.delete(0, tk.END); entry.insert(0, value)

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
            self.controller.delete_subject(self.selected_subject_id); self.refresh_subjects()

    def select_subject(self, _: object) -> None:
        selection = self.subject_tree.selection()
        if selection:
            values = self.subject_tree.item(selection[0])["values"]; self.selected_subject_id = int(values[0])
            for entry, value in zip(self.subject_entries, values[1:]): entry.delete(0, tk.END); entry.insert(0, value)

    def save_mark(self) -> None:
        student_id = int(self.mark_student.get().split(" | ")[0]); subject_id = int(self.mark_subject.get().split(" | ")[0])
        internal, external, attendance = (float(entry.get()) for entry in self.mark_entries)
        self.controller.record_mark(student_id, subject_id, internal, external, attendance)
        self._clear(self.mark_entries); messagebox.showinfo("Saved", "Marks and attendance saved."); self.refresh_attendance(); self.refresh_dashboard()

    def show_report(self) -> None:
        if self.selected_student_id is None: raise ValueError("Select a student first.")
        data = self.controller.report_data(self.selected_student_id)
        window = tk.Toplevel(self.root); window.title("Report Card"); window.geometry("800x570")
        text = tk.Text(window, font=("Consolas", 10), wrap="none"); text.insert("1.0", ReportGenerator.to_text(data)); text.config(state="disabled"); text.pack(fill="both", expand=True, padx=8, pady=8)
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

















