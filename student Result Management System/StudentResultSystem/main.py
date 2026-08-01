"""Application entry point."""
from pathlib import Path
import tkinter as tk

from controller import Controller
from database import DatabaseManager
from gui import ApplicationGUI


def main() -> None:
    """Launch the desktop application."""
    root = tk.Tk()
    database = DatabaseManager(Path(__file__).with_name("student_results.db"))
    ApplicationGUI(root, Controller(database))
    root.protocol("WM_DELETE_WINDOW", lambda: (database.close(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()
