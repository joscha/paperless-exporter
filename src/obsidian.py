from pathlib import Path
from typing import AsyncGenerator, Dict, Generator
import logging
from .model import (
    DataType,
    ReceiptCollection,
    ReceiptTag,
    Zcategory,
    Zcollection,
    Zpaymentmethod,
    Zreceipt,
    Zsubcategory,
    database,
)
from frontmatter import Post, dump
from peewee import fn, SqliteDatabase
from .tag_set import TagSet
from .document_path import DocumentPath
from .file_handler import FileHandler
from .utils import format_datetime_utc, create_out_dir, sanitize_filename_for_obsidian


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


type ReceiptPrimaryKey = int
type NoteName = str


class PaperlessDatabase(SqliteDatabase):
    path_to_paperless_db: Path

    def __init__(self, path_to_paperless_db: Path):
        self.path_to_paperless_db = path_to_paperless_db

    def __enter__(self):
        database.init(self.path_to_paperless_db / "DocumentWallet.documentwalletsql")

    def __exit__(self, exc_type, exc_value, traceback):
        # always close, even if an exception occurred
        database.close()
        # return False so any exception is propagated
        return False


def get_collection_paths(collection: Zcollection) -> list[str]:
    paths = []
    while collection:
        paths.insert(0, collection.zname)
        collection = collection.parent
    return paths


def get_document_title(receipt: Zreceipt):
    title = receipt.zmerchant
    if not title:
        try:
            title = receipt.zcategory.zname
        except Zcategory.DoesNotExist:
            pass
    if not title:
        title = receipt.zoriginalfilename
    if not title:
        title = f"Paperless document {receipt.z_pk}"
    return title


def get_receipts() -> Generator[Zreceipt, None, None]:
    yield from Zreceipt.select()


def get_receipt_max_id() -> int:
    return Zreceipt.select(fn.MAX(Zreceipt.z_pk)).scalar()


class ObsidianItem:
    receipt: Zreceipt
    markdown: Post
    path_to_paperless_db: Path
    document_path: DocumentPath

    def __init__(self, receipt: Zreceipt, path_to_paperless_db: Path):
        self.receipt = receipt
        self.path_to_paperless_db = path_to_paperless_db
        self.document_path = DocumentPath(path_to_paperless_db, receipt)

    def save(
        self, out_dir_path: Path, attachments_dir_path: Path, max_id_length: int
    ) -> NoteName:
        title = self.get_document_title()
        id: ReceiptPrimaryKey = self.receipt.z_pk

        note_name: NoteName = sanitize_filename_for_obsidian(f"{title} ({id})")
        out_file_path = out_dir_path / f"{note_name}.md"
        if out_file_path.exists():
            raise Exception(f"File {out_file_path} already exists")

        padded_id = str(id).zfill(max_id_length)
        receipt_date = format_datetime_utc(self.receipt.zdate, date_only=True)
        prefix = f"{receipt_date}_{padded_id}_{title}"

        original_files = self.document_path.get_all_paths()
        if len(original_files) == 0:
            logger.warning(
                f"No documents exist for receipt '{title}' (Paperless ID: {id}; Document path: {self.document_path.get_document_path()})."
            )
            thumbnail_path = self.document_path.get_thumbnail_path()
            if thumbnail_path and thumbnail_path.exists():
                original_files["thumbnail"] = thumbnail_path

        file_handler = FileHandler(out_dir_path, attachments_dir_path)
        linked_attachments = file_handler.copy_files(original_files, prefix)

        dump(
            self.transform(linked_attachments=linked_attachments),
            out_file_path,
        )
        return note_name

    def get_document_title(self) -> str:
        return get_document_title(self.receipt)

    def transform(self, linked_attachments: Dict[str, Path] = None) -> Post:
        receipt = self.receipt
        content = []
        if receipt.znotes:
            content.append(receipt.znotes.strip())
            content.append("")
            content.append("-----")
        if linked_attachments and len(linked_attachments) > 0:
            for file_name, file_path in linked_attachments.items():
                content.append(f"#### {file_name}")
                content.append(f"![[{file_path}]]")

        markdown = Post(content="\n".join(content))
        tags = TagSet(["paperless"])
        self._set_basic_metadata(markdown)
        self._set_collection_metadata(markdown, tags)
        self._set_category_metadata(markdown, tags)
        self._set_receipt_metadata(markdown)
        self._set_document_metadata(markdown, tags)
        self._set_status_metadata(markdown)

        markdown.metadata["tags"] = set(tags)
        return markdown

    def _set_basic_metadata(self, markdown: Post) -> None:
        """Set basic metadata like filename, dates, and type."""
        if self.receipt.zoriginalfilename:
            markdown.metadata["Original filename"] = self.receipt.zoriginalfilename
        receipt_date = format_datetime_utc(self.receipt.zdate, date_only=True)
        markdown.metadata["Date"] = receipt_date
        markdown.metadata["Import date"] = format_datetime_utc(self.receipt.zimportdate)

        document_type = self.receipt.zdatatype.zname
        if document_type:
            markdown.metadata["Type"] = document_type

    def _set_collection_metadata(self, markdown: Post, tags: TagSet) -> None:
        """Set collection-related metadata and tags."""
        collections = []
        for receipt_collection in self.receipt.collections:
            assert isinstance(receipt_collection, ReceiptCollection)
            if receipt_collection.collection.z_pk == 1:
                # ignore the "Library" collection
                continue
            collection_paths = get_collection_paths(receipt_collection.collection)
            collections.append("/".join(collection_paths))
            tags.update(collection_paths)

        if collections:
            markdown.metadata["Collection paths"] = collections

    def _set_category_metadata(self, markdown: Post, tags: TagSet) -> None:
        """Set category and subcategory metadata and tags."""
        try:
            markdown.metadata["Category"] = self.receipt.zcategory.zname
            tags.add(self.receipt.zcategory.zname)
        except Zcategory.DoesNotExist:
            pass

        try:
            markdown.metadata["Subcategory"] = self.receipt.zsubcategory.zname
            tags.add(self.receipt.zsubcategory.zname)
        except Zsubcategory.DoesNotExist:
            pass

        try:
            markdown.metadata["Payment method"] = self.receipt.zpaymentmethod.zname
        except Zpaymentmethod.DoesNotExist:
            pass

    def _set_receipt_metadata(self, markdown: Post) -> None:
        """Set receipt-specific metadata."""
        if self.receipt.zdatatype.z_pk == DataType.RECEIPT.value:
            markdown.metadata["Amount"] = self.receipt.zamount
            if self.receipt.ztaxamount is not None:
                markdown.metadata["Tax/VAT"] = self.receipt.ztaxamount

    def _set_document_metadata(self, markdown: Post, tags: TagSet) -> None:
        """Set document-specific metadata and tags."""
        document_type = self.receipt.zdatatype.zname

        if self.receipt.zocrattemptedvalue == 1 and self.receipt.zocrresult:
            markdown.metadata["OCR result"] = self.receipt.zocrresult

        document_paths = [
            self.document_path.get_document_path(),
            self.document_path.get_document_path(should_unidecode=True),
        ]
        document_exists = False
        for document_path in document_paths:
            document_exists = document_path.exists()
            if document_exists:
                markdown.metadata["source"] = document_path.absolute().as_uri()
                break

        if document_type:
            tags.add(f"paperless-type-{document_type}")
        if not document_exists:
            tags.add("paperless-document-missing")
        for tag in self.receipt.receipt_tags:
            assert isinstance(tag, ReceiptTag)
            if tag.tag.zname:
                tags.add(tag.tag.zname)

    def _set_status_metadata(self, markdown: Post) -> None:
        """Set status-related metadata."""
        if self.receipt.zinboxvalue == 1:
            markdown.metadata["In inbox"] = True

        if self.receipt.zintrashvalue == 1:
            markdown.metadata["In trash"] = True


