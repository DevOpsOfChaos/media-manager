from __future__ import annotations

import argparse
import json
from pathlib import Path

from .constants import MEDIA_EXTENSIONS
from .core.date_resolver import resolve_capture_datetime
from .core.metadata import inspect_media_file
from .core.scanner import ScanOptions, scan_media_sources


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



def _build_payload(records) -> list[dict[str, object]]:
    return [
        {
            "path": str(record["inspection"].path),
            "selected_value": record["inspection"].selected_value,
            "selected_source": record["inspection"].selected_source,
            "file_modified_value": record["inspection"].file_modified_value,
            "metadata_available": record["inspection"].metadata_available,
            "exiftool_available": record["inspection"].exiftool_available,
            "metadata_tag_count": record["inspection"].metadata_tag_count,
            "metadata_error_kind": record["inspection"].metadata_error_kind,
            "error": record["inspection"].error,
            "date_candidates": [
                {
                    "source_tag": candidate.source_tag,
                    "value": candidate.value,
                    "priority_index": candidate.priority_index,
                }
                for candidate in record["inspection"].date_candidates
            ],
            "resolution": {
                "resolved_value": record["resolution"].resolved_value,
                "source_kind": record["resolution"].source_kind,
                "source_label": record["resolution"].source_label,
                "confidence": record["resolution"].confidence,
                "timezone_status": record["resolution"].timezone_status,
                "reason": record["resolution"].reason,
                "candidates_checked": record["resolution"].candidates_checked,
            },
        }
        for record in records
    ]


def _build_summary(records) -> dict[str, int]:
    summary = {"metadata": 0, "filename": 0, "file_system": 0, "warnings": 0}
    for record in records:
        inspection = record["inspection"]
        resolution = record["resolution"]
        summary[resolution.source_kind] = summary.get(resolution.source_kind, 0) + 1
        if inspection.error or inspection.metadata_error_kind:
            summary["warnings"] += 1
    return summary



def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    exiftool_path = Path(args.exiftool) if args.exiftool else None
    targets, directories = _collect_targets(
        args.paths,
        recursive=not args.non_recursive,
        include_hidden=args.include_hidden,
        limit=args.limit,
    )

    records = []
    for path in targets:
        inspection = inspect_media_file(path, exiftool_path=exiftool_path)
        resolution = resolve_capture_datetime(path, inspection=inspection, exiftool_path=exiftool_path)
        records.append({"inspection": inspection, "resolution": resolution})

    if args.json:
        print(json.dumps({"summary": _build_summary(records), "files": _build_payload(records)}, indent=2, ensure_ascii=False))
        return 0 if records else 1

    if not records:
        print("No media files found to inspect.")
        return 1

    summary = _build_summary(records)

    if directories:
        print(f"Scanned {len(directories)} director{'y' if len(directories) == 1 else 'ies'} and selected {len(records)} file(s) for inspection.")
        print()

    print(
        "Inspect summary: "
        f"metadata={summary.get('metadata', 0)} | "
        f"filename={summary.get('filename', 0)} | "
        f"file_system={summary.get('file_system', 0)} | "
        f"warnings={summary.get('warnings', 0)}"
    )
    print()

    for record in records:
        item = record["inspection"]
        resolution = record["resolution"]
        print(item.path)
        print(f"  Resolved:           {resolution.resolved_value}")
        print(f"  Source:             {resolution.source_kind}:{resolution.source_label}")
        print(f"  Confidence:         {resolution.confidence}")
        print(f"  Timezone:           {resolution.timezone_status}")
        print(f"  Fallback:           {item.file_modified_value}")
        print(f"  Metadata tags:      {item.metadata_tag_count}")
        print(f"  Metadata available: {item.metadata_available}")
        print(f"  ExifTool available: {item.exiftool_available}")
        print(f"  Reason:             {resolution.reason}")
        if item.metadata_error_kind:
            print(f"  Metadata issue:     {item.metadata_error_kind}")
        if item.error:
            print(f"  Error:              {item.error}")
        if item.date_candidates:
            print("  Candidates:")
            for candidate in item.date_candidates:
                print(f"    - [{candidate.priority_index}] {candidate.source_tag}: {candidate.value}")
        else:
            print("  Candidates: none")
        print()

    return 0
