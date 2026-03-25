from __future__ import annotations

import argparse
from pathlib import Path

from .sorter import SortConfig, organize_media


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="media-manager organize")
    parser.add_argument(
        "--source",
        dest="sources",
        action="append",
        type=Path,
        required=True,
        help="Source directory. Repeat the flag to add multiple source folders.",
    )
    parser.add_argument("--target", type=Path, required=True, help="Target directory")
    parser.add_argument(
        "--template",
        default="{year}/{month}",
        help="Target path template relative to the target directory (default: {year}/{month})",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--copy", action="store_true", help="Copy files instead of moving them")
    mode_group.add_argument("--move", action="store_true", help="Move files instead of copying them")
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

    args.target.mkdir(parents=True, exist_ok=True)
    mode = "move" if args.move else "copy"
    config = SortConfig(
        source_dirs=args.sources,
        target_dir=args.target,
        target_template=args.template,
        dry_run=not args.apply,
        mode=mode,
        exiftool_path=args.exiftool_path,
    )
    results = organize_media(config)
    print(
        f"Processed: {results.processed} | Planned/Executed: {results.organized} | "
        f"Skipped: {results.skipped} | Errors: {results.errors}"
    )
    return 0 if results.errors == 0 else 1
