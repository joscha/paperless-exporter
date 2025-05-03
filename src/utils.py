import unicodedata
from pathlib import Path
from pathvalidate import sanitize_filename
from datetime import datetime
import hashlib

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


_umlaut_map = str.maketrans(
    {
        "ä": "ae",
        "Ä": "Ae",
        "ö": "oe",
        "Ö": "Oe",
        "ü": "ue",
        "Ü": "Ue",
        "ß": "ss",
    }
)


def german_to_ascii(s: str) -> str:
    # 1) normalize so that any combining forms become precomposed
    s = unicodedata.normalize("NFC", s)
    # 2) transliterate via our map
    return s.translate(_umlaut_map)


def unidecode_filename(file_name: str) -> str:
    # Mariner Paperless follows the German rules for Umlauts
    file_name = german_to_ascii(file_name)
    return file_name


def get_document_path(
    path_to_paperless_db: Path, receipt, should_unidecode: bool = False
) -> Path:
    file_name = receipt.zpath
    if should_unidecode:
        file_name = unidecode_filename(file_name)
    return path_to_paperless_db / Path(file_name)


def format_datetime_utc(dt: datetime, date_only: bool = False) -> str:
    return dt.date().isoformat() if date_only else dt.isoformat()


def create_out_dir(dir_path: str | Path) -> Path:
    if isinstance(dir_path, str):
        dir_path = Path(dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def calculate_file_hash(file_path: Path) -> str:
    """Calculate the MD5 hash of a file."""
    return hashlib.md5(file_path.read_bytes()).hexdigest()
