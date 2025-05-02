from pathlib import Path
from typing import Optional
from .utils import get_document_path
from .model import Zreceipt


class DocumentPath:
    """Handles all path-related operations for a document."""

    def __init__(self, path_to_paperless_db: Path, receipt: Zreceipt):
        self.path_to_paperless_db = path_to_paperless_db
        self.receipt = receipt

    def get_document_path(self, should_unidecode: bool = False) -> Path:
        """Get the path to the document file."""
        return get_document_path(
            self.path_to_paperless_db, self.receipt, should_unidecode
        )

    def get_original_document_path(self) -> Optional[Path]:
        """Get the path to the original document file."""
        if not self.receipt.zoriginalfilename:
            return None

        document_path = self.get_document_path()
        document_file_name = document_path.name
        document_file_name_without_extension = document_file_name.rsplit(".", 1)[0]
        return (
            document_path.parent
            / document_file_name_without_extension
            / self.receipt.zoriginalfilename
        )

    def get_thumbnail_path(self) -> Optional[Path]:
        """Get the path to the thumbnail file."""
        if not self.receipt.zthumbnailpath:
            return None
        return self.path_to_paperless_db / Path(self.receipt.zthumbnailpath)

    def get_all_paths(self) -> dict[str, Path]:
        """Get all possible document paths."""
        paths = {
            "document": self.get_document_path(),
            "document.unidecode": self.get_document_path(should_unidecode=True),
            "original": self.get_original_document_path(),
        }
        return {k: v for k, v in paths.items() if v is not None and v.exists()}
