import pytest

from whatsmypaper.whats_my_paper import safe_stem, unique_path


def test_leaves_a_free_path_alone(tmp_path):
    path = tmp_path / "paper.pdf"
    assert unique_path(path) == path


def test_suffixes_an_existing_file(tmp_path):
    path = tmp_path / "paper.pdf"
    path.touch()
    assert unique_path(path).name == "paper-2.pdf"


def test_keeps_counting_past_the_first_clash(tmp_path):
    (tmp_path / "paper.pdf").touch()
    (tmp_path / "paper-2.pdf").touch()
    assert unique_path(tmp_path / "paper.pdf").name == "paper-3.pdf"


def test_avoids_names_claimed_but_not_yet_written(tmp_path):
    # the batch reserves names before renaming, so two papers sharing a title
    # don't both resolve to the same destination
    path = tmp_path / "paper.pdf"
    assert unique_path(path, claimed={path}).name == "paper-2.pdf"


def test_keeps_the_suffix(tmp_path):
    path = tmp_path / "paper.pdf"
    path.touch()
    assert unique_path(path).suffix == ".pdf"


@pytest.mark.parametrize("reserved", ["con", "CON", "Nul", "prn", "aux", "com1", "lpt9"])
def test_reserved_windows_device_names_are_escaped(reserved):
    assert safe_stem(reserved) == f"{reserved}_"


@pytest.mark.parametrize("ordinary", ["attention", "com", "com10", "console", "lpt", "nullable"])
def test_ordinary_names_are_untouched(ordinary):
    assert safe_stem(ordinary) == ordinary
