from __future__ import annotations

import argparse
from pathlib import Path

from .duplicates import DuplicateScanConfig, scan_exact_duplicates


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="media-manager duplicates")
    parser.add_argument(
        "--source",
        dest="sources",
        action="append",
        type=Path,
        required=True,
        help="Source directory. Repeat the flag to add multiple source folders.",
    )
    parser.add_argument(
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
