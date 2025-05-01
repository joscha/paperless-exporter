from pathlib import Path
import pytest

from src.cli import validate_paperless_library, validate_empty_or_create


def test_validate_paperless_library_valid():
    # This should not raise
    path = Path("fixtures/library.paperless")
    assert validate_paperless_library(path) == path


def test_validate_paperless_library_invalid(tmp_path):
    # Not a directory
    file_path = tmp_path / "not_a_dir.paperless"
    file_path.write_text("not a dir")
    with pytest.raises(Exception):
        validate_paperless_library(file_path)

    # Directory does not end with .paperless
    bad_dir = tmp_path / "notpaperless"
    bad_dir.mkdir()
    with pytest.raises(Exception):
        validate_paperless_library(bad_dir)

    # Missing DocumentWallet.documentwalletsql
    bad_paperless = tmp_path / "bad.paperless"
    bad_paperless.mkdir()
    with pytest.raises(Exception):
        validate_paperless_library(bad_paperless)


def test_validate_empty_or_create(tmp_path):
    # Directory does not exist: should be created
    new_dir = tmp_path / "newdir"
    assert validate_empty_or_create(new_dir) == new_dir
    assert new_dir.exists() and new_dir.is_dir()

    # Directory exists and is empty: should pass
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    assert validate_empty_or_create(empty_dir) == empty_dir

    # Directory exists and is not empty: should raise
    not_empty = tmp_path / "notempty"
    not_empty.mkdir()
    (not_empty / "file.txt").write_text("something")
    with pytest.raises(Exception):
        validate_empty_or_create(not_empty)

    # Path exists and is a file: should raise
    file_path = tmp_path / "afile"
    file_path.write_text("not a dir")
    with pytest.raises(Exception):
        validate_empty_or_create(file_path)
