import argparse
import sys
from pathlib import Path
import asyncio
from tqdm.asyncio import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from .obsidian import (
    CollectionItem,
    ObsidianItem,
    OrphanedFileItem,
    check_orphaned_files,
    export,
    get_receipt_count,
    get_collection_with_receipts_count,
    find_orphaned_files,
)


def validate_paperless_library(path: Path) -> Path:
    if not path.exists() or not path.is_dir():
        raise argparse.ArgumentTypeError(
            f"Source path '{path}' does not exist or is not a directory."
        )
    if not str(path).endswith(".paperless"):
        raise argparse.ArgumentTypeError("Source directory must end with '.paperless'.")
    if not (path / "DocumentWallet.documentwalletsql").exists():
        raise argparse.ArgumentTypeError(
            "Source directory does not contain 'DocumentWallet.documentwalletsql'."
        )
    return path


def validate_empty_or_create(path: Path) -> Path:
    if path.exists():
        if not path.is_dir():
            raise argparse.ArgumentTypeError(
                f"Target path '{path}' exists and is not a directory."
            )
        if any(path.iterdir()):
            raise argparse.ArgumentTypeError(f"Target directory '{path}' is not empty.")
    else:
        path.mkdir(parents=True, exist_ok=True)
    return path


def main():
    parser = argparse.ArgumentParser(
        description="Export a Mariner Paperless library to an Obsidian-compatible Markdown library."
    )
    parser.add_argument(
        "source",
        type=lambda p: validate_paperless_library(Path(p)),
        help="Path to the Paperless library (must end in '.paperless' and contain 'DocumentWallet.documentwalletsql').",
    )
    parser.add_argument(
        "target",
        nargs="?",
        type=lambda p: validate_empty_or_create(Path(p)),
        help="Path to the output folder (must not exist or must be empty). Required unless --check-orphans is used.",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress bar during export.",
    )
    parser.add_argument(
        "--check-orphans",
        action="store_true",
        help="Check for orphaned files in the Paperless library.",
    )

    args = parser.parse_args()

    if args.check_orphans:
        check_orphaned_files(args.source)
        return

    if not args.target:
        parser.error("target argument is required unless --check-orphans is used")

    async def run_export():
        count = get_receipt_count(args.source)
        if count == 0:
            print("No receipts found in the source library.", file=sys.stderr)  # noqa T201
            sys.exit(1)
        print(f"Found {count} receipts to export.")  # noqa T201

        # Get count of orphaned files
        orphaned_files = find_orphaned_files(args.source)
        orphaned_count = len(orphaned_files)
        if orphaned_count > 0:
            print(f"Found {orphaned_count} orphaned files to export.")  # noqa T201

        generator = export(args.source, args.target)
        if args.no_progress:
            async for _ in generator:
                pass
        else:
            with logging_redirect_tqdm():
                # Create progress bars
                document_progress = tqdm(
                    total=count,
                    desc="Exporting documents",
                    unit="document",
                    disable=args.no_progress,
                )
                collection_progress = tqdm(
                    total=get_collection_with_receipts_count(args.source),
                    desc="Linking documents to collections",
                    unit="collection",
                    disable=args.no_progress,
                )
                orphaned_progress = tqdm(
                    total=orphaned_count,
                    desc="Exporting orphaned files",
                    unit="file",
                    disable=args.no_progress,
                )

                async for item in generator:
                    if isinstance(item, ObsidianItem):
                        document_progress.update()
                    elif isinstance(item, CollectionItem):
                        document_progress.total = document_progress.n
                        document_progress.refresh()
                        collection_progress.update()
                    elif isinstance(item, OrphanedFileItem):
                        collection_progress.total = collection_progress.n
                        collection_progress.refresh()
                        orphaned_progress.update()

                orphaned_progress.total = orphaned_progress.n
                orphaned_progress.refresh()
                document_progress.close()
                collection_progress.close()
                orphaned_progress.close()

    # Run the export
    try:
        asyncio.run(run_export())
        print("Export completed successfully.")  # noqa T201
    except Exception as e:
        print(f"Export failed: {e}", file=sys.stderr)  # noqa T201
        sys.exit(1)


if __name__ == "__main__":
    main()
