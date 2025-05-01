import sys
import subprocess
from pathlib import Path

from . import get_tree_string_from_path


def assert_tree_snapshot(tmp_path, snapshot):
    tree_str = get_tree_string_from_path(tmp_path)
    assert snapshot == tree_str


def test_cli_generates_expected_tree(tmp_path, snapshot):
    source = Path("fixtures/library.paperless")
    target = tmp_path / "out"
    result = subprocess.run(
        [sys.executable, "-m", "src.cli", str(source), str(target)],
        capture_output=True,
        text=True,
    )
    # Optionally print result.stdout/result.stderr for debugging
    snapshot(name="stdout") == result.stdout
    snapshot(name="stderr") == result.stderr
    assert_tree_snapshot(target, snapshot(name="generated_tree"))
