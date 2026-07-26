import typer
from pathlib import Path
from name_classify import numeric_percentage_strategy
from rich import print
from typing import Callable
from whats_my_paper_repository import WMPRepository
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
def rename(path: Path):

    title = WMPRepository().extract_title(path)
    if not title: 
        return ValueError(f'No title found for {path}')

    title = kebabcase(title)

    
    WMPRepository().rename(path=path, name=title)

if __name__ == "__main__":
    app()
