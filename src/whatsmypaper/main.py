import typer
from pathlib import Path
from rich import print
from typing import Callable
from . import whats_my_paper
from .titles import MAX_NAME_LENGTH, numeric_percentage_strategy
from caseconverter import kebabcase

app = typer.Typer()



strategy: Callable[[str], bool] = numeric_percentage_strategy


@app.command()
def scan(path: Path):
    """
    Scan a directory for PDFs whose filename looks auto-generated.
    """
    for pdf_path in sorted(path.glob('*.pdf')):
        name = pdf_path.with_suffix('').name

        flagged = strategy(name)

        if flagged:
            print(name)

@app.command()
def rename(
    path: Path,
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be renamed, without renaming"),
):
    """
    Rename a PDF to its title, or every auto-generated-looking PDF in a directory.
    """
    single = not path.is_dir()

    if single:
        pdf_paths = [path]
    else:
        pdf_paths = [p for p in sorted(path.glob('*.pdf')) if strategy(p.with_suffix('').name)]

    claimed: set[Path] = set()
    renamed = 0

    for pdf_path in pdf_paths:
        title = whats_my_paper.extract_title(pdf_path)
        if not title:
            print(f"[yellow]skipped[/yellow] {pdf_path.name}: no title found")
            continue

        name = kebabcase(title)[:MAX_NAME_LENGTH].strip('-')
        new_path = pdf_path.with_name(f"{name}{pdf_path.suffix}")

        if not name or new_path == pdf_path:
            print(f"[yellow]skipped[/yellow] {pdf_path.name}: already named after its title")
            continue

        new_path = whats_my_paper.unique_path(new_path, claimed)
        claimed.add(new_path)

        if not dry_run:
            whats_my_paper.rename(path=pdf_path, new_path=new_path)

        print(f"{pdf_path.name} [dim]->[/dim] {new_path.name}")
        renamed += 1

    if not renamed:
        print("Nothing to rename.")
        raise typer.Exit(code=1 if single else 0)

if __name__ == "__main__":
    app()
