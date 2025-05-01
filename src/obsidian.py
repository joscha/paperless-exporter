import hashlib
from pathlib import Path
from shutil import copy
from typing import AsyncGenerator, Dict, Generator
import logging
from datetime import datetime
from pathvalidate import sanitize_filename
from unidecode import unidecode
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


# see https://forum.obsidian.md/t/valid-characters-for-file-names/55307/3
OBSIDIAN_SPECIAL_CHARACTERS = list("[]#^|\\/:?")


def sanitize_filename_for_obsidian(file_name: str) -> str:
    """
    Sanitize a filename for Obsidian by replacing special characters with underscores.
    """
    for char in OBSIDIAN_SPECIAL_CHARACTERS:
        file_name = file_name.replace(char, "_")
    file_name = sanitize_filename(file_name, replacement_text="_")
    # Remove any leading or trailing underscores
    file_name = file_name.strip("_")
    # Remove any double underscores
    while "__" in file_name:
        file_name = file_name.replace("__", "_")
    return file_name


def get_collection_paths(collection: Zcollection) -> str:
    paths = []
    while collection:
        paths.insert(0, collection.zname)
        collection = collection.parent
    return paths


def create_out_dir(dir_path: str | Path):
    if isinstance(dir_path, str):
        dir_path = Path(dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_document_path(
    path_to_paperless_db: Path, receipt: Zreceipt, should_unidecode: bool = False
):
    file_name = receipt.zpath
    if should_unidecode:
        file_name = unidecode(file_name)
    return path_to_paperless_db / Path(file_name)


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


def format_datetime_utc(dt: datetime, date_only: bool = False) -> str:
    return dt.date().isoformat() if date_only else dt.isoformat()


class ObsidianItem:
    receipt: Zreceipt
    markdown: Post
    path_to_paperless_db: Path

    def __init__(self, receipt: Zreceipt, path_to_paperless_db: Path):
        self.receipt = receipt
        self.path_to_paperless_db = path_to_paperless_db

    def save(
        self, out_dir_path: Path, attachments_dir_path: Path, max_id_length: int
    ) -> NoteName:
        title = self.get_document_title()
        id: ReceiptPrimaryKey = self.receipt.z_pk

        note_name: NoteName = sanitize_filename_for_obsidian(f"{title} ({id})")
        out_file_path = out_dir_path / f"{note_name}.md"
        if out_file_path.exists():
            raise Exception(f"File {out_file_path} already exists")

        document_path = self.get_document_path()
        original_document_path = self.get_original_document_path()
        padded_id = str(id).zfill(max_id_length)
        receipt_date = format_datetime_utc(self.receipt.zdate, date_only=True)
        prefix = f"{receipt_date}_{padded_id}_{title}"

        original_files = {
            "document": document_path,
            "document.unidecode": self.get_document_path(should_unidecode=True),
            "original": original_document_path,
        }
        original_files = {
            k: v for k, v in original_files.items() if v is not None and v.exists()
        }

        if len(original_files) == 0:
            logger.warning(
                f"No documents exist for receipt '{title}' (Paperless ID: {id}; Document path: {document_path})."
            )
            thumbnail_path = self.get_thumbnail_path()
            if thumbnail_path and thumbnail_path.exists():
                original_files["thumbnail"] = thumbnail_path

        linked_attachments = {}
        seen_hashes = set()
        for file_name, file_path in original_files.items():
            file_hash = hashlib.md5(file_path.read_bytes()).hexdigest()
            if file_hash in seen_hashes:
                continue
            seen_hashes.add(file_hash)
            file_out_path = attachments_dir_path / sanitize_filename_for_obsidian(
                f"{prefix}.{file_name}{file_path.suffix}"
            )
            copy(file_path, file_out_path)
            linked_attachments[file_name] = file_out_path.relative_to(out_dir_path)
        dump(
            self.transform(linked_attachments=linked_attachments),
            out_file_path,
        )
        return note_name

    def get_document_path(self, should_unidecode: bool = False) -> Path:
        return get_document_path(
            self.path_to_paperless_db, self.receipt, should_unidecode
        )

    def get_original_document_path(self) -> Path | None:
        if self.receipt.zoriginalfilename:
            document_path = get_document_path(self.path_to_paperless_db, self.receipt)
            document_file_name = document_path.name
            document_file_name_without_extension = document_file_name.rsplit(".", 1)[0]
            original_document_path = (
                document_path.parent
                / document_file_name_without_extension
                / self.receipt.zoriginalfilename
            )
            return original_document_path
        return None

    def get_thumbnail_path(self) -> Path | None:
        if self.receipt.zthumbnailpath:
            return self.path_to_paperless_db / Path(self.receipt.zthumbnailpath)
        return None

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
        if receipt.zoriginalfilename:
            markdown.metadata["Original filename"] = receipt.zoriginalfilename
        receipt_date = format_datetime_utc(self.receipt.zdate, date_only=True)
        markdown.metadata["Date"] = receipt_date
        markdown.metadata["Import date"] = format_datetime_utc(receipt.zimportdate)

        document_type = receipt.zdatatype.zname
        if document_type:
            markdown.metadata["Type"] = document_type

        collections = []
        for receipt_collection in receipt.collections:
            assert isinstance(receipt_collection, ReceiptCollection)
            collections.append(
                "/".join(get_collection_paths(receipt_collection.collection))
            )

        if collections:
            markdown.metadata["Collection paths"] = collections

        try:
            markdown.metadata["Category"] = receipt.zcategory.zname
        except Zcategory.DoesNotExist:
            pass

        try:
            markdown.metadata["Subcategory"] = receipt.zsubcategory.zname
        except Zsubcategory.DoesNotExist:
            pass

        try:
            markdown.metadata["Payment method"] = receipt.zpaymentmethod.zname
        except Zpaymentmethod.DoesNotExist:
            pass

        if receipt.zdatatype.z_pk == DataType.RECEIPT.value:
            markdown.metadata["Amount"] = receipt.zamount
            if receipt.ztaxamount is not None:
                markdown.metadata["Tax/VAT"] = receipt.ztaxamount

        if receipt.zocrattemptedvalue == 1 and receipt.zocrresult:
            markdown.metadata["OCR result"] = receipt.zocrresult

        tags = ["paperless"]

        document_paths = [
            self.get_document_path(),
            self.get_document_path(should_unidecode=True),
        ]
        document_exists = False
        for document_path in document_paths:
            document_exists = document_path.exists()
            if document_exists:
                markdown.metadata["source"] = document_path.absolute().as_uri()
                break

        if document_type:
            tags.append(f"paperless-type-{document_type.strip().lower()}")
        if not document_exists:
            tags.append("paperless-document-missing")
        for tag in receipt.receipt_tags:
            assert isinstance(tag, ReceiptTag)
            if tag.tag.zname:
                tags.append(tag.tag.zname.strip().lower())
        if tags:
            markdown.metadata["tags"] = tags

        if receipt.zinboxvalue == 1:
            markdown.metadata["In inbox"] = True

        if receipt.zintrashvalue == 1:
            markdown.metadata["In trash"] = True

        return markdown


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


class ExportResult:
    documents: list[ObsidianItem] = []
    collection_items: list[CollectionItem] = []


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
