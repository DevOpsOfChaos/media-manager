from __future__ import annotations

import argparse
from pathlib import Path

from .renamer import RenameConfig, rename_media


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="media-manager rename")
    parser.add_argument(
        "--source",
        dest="sources",
        action="append",
        type=Path,
        required=True,
        help="Source directory. Repeat the flag to add multiple source folders.",
    )
    parser.add_argument(
        "--template",
        default="{day}.{month}.{year}-{hour}-{minute}-{second}-{stem}{suffix}",
        help="Rename template for media files.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes. Without this flag, a dry-run preview is performed.",
    )
    parser.add_argument(
        "--exiftool-path",
        type=Path,
        default=None,
        help="Optional explicit path to the exiftool executable",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    invalid_sources = [path for path in args.sources if not path.is_dir()]
    if invalid_sources:
        parser.error(
            "The following source directories do not exist or are not directories: "
            + ", ".join(str(path) for path in invalid_sources)
        )

    config = RenameConfig(
        source_dirs=args.sources,
        template=args.template,
        dry_run=not args.apply,
        exiftool_path=args.exiftool_path,
    )
    results = rename_media(config)
    print(
        f"Processed: {results.processed} | Planned/Executed: {results.renamed} | "
        f"Skipped: {results.skipped} | Errors: {results.errors}"
    )
    return 0 if results.errors == 0 else 1
