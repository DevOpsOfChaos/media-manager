from __future__ import annotations

import argparse
from pathlib import Path

from .duplicates import DuplicateScanConfig, scan_exact_duplicates
from .sorter import SortConfig, organize_media


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="media-manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    organize = subparsers.add_parser("organize", help="Sort media files by resolved date")
    organize.add_argument(
        "--source",
        dest="sources",
        action="append",
        type=Path,
        required=True,
        help="Source directory. Repeat the flag to add multiple source folders.",
    )
    organize.add_argument(
        "--target",
        type=Path,
        required=True,
        help="Target directory",
    )
    organize.add_argument(
        "--template",
        default="{year}/{month}",
        help="Target path template relative to the target directory (default: {year}/{month})",
    )
    mode_group = organize.add_mutually_exclusive_group()
    mode_group.add_argument("--copy", action="store_true", help="Copy files instead of moving them")
    mode_group.add_argument("--move", action="store_true", help="Move files instead of copying them")
    organize.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes. Without this flag, a dry-run preview is performed.",
    )
    organize.add_argument(
        "--exiftool-path",
        type=Path,
        default=None,
        help="Optional explicit path to the exiftool executable",
    )

    duplicates = subparsers.add_parser("duplicates", help="Scan exact duplicate media files")
    duplicates.add_argument(
        "--source",
        dest="sources",
        action="append",
        type=Path,
        required=True,
        help="Source directory. Repeat the flag to add multiple source folders.",
    )
    duplicates.add_argument(
        "--show-groups",
        action="store_true",
        help="Print all confirmed exact duplicate groups.",
    )

    return parser


def _print_duplicate_groups(result) -> None:
    for index, group in enumerate(result.exact_groups, start=1):
        same_name = "yes" if group.same_name else "no"
        same_suffix = "yes" if group.same_suffix else "no"
        print(
            f"\n[Group {index}] size={group.file_size} bytes | files={len(group.files)} | "
            f"same-name={same_name} | same-suffix={same_suffix}"
        )
        for path in group.files:
            print(f" - {path}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "organize":
        invalid_sources = [path for path in args.sources if not path.is_dir()]
        if invalid_sources:
            parser.error(
                "The following source directories do not exist or are not directories: "
                + ", ".join(str(path) for path in invalid_sources)
            )
        args.target.mkdir(parents=True, exist_ok=True)

        mode = "copy"
        if args.move:
            mode = "move"

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

    if args.command == "duplicates":
        invalid_sources = [path for path in args.sources if not path.is_dir()]
        if invalid_sources:
            parser.error(
                "The following source directories do not exist or are not directories: "
                + ", ".join(str(path) for path in invalid_sources)
            )

        result = scan_exact_duplicates(DuplicateScanConfig(source_dirs=args.sources))
        print(
            f"Scanned: {result.scanned_files} | Size candidates: {result.size_candidate_files} | "
            f"Hashed: {result.hashed_files} | Exact groups: {len(result.exact_groups)} | "
            f"Duplicate files: {result.exact_duplicate_files} | Extra duplicates: {result.exact_duplicates} | Errors: {result.errors}"
        )
        if args.show_groups and result.exact_groups:
            _print_duplicate_groups(result)
        return 0 if result.errors == 0 else 1

    parser.error("Unknown command")
    return 2
