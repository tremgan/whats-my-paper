import re
from pathlib import Path
from typing import Optional

from pypdf import PdfReader
from rich import print

# guards against path.rename() failing with "File name too long" when the parse
# fallback returns a paragraph instead of a title
MAX_NAME_LENGTH = 120


def numeric_percentage_strategy(name: str, threshold: float=3/4) -> bool:
    if not name:
        return False

    digit_count = sum(1 for char in name if char.isdigit())
    return digit_count/len(name) >= threshold


def get_pdf_title(path: Path) -> Optional[str]:
    title = get_pdf_title_from_metadata(path=path)
    if title:
        return title

    title = get_pdf_title_from_parse(path=path)
    if title:
        return title

    return None


def get_pdf_title_from_metadata(path: Path) -> Optional[str]:
    try:
        reader = PdfReader(path)
    except Exception:
        return None

    if not reader.metadata:
        return None

    return clean(reader.metadata.title)


def get_pdf_title_from_parse(path: Path) -> Optional[str]:
    # imported here so that scan, --help and the metadata path don't pay for it
    from docling.datamodel.pipeline_options import LayoutOptions
    from docling.document_converter import DocumentConverter
    from huggingface_hub.constants import HF_HUB_CACHE

    # docling pulls its weights from the Hugging Face hub cache on first use
    cache_dir = Path(HF_HUB_CACHE)
    repo_id = LayoutOptions().model_spec.repo_id
    if not (cache_dir / f"models--{repo_id.replace('/', '--')}").exists():
        print(f"[yellow]Downloading docling model weights[/yellow] [dim]->[/dim] {cache_dir}")
        print("[dim]This happens once; later runs reuse the cache.[/dim]")

    converter = DocumentConverter()
    try:
        result = converter.convert(path, page_range=(1, 2)) # only first page is needed to infer title
    except Exception:
        return None
    doc = result.document

    # the heuristic is that the title is the section with the most words, works suprisingly well
    def n_words(text: str):
        return len(text.split())

    title = max((item.text
                for item, _ in doc.iterate_items()
                if item.label in ["title", "section_header"]),
                key=n_words,
                default=None
               )

    return clean(title)


def clean(title: Optional[str]) -> Optional[str]:
    """Collapse the newlines and non-breaking spaces that PDF titles carry."""
    if not title:
        return None

    return re.sub(r"\s+", " ", title.replace("\xa0", " ")).strip() or None
