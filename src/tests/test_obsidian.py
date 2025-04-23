from pathlib import Path

from . import get_tree_string_from_path

from ..obsidian import export


def assert_tree_snapshot(tmp_path, snapshot):
    tree_str = get_tree_string_from_path(tmp_path)
    assert snapshot == tree_str


def test_export(tmp_path, snapshot):
    export(Path("fixtures/library.paperless"), tmp_path)
    # You can use the following to see the output and open it in Obsidian:
    # export(Path("fixtures/library.paperless"), Path("fixtures/out"))
    assert_tree_snapshot(tmp_path, snapshot)
