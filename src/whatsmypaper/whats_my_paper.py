from pathlib import Path
from typing import Iterable

from .titles import get_pdf_title


def extract_title(path: Path):
    return get_pdf_title(path)


# Win32 reserves these as device names, and the extension doesn't help: con.pdf
# is as unusable as con. Applied on every platform so a renamed folder stays
# portable, and with a trailing underscore because the -2 suffix below means
# "this name was taken".
WINDOWS_RESERVED_NAMES = frozenset(
    ["con", "prn", "aux", "nul"]
    + [f"com{i}" for i in range(1, 10)]
    + [f"lpt{i}" for i in range(1, 10)]
)


def safe_stem(stem: str) -> str:
    """Return stem, or stem_ if Windows would refuse to create a file called that."""
    return f"{stem}_" if stem.lower() in WINDOWS_RESERVED_NAMES else stem


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
