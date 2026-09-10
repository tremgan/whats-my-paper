from pathlib import Path
from typing import Iterable

from .titles import get_pdf_title


def extract_title(path: Path):
    return get_pdf_title(path)


def unique_path(path: Path, claimed: Iterable[Path] = ()) -> Path:
    """Return path, or path-2 / path-3 / ... if it is already taken."""
    claimed = set(claimed)

    candidate = path
    counter = 2
    while candidate.exists() or candidate in claimed:
        candidate = path.with_name(f"{path.stem}-{counter}{path.suffix}")
        counter += 1

    return candidate


def rename(path: Path, new_path: Path) -> Path:
    path.rename(new_path)
    return new_path
