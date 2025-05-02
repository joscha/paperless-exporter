import argparse
import sys
from pathlib import Path
import asyncio
from tqdm.asyncio import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from .obsidian import export, get_receipt_count


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
        type=lambda p: validate_empty_or_create(Path(p)),
        help="Path to the output folder (must not exist or must be empty).",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress bar during export.",
    )

    args = parser.parse_args()

    async def run_export():
        count = get_receipt_count(args.source)
        if count == 0:
            print("No receipts found in the source library.", file=sys.stderr)  # noqa T201
            sys.exit(1)
        print(f"Found {count} receipts to export.")  # noqa T201

        generator = export(args.source, args.target)
        if args.no_progress:
            async for _ in generator:
                pass
        else:
            with logging_redirect_tqdm():
                async for _ in tqdm(generator, total=count, desc="Exporting"):
                    pass

    # Run the export
    try:
        asyncio.run(run_export())
        print("Export completed successfully.")  # noqa T201
    except Exception as e:
        print(f"Export failed: {e}", file=sys.stderr)  # noqa T201
        sys.exit(1)


if __name__ == "__main__":
    main()
