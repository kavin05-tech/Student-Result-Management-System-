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
        self.root.geometry("1180x720")
        self.root.minsize(900, 600)
        self.selected_student_id: int | None = None
        self._style()
        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill="both", expand=True, padx=12, pady=12)
        self._students_tab()
        self._subjects_tab()
        self._marks_tab()
        self._dashboard_tab()

    def _style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), foreground="#17365D")
        style.configure("Pass.TLabel", foreground="#218739", font=("Segoe UI", 11, "bold"))
        style.configure("Fail.TLabel", foreground="#C62828", font=("Segoe UI", 11, "bold"))
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#17365D", foreground="white")

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
        ttk.Label(page, text="Student Management", style="Title.TLabel").pack(anchor="w")
        form = ttk.LabelFrame(page, text="Student details", padding=10)
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
                               ("Delete Student", self.delete_student), ("Generate Report", self.show_report), ("Refresh", self.refresh_students)]:
            ttk.Button(buttons, text=label, command=lambda cmd=command: self._run(cmd)).pack(side="left", padx=3, pady=4)
        search = ttk.Frame(page); search.pack(fill="x", pady=4)
        self.search_query = ttk.Entry(search, width=26); self.search_query.pack(side="left", padx=3)
        self.search_field = ttk.Combobox(search, values=("name", "roll_no", "department"), state="readonly", width=14); self.search_field.set("name"); self.search_field.pack(side="left")
        ttk.Button(search, text="Search", command=lambda: self._run(self.search_students)).pack(side="left", padx=3)
        ttk.Button(search, text="Binary Roll Search", command=lambda: self._run(lambda: self.search_students(True))).pack(side="left")
        columns = ("student_id", "roll_no", "name", "department", "semester", "email", "phone")
        self.student_tree = self._tree(page, columns, [80, 110, 170, 140, 90, 180, 130])
        self.student_tree.pack(fill="both", expand=True); self.student_tree.bind("<<TreeviewSelect>>", self.select_student)
        self.refresh_students()

    def _subjects_tab(self) -> None:
        page = ttk.Frame(self.tabs, padding=12); self.tabs.add(page, text="Subjects")
        ttk.Label(page, text="Subject Management", style="Title.TLabel").pack(anchor="w")
        form = ttk.Frame(page); form.pack(fill="x", pady=12)
        self.subject_entries: list[tk.Entry] = []
        for i, name in enumerate(("Code", "Subject Name", "Credits")):
            ttk.Label(form, text=name).grid(row=0, column=i * 2, padx=3)
            entry = ttk.Entry(form, width=24); entry.grid(row=0, column=i * 2 + 1, padx=3); self.subject_entries.append(entry)
        self.selected_subject_id: int | None = None
        for label, command in [("Add Subject", self.add_subject), ("Update Subject", self.update_subject), ("Delete Subject", self.delete_subject), ("Refresh", self.refresh_subjects)]:
            ttk.Button(page, text=label, command=lambda cmd=command: self._run(cmd)).pack(side="left", padx=3)
        self.subject_tree = self._tree(page, ("subject_id", "subject_code", "subject_name", "credits"), [120, 180, 350, 120])
        self.subject_tree.pack(fill="both", expand=True, pady=10); self.subject_tree.bind("<<TreeviewSelect>>", self.select_subject)
        self.refresh_subjects()

    def _marks_tab(self) -> None:
        page = ttk.Frame(self.tabs, padding=12); self.tabs.add(page, text="Marks & Attendance")
        ttk.Label(page, text="Marks Entry", style="Title.TLabel").pack(anchor="w")
        form = ttk.LabelFrame(page, text="Select student and subject", padding=12); form.pack(fill="x", pady=10)
        self.mark_student = ttk.Combobox(form, state="readonly", width=35); self.mark_student.grid(row=0, column=1, padx=5)
        self.mark_subject = ttk.Combobox(form, state="readonly", width=35); self.mark_subject.grid(row=0, column=3, padx=5)
        ttk.Label(form, text="Student").grid(row=0, column=0); ttk.Label(form, text="Subject").grid(row=0, column=2)
        self.mark_entries: list[tk.Entry] = []
        for i, label in enumerate(("Internal (0-100)", "External (0-100)", "Attendance %")):
            ttk.Label(form, text=label).grid(row=1, column=i * 2, pady=8)
            entry = ttk.Entry(form, width=14); entry.grid(row=1, column=i * 2 + 1); self.mark_entries.append(entry)
        ttk.Button(form, text="Save Marks", command=lambda: self._run(self.save_mark)).grid(row=2, column=0, columnspan=6, pady=6)
        self.refresh_mark_choices()

    def _dashboard_tab(self) -> None:
        page = ttk.Frame(self.tabs, padding=12); self.tabs.add(page, text="Dashboard")
        ttk.Label(page, text="Statistics & Merit List", style="Title.TLabel").pack(anchor="w")
        actions = ttk.Frame(page); actions.pack(anchor="w", pady=8)
        ttk.Button(actions, text="Refresh Dashboard", command=lambda: self._run(self.refresh_dashboard)).pack(side="left")
        ttk.Button(actions, text="Generate Charts", command=lambda: self._run(self.generate_charts)).pack(side="left", padx=5)
        self.stats_label = ttk.Label(page, text="", font=("Segoe UI", 11)); self.stats_label.pack(anchor="w")
        self.rank_tree = self._tree(page, ("rank", "roll_no", "name", "department", "total_marks", "average", "cgpa"), [70, 120, 180, 150, 120, 120, 100])
        self.rank_tree.pack(fill="both", expand=True, pady=10)
        self.refresh_dashboard()

    def _fill_tree(self, tree: ttk.Treeview, rows: list[dict]) -> None:
        tree.delete(*tree.get_children())
        for index, row in enumerate(rows):
            tag = "odd" if index % 2 else ""
            if "status" in row: tag = "pass" if row["status"] == "PASS" else "fail"
            tree.insert("", "end", values=[row.get(column, "") for column in tree["columns"]], tags=(tag,))

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

    def search_students(self, binary: bool = False) -> None:
        results = self.controller.search_students(self.search_field.get(), self.search_query.get(), binary); self._fill_tree(self.student_tree, results)

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
        self._clear(self.mark_entries); messagebox.showinfo("Saved", "Marks and attendance saved."); self.refresh_dashboard()

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
        self.stats_label.config(text=f"Highest: {stats['highest']:.2f}   Lowest: {stats['lowest']:.2f}   Average: {stats['average']:.2f}   Pass: {stats['pass_percentage']:.2f}%   Fail: {stats['fail_percentage']:.2f}%")
        self._fill_tree(self.rank_tree, stats["top_students"])

    def generate_charts(self) -> None:
        paths = StatisticsManager(self.controller).generate_charts()
        messagebox.showinfo("Charts created", "Saved charts:\n" + "\n".join(str(path) for path in paths))
