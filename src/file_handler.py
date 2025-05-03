from pathlib import Path
from shutil import copy
from typing import Dict, Tuple
from .utils import sanitize_filename_for_obsidian, calculate_file_hash


class FileHandler:
    """Handles file operations for document attachments."""

    def __init__(self, out_dir_path: Path, attachments_dir_path: Path):
        self.out_dir_path = out_dir_path
        self.attachments_dir_path = attachments_dir_path
        self.seen_hashes = set()

    def copy_file(self, file_name: str, file_path: Path, prefix: str) -> Path:
        """Copy a file to the attachments directory with a unique name."""
        file_hash = calculate_file_hash(file_path)
        if file_hash in self.seen_hashes:
            return None

        self.seen_hashes.add(file_hash)
        file_out_path = self.attachments_dir_path / sanitize_filename_for_obsidian(
            f"{prefix}.{file_name}{file_path.suffix}"
        )
        copy(file_path, file_out_path)
        return file_out_path.relative_to(self.out_dir_path)

    def copy_files(
        self, files: Dict[str, Path], prefix: str
    ) -> Tuple[Dict[str, Path], Dict[str, Path]]:
        """Copy multiple files to the attachments directory."""
        linked_attachments = {}
        copied_files = {}
        for file_name, file_path in files.items():
            relative_path = self.copy_file(file_name, file_path, prefix)
            if relative_path:
                linked_attachments[file_name] = relative_path
                copied_files[file_name] = file_path
        return linked_attachments, copied_files
