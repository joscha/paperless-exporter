from pathlib import Path
import pytest
from syrupy.filters import props

from . import assert_tree_snapshot

from ..obsidian import (
    CollectionItem,
    ObsidianItem,
    export,
    german_to_ascii,
    unidecode_filename,
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
            assert snapshot(name=f"collection_{item.collection.z_pk}") == item.markdown

    assert_tree_snapshot(tmp_path, snapshot(name="tree"))


def test_unidecode():
    assert german_to_ascii("Geburtstagsgrüße") == "Geburtstagsgruesse"
    assert (
        unidecode_filename(
            "sparhandy 2012-05-25  BASE Internet-Flat (500MB) für effektiv 0,21€ pro Monat inkl. UMTS-Stick - myDealZ.de — myDealZ.de - 25.05.12.pdf"
        )
        == "sparhandy 2012-05-25  BASE Internet-Flat (500MB) fuer effektiv 0,21€ pro Monat inkl. UMTS-Stick - myDealZ.de — myDealZ.de - 25.05.12.pdf"
    )
