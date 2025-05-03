from pathlib import Path
import pytest
from syrupy.filters import props

from . import assert_tree_snapshot

from ..obsidian import (
    CollectionItem,
    ObsidianItem,
    OrphanedFileItem,
    export,
)


@pytest.mark.asyncio
async def test_export(tmp_path, snapshot):
    async for item in export(Path("fixtures/library.paperless"), tmp_path):
        if isinstance(item, ObsidianItem):
            assert (
                snapshot(name=f"document_{item.receipt.z_pk}", exclude=props("source"))
                == item.transform(
                    linked_attachments={
                        "document": "linked_attachment.document.pdf",
                        "original": "linked_attachment.original.pdf",
                    }
                ).to_dict()
            )
        elif isinstance(item, CollectionItem):
            assert (
                snapshot(name=f"collection_{item.collection.z_pk}")
                == item.markdown.to_dict()
            )
        elif isinstance(item, OrphanedFileItem):
            assert (
                snapshot(name=f"orphaned_file_{item.file_hash[:8]}")
                == item.transform(
                    {
                        "document": "linked_attachment.document.pdf",
                    },
                    {
                        "document": "copied.file.pdf",
                    },
                ).to_dict()
            )

    assert_tree_snapshot(tmp_path, snapshot(name="tree"))
