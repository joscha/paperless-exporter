import sys
import subprocess
from pathlib import Path

from . import assert_tree_snapshot


def test_cli_generates_expected_tree(tmp_path, snapshot):
    source = Path("fixtures/library.paperless")
    target = tmp_path / "out"
    result = subprocess.run(
        [sys.executable, "-m", "src.cli", str(source), str(target)],
        capture_output=True,
        text=True,
    )
    # Optionally print result.stdout/result.stderr for debugging
    assert snapshot(name="stdout") == result.stdout
    assert snapshot(name="stderr") == result.stderr
    assert_tree_snapshot(target, snapshot(name="generated_tree"))
