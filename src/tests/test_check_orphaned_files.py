from pathlib import Path
from ..obsidian import check_orphaned_files


def test_orphaned_files_found(snapshot, capsys):
    check_orphaned_files(Path("fixtures/library.paperless"))

    captured = capsys.readouterr()
    assert snapshot == captured.err