class CollectionItem:
    collection: Zcollection
    markdown: Post

    def __init__(self, collection: Zcollection, markdown: Post):
        self.collection = collection
        self.markdown = markdown

    def save(self, collection_md_path: Path):
        if collection_md_path.exists():
            raise Exception(f"Collection file {collection_md_path} already exists")
        dump(self.markdown, collection_md_path)


def get_receipt_count(path_to_paperless_db: Path) -> int:
    with PaperlessDatabase(path_to_paperless_db):
        return Zreceipt.select().count()


async def export(
    path_to_paperless_db: Path, out_dir: Path
) -> AsyncGenerator[ObsidianItem | CollectionItem, None]:
    with PaperlessDatabase(path_to_paperless_db):
        out_dir_path = create_out_dir(out_dir)
        attachments_dir_path = create_out_dir(out_dir_path / "_attachments")

        max_id = get_receipt_max_id()
        logger.debug(f"Max receipt ID: {max_id}")
        max_length = len(str(max_id))

        receipt_to_note_name: Dict[ReceiptPrimaryKey, NoteName] = {}
        receipts = [receipt for receipt in get_receipts()]
        for receipt in receipts:
            obsidian_item = ObsidianItem(receipt, path_to_paperless_db)
            yield obsidian_item
            note_name = obsidian_item.save(
                out_dir_path, attachments_dir_path, max_length
            )
            receipt_to_note_name[receipt.z_pk] = note_name

        for collection in Zcollection.select():
            receipt_collections: list[ReceiptCollection] = collection.receipts
            if not receipt_collections or len(receipt_collections) == 0:
                continue
            collection_path = Path(out_dir_path / "collections")
            paths = get_collection_paths(collection)
            for collection_path_part in paths[:-1]:
                collection_path = collection_path / Path(
                    sanitize_filename_for_obsidian(collection_path_part)
                )
            collection_dir_path = create_out_dir(collection_path)
            collection_md_path = collection_dir_path / Path(
                sanitize_filename_for_obsidian(f"{paths[-1]}.md")
            )
            note_references = [
                receipt_to_note_name[receipt_collection.receipt.z_pk]
                for receipt_collection in receipt_collections
            ]
            content = [f"* [[{note_reference}]]" for note_reference in note_references]
            markdown = Post(content="\n".join(content))
            collection_item = CollectionItem(collection, markdown)
            yield collection_item
            collection_item.save(collection_md_path)
