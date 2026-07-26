import marimo

__generated_with = "0.23.15"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    from collections import Counter
    import string
    from pathlib import Path
    from pypdf import PdfReader
    from typing import Optional
    from rich import print
    from docling.document_converter import DocumentConverter
    from docling_core.types.doc import DocItemLabel
    from caseconverter import kebabcase


@app.function
def numeric_percentage_strategy(string: str, threshold: float=3/4) -> bool:
    digit_count = sum(1 for char in string if char in string.digits)
    return digit_count/len(string) >= threshold


@app.function
def get_pdf_title(path: Path) -> Optional[str]:
    title = get_pdf_title_from_metadata(path=path)
    if title:
        return title

    title = get_pdf_title_from_parse(path=path)
    if title:
        return title

    return None


@app.function
def get_pdf_title_from_metadata(path: Path) -> Optional[str]:
    reader = PdfReader(path)    
    
    if not reader.metadata:
        return None

    if not reader.metadata.title: 
        return None

    return reader.metadata.title


@app.function
def get_pdf_title_from_parse(path: Path) -> Optional[str]:

    converter = DocumentConverter()
    result = converter.convert(path, page_range=(1, 2)) # only first page is needed to infer title
    doc = result.document

    # the heuristic is that the title is the section with the most words, works suprisingly well
    def n_words(text: str):
        return len(text.split())
    
    title = max((item.text
                for item, _ in doc.iterate_items()
                if item.label in ["title", "section_header"]),
                key=n_words
               )

    return title


@app.cell
def _():
    examples_path = Path('examples')

    print(list(examples_path.glob('*.pdf')))

    titles = []
    for file in examples_path.glob('*.pdf'):
        name = file.with_suffix('').name

        title = get_pdf_title(file)
        print(f'{name=}, {title=}')

        titles.append(title)



    return (titles,)


@app.cell
def _(titles):
    [kebabcase(t) for t in titles]
    return


if __name__ == "__main__":
    app.run()
