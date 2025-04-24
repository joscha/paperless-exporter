from pathlib import Path
import pytest
from syrupy.filters import props

from . import get_tree_string_from_path

from ..obsidian import export


def assert_tree_snapshot(tmp_path, snapshot):
    tree_str = get_tree_string_from_path(tmp_path)
    assert snapshot == tree_str


@pytest.mark.asyncio
async def test_export(tmp_path, snapshot):
    async for item in export(Path("fixtures/library.paperless"), tmp_path):
        snapshot(name=item.receipt.z_pk, exclude=props("source")) == item.transform(
            linked_attachments=[
                "linked_attachment.document.pdf",
                "linked_attachment.original.pdf",
            ]
        ).to_dict()
    # You can use the following to see the output and open it in Obsidian:
    # async for item in export(Path("fixtures/library.paperless"), Path("fixtures/out")):
    #     pass

    assert_tree_snapshot(tmp_path, snapshot(name="tree"))
