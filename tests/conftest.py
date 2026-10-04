import pytest
from pypdf import PdfWriter


@pytest.fixture
def make_pdf(tmp_path):
    """Write a one-page PDF, optionally carrying a title in its metadata."""

    def _make(filename: str, title: str | None = None):
        writer = PdfWriter()
        writer.add_blank_page(width=200, height=200)
        if title is not None:
            writer.add_metadata({"/Title": title})

        path = tmp_path / filename
        with open(path, "wb") as f:
            writer.write(f)
        return path

    return _make
