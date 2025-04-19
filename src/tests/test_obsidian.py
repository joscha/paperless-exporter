from pathlib import Path

from ..obsidian import export


def test_export():
    export(Path("fixtures/library.paperless"), Path("fixtures/out"))
    assert True
