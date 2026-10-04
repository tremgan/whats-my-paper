import pytest

from whatsmypaper.titles import clean, get_pdf_title_from_metadata, numeric_percentage_strategy


@pytest.mark.parametrize("name", ["1706.03762v7", "2104.00673v4", "978-1-61779-582-4", "12345"])
def test_flags_auto_generated_names(name):
    assert numeric_percentage_strategy(name)


@pytest.mark.parametrize(
    "name", ["Download", "attention-is-all-you-need", "", "paper2", "v105i09"]
)
def test_leaves_human_names_alone(name):
    assert not numeric_percentage_strategy(name)


def test_threshold_is_inclusive():
    # 3 digits out of 4 characters is exactly the default 3/4
    assert numeric_percentage_strategy("123a")
    assert not numeric_percentage_strategy("12ab")


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Attention Is All\nYou Need", "Attention Is All You Need"),
        ("Non\xa0breaking\xa0spaces", "Non breaking spaces"),
        ("  padded  and   spaced  ", "padded and spaced"),
        ("", None),
        ("   ", None),
        (None, None),
    ],
)
def test_clean(raw, expected):
    assert clean(raw) == expected


def test_reads_title_from_metadata(make_pdf):
    path = make_pdf("1706.03762v7.pdf", title="Attention Is All You Need")
    assert get_pdf_title_from_metadata(path) == "Attention Is All You Need"


def test_collapses_newlines_in_metadata_title(make_pdf):
    path = make_pdf("x.pdf", title="Attention Is\nAll You Need")
    assert get_pdf_title_from_metadata(path) == "Attention Is All You Need"


def test_untitled_pdf_has_no_metadata_title(make_pdf):
    assert get_pdf_title_from_metadata(make_pdf("x.pdf")) is None


def test_unreadable_file_is_not_an_error(tmp_path):
    junk = tmp_path / "junk.pdf"
    junk.write_bytes(b"this is not a PDF")
    assert get_pdf_title_from_metadata(junk) is None
