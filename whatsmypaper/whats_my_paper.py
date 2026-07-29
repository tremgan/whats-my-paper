
from pathlib import Path
from typing import Iterable
from name_classify import get_pdf_title
from caseconverter import kebabcase
from dataclasses import dataclass



def scan():
    pass


def extract_titles(paths: Iterable[Path], as_dict=False):
    titles = [self.extract_title(path) for path in paths]

    if not as_dict: 
        return titles
    else: 
        return {path: title for path, title in zip(paths, titles)}

def extract_title(path: Path):
    return get_pdf_title(path)


def rename(path: Path, name: str) -> Path:
    new_path = path.parent / f"{name}{path.suffix}"
    path.rename(new_path)
    return new_path


