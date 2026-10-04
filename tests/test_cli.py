import tomllib
from pathlib import Path

import pytest
from typer.testing import CliRunner

from whatsmypaper.main import app
from whatsmypaper.titles import MAX_NAME_LENGTH

runner = CliRunner()

# every character Win32 forbids in a filename
WINDOWS_ILLEGAL = set('<>:"/\\|?*')


def test_version_matches_pyproject():
    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    declared = tomllib.loads(pyproject.read_text())["project"]["version"]

    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == declared


def test_scan_lists_only_auto_generated_names(make_pdf, tmp_path):
    make_pdf("1706.03762v7.pdf")
    make_pdf("Download.pdf")

    result = runner.invoke(app, ["scan", str(tmp_path)])

    assert result.exit_code == 0
    assert "1706.03762v7" in result.stdout
    assert "Download" not in result.stdout


def test_rename_uses_the_title(make_pdf, tmp_path):
    make_pdf("1706.03762v7.pdf", title="Attention Is All You Need")

    result = runner.invoke(app, ["rename", str(tmp_path)])

    assert result.exit_code == 0
    assert (tmp_path / "attention-is-all-you-need.pdf").exists()
    assert not (tmp_path / "1706.03762v7.pdf").exists()


def test_rename_skips_files_scan_would_not_flag(make_pdf, tmp_path):
    make_pdf("Download.pdf", title="Attention Is All You Need")

    runner.invoke(app, ["rename", str(tmp_path)])

    assert (tmp_path / "Download.pdf").exists()


def test_rename_a_single_file_regardless_of_its_name(make_pdf, tmp_path):
    path = make_pdf("Download.pdf", title="Attention Is All You Need")

    result = runner.invoke(app, ["rename", str(path)])

    assert result.exit_code == 0
    assert (tmp_path / "attention-is-all-you-need.pdf").exists()


def test_preview_changes_nothing_on_disk(make_pdf, tmp_path):
    make_pdf("1706.03762v7.pdf", title="Attention Is All You Need")

    result = runner.invoke(app, ["rename", str(tmp_path), "--preview"])

    assert result.exit_code == 0
    assert "attention-is-all-you-need" in result.stdout
    assert (tmp_path / "1706.03762v7.pdf").exists()
    assert not (tmp_path / "attention-is-all-you-need.pdf").exists()


def test_titles_that_collide_get_a_suffix(make_pdf, tmp_path):
    make_pdf("1706.03762v7.pdf", title="Attention Is All You Need")
    make_pdf("2104.00673v4.pdf", title="Attention Is All You Need")

    runner.invoke(app, ["rename", str(tmp_path)])

    assert (tmp_path / "attention-is-all-you-need.pdf").exists()
    assert (tmp_path / "attention-is-all-you-need-2.pdf").exists()


def test_a_pdf_without_a_title_is_skipped_not_fatal(make_pdf, tmp_path):
    tmp_path.joinpath("1111111111.pdf").write_bytes(b"not a PDF")
    make_pdf("2104.00673v4.pdf", title="Attention Is All You Need")

    result = runner.invoke(app, ["rename", str(tmp_path)])

    assert result.exit_code == 0
    assert "skipped" in result.stdout
    # the unreadable file did not stop the batch
    assert (tmp_path / "attention-is-all-you-need.pdf").exists()


def test_camel_case_names_are_not_split(make_pdf, tmp_path):
    make_pdf("1706.03762v7.pdf", title="scDiffusion and AlphaFold")

    runner.invoke(app, ["rename", str(tmp_path)])

    assert (tmp_path / "scdiffusion-and-alphafold.pdf").exists()


def test_long_titles_are_truncated(make_pdf, tmp_path):
    make_pdf("1706.03762v7.pdf", title=" ".join(["word"] * 100))

    runner.invoke(app, ["rename", str(tmp_path)])

    renamed = next(p for p in tmp_path.glob("word*.pdf"))
    assert len(renamed.stem) <= MAX_NAME_LENGTH


@pytest.mark.parametrize(
    "title",
    [
        "BERT: Pre-training of Deep Bidirectional Transformers",
        "What is AI? A survey",
        "Model A/B testing in production",
        'Stars * and pipes | and quotes "here"',
        "Backslash C:\\path weirdness",
        "Trailing dot in version 1.2.",
    ],
)
def test_renamed_files_are_legal_on_windows(make_pdf, tmp_path, title):
    """Titles carry punctuation that Win32 forbids in filenames; it must not survive."""
    make_pdf("1706.03762v7.pdf", title=title)

    runner.invoke(app, ["rename", str(tmp_path)])

    renamed = next(p for p in tmp_path.glob("*.pdf") if p.name != "1706.03762v7.pdf")
    assert not (set(renamed.stem) & WINDOWS_ILLEGAL)
    assert not renamed.stem.endswith((".", " "))
