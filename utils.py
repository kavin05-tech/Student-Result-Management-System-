"""Reusable UI and filesystem helpers."""
from pathlib import Path


def project_path(*parts: str) -> Path:
    """Return a path relative to this application directory."""
    return Path(__file__).resolve().parent.joinpath(*parts)


def ensure_reports_dir() -> Path:
    """Create and return the report export directory."""
    directory = project_path("reports")
    directory.mkdir(exist_ok=True)
    return directory
