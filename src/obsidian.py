import hashlib
from pathlib import Path
from shutil import copy
from typing import Dict, Generator

from pathvalidate import sanitize_filename
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


def get_collection_paths(collection: Zcollection) -> str:
    paths = []
    while collection:
        paths.insert(0, collection.zname)
        collection = collection.parent
    return " / ".join(paths)


def create_out_dir(dir_path: str | Path):
    p = Path(dir_path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_document_path(path_to_paperless_db: Path, receipt: Zreceipt):
    return path_to_paperless_db / Path(receipt.zpath)


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


def get_receipts(path_to_paperless_db: Path) -> Generator[Zreceipt, None, None]:
    database.init(path_to_paperless_db / "DocumentWallet.documentwalletsql")
    try:
        yield from Zreceipt.select()
    finally:
        database.close()


async def export(path_to_paperless_db: Path, out_dir: Path):
    out_dir_path = create_out_dir(out_dir)
    attachments_dir_path = create_out_dir(out_dir_path / "_attachments")

    for receipt in get_receipts(path_to_paperless_db):
        obsidian_item = ObsidianItem(receipt, path_to_paperless_db)
        yield obsidian_item
        obsidian_item.save(out_dir_path, attachments_dir_path)


class ObsidianItem:
    receipt: Zreceipt
    markdown: Post
    path_to_paperless_db: Path

    def __init__(self, receipt: Zreceipt, path_to_paperless_db: Path):
        self.receipt = receipt
        self.path_to_paperless_db = path_to_paperless_db

    def save(self, out_dir_path: Path, attachments_dir_path: Path):
        title = self.get_document_title()
        id = self.receipt.z_pk
        out_file_path = out_dir_path / sanitize_filename(f"{title}.md")
        if out_file_path.exists():
            out_file_path = out_dir_path / sanitize_filename(f"{title} ({id}).md")
            if out_file_path.exists():
                raise Exception(f"File {out_file_path} already exists")

        document_path = self.get_document_path()
        original_document_path = self.get_original_document_path()
        prefix = f"{self.receipt.zdate.strftime("%Y-%m-%d")}_{title}_{id}"

        original_files = {
            "document": document_path,
            "original": original_document_path,
        }
        original_files = {
            k: v for k, v in original_files.items() if v is not None and v.exists()
        }
        if len(original_files) == 0:
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
            file_out_path = attachments_dir_path / sanitize_filename(
                f"{prefix}.{file_name}{file_path.suffix}"
            )
            copy(file_path, file_out_path)
            linked_attachments[file_name] = file_out_path.relative_to(out_dir_path)
        dump(
            self.transform(linked_attachments=linked_attachments),
            out_file_path,
        )

    def get_document_path(self) -> Path:
        return get_document_path(self.path_to_paperless_db, self.receipt)

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
        document_path = self.get_document_path()
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
        markdown.metadata["Date"] = receipt.zdate.strftime("%Y-%m-%d")
        markdown.metadata["Import date"] = (
            receipt.zimportdate.isoformat()
        )  # .astimezone().replace(microsecond=0).isoformat()
        markdown.metadata["Type"] = receipt.zdatatype.zname

        collections = []
        for receipt_collection in receipt.collections:
            assert isinstance(receipt_collection, ReceiptCollection)
            collections.append(get_collection_paths(receipt_collection.collection))

        if collections:
            markdown.metadata["Collections"] = collections

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

        document_exists = document_path.exists()

        tags = ["paperless"]
        if not document_exists:
            tags.append("missing-document")
        for tag in receipt.receipt_tags:
            assert isinstance(tag, ReceiptTag)
            if tag.tag.zname:
                tags.append(tag.tag.zname.strip().lower())
        if tags:
            markdown.metadata["tags"] = tags

        if document_exists:
            markdown.metadata["source"] = document_path.absolute().as_uri()

        if receipt.zinboxvalue == 1:
            markdown.metadata["In inbox"] = True

        if receipt.zintrashvalue == 1:
            markdown.metadata["In trash"] = True

        return markdown
