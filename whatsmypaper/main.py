import typer
from pathlib import Path
from name_classify import numeric_percentage_strategy
from rich import print
from typing import Callable
import whats_my_paper
from caseconverter import kebabcase

app = typer.Typer()



strategy: Callable[[str], bool] = numeric_percentage_strategy


@app.command()
def scan(path: Path):
    """
    Scan a direcotry for 
    """
    for pdf_path in path.glob('*.pdf'):
        name = pdf_path.with_suffix('').name

        flagged = strategy(name)

        if flagged:
            print(name)

@app.command()
def rename(path: Path, yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")):
    title = whats_my_paper.extract_title(path)
    if not title:
        raise ValueError(f"No title found for {path}")
    
    title = kebabcase(title)

    if not yes and not typer.confirm(f"Rename {path.name} -> {title}{path.suffix}?"):
        typer.echo("Aborted.")
        raise typer.Abort()

    whats_my_paper.rename(path=path, name=title)

if __name__ == "__main__":
    app()
