from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core.metadata import inspect_media_file
from .core.scanner import ScanOptions, scan_media_sources
from .constants import MEDIA_EXTENSIONS



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager inspect",
        description="Inspect capture-date candidates for media files or folders.",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="One or more media files or source folders.",
    )
    parser.add_argument(
        "--exiftool",
        help="Optional explicit path to exiftool.",
    )
    parser.add_argument(
        "--non-recursive",
        action="store_true",
        help="Only scan the top level of directory inputs.",
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files and folders when scanning directories.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of inspected files when directory inputs are used.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    return parser



def _collect_targets(paths: list[str], *, recursive: bool, include_hidden: bool, limit: int) -> tuple[list[Path], list[Path]]:
    files: list[Path] = []
    directories: list[Path] = []

    for raw_path in paths:
        path = Path(raw_path).expanduser()
        if path.is_dir():
            directories.append(path)
            continue
        if path.is_file() and path.suffix.lower() in MEDIA_EXTENSIONS:
            files.append(path)

    if directories:
        summary = scan_media_sources(
            ScanOptions(
                source_dirs=tuple(directories),
                recursive=recursive,
                include_hidden=include_hidden,
            )
        )
        files.extend(item.path for item in summary.files)

    unique_files: list[Path] = []
    seen: set[str] = set()
    for file_path in files:
        key = str(file_path).lower()
        if key in seen:
            continue
        seen.add(key)
        unique_files.append(file_path)

    return unique_files[: max(0, limit)], directories



def _build_payload(inspections) -> list[dict[str, object]]:
    return [
        {
            "path": str(item.path),
            "selected_value": item.selected_value,
            "selected_source": item.selected_source,
            "file_modified_value": item.file_modified_value,
            "metadata_available": item.metadata_available,
            "exiftool_available": item.exiftool_available,
            "error": item.error,
            "date_candidates": [
                {
                    "source_tag": candidate.source_tag,
                    "value": candidate.value,
                    "priority_index": candidate.priority_index,
                }
                for candidate in item.date_candidates
            ],
        }
        for item in inspections
    ]



def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    targets, directories = _collect_targets(
        args.paths,
        recursive=not args.non_recursive,
        include_hidden=args.include_hidden,
        limit=args.limit,
    )

    inspections = [inspect_media_file(path, exiftool_path=Path(args.exiftool) if args.exiftool else None) for path in targets]

    if args.json:
        print(json.dumps(_build_payload(inspections), indent=2, ensure_ascii=False))
        return 0 if inspections else 1

    if not inspections:
        print("No media files found to inspect.")
        return 1

    if directories:
        print(f"Scanned {len(directories)} director{'y' if len(directories) == 1 else 'ies'} and selected {len(inspections)} file(s) for inspection.")
        print()

    for item in inspections:
        print(item.path)
        print(f"  Selected: {item.selected_value}")
        print(f"  Source:   {item.selected_source}")
        print(f"  Fallback: {item.file_modified_value}")
        if item.error:
            print(f"  Error:    {item.error}")
        if item.date_candidates:
            print("  Candidates:")
            for candidate in item.date_candidates:
                print(f"    - [{candidate.priority_index}] {candidate.source_tag}: {candidate.value}")
        else:
            print("  Candidates: none")
        print()

    return 0
