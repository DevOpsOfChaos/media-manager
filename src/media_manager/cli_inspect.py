from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from .constants import MEDIA_EXTENSIONS
from .core.date_resolver import parse_datetime_value, resolve_capture_datetime
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


def _candidate_parse_counts(inspection) -> tuple[int, int]:
    parseable = 0
    unparseable = 0
    for candidate in inspection.date_candidates:
        if parse_datetime_value(candidate.value) is None:
            unparseable += 1
        else:
            parseable += 1
    return parseable, unparseable


def _build_payload(records) -> list[dict[str, object]]:
    payload: list[dict[str, object]] = []
    for record in records:
        inspection = record["inspection"]
        resolution = record["resolution"]
        parseable_candidates, unparseable_candidates = _candidate_parse_counts(inspection)
        payload.append(
            {
                "path": str(inspection.path),
                "selected_value": inspection.selected_value,
                "selected_source": inspection.selected_source,
                "file_modified_value": inspection.file_modified_value,
                "metadata_available": inspection.metadata_available,
                "exiftool_available": inspection.exiftool_available,
                "metadata_tag_count": inspection.metadata_tag_count,
                "metadata_error_kind": inspection.metadata_error_kind,
                "error": inspection.error,
                "parseable_candidate_count": parseable_candidates,
                "unparseable_candidate_count": unparseable_candidates,
                "date_candidates": [
                    {
                        "source_tag": candidate.source_tag,
                        "value": candidate.value,
                        "priority_index": candidate.priority_index,
                        "parseable": parse_datetime_value(candidate.value) is not None,
                    }
                    for candidate in inspection.date_candidates
                ],
                "resolution": {
                    "resolved_value": resolution.resolved_value,
                    "source_kind": resolution.source_kind,
                    "source_label": resolution.source_label,
                    "confidence": resolution.confidence,
                    "timezone_status": resolution.timezone_status,
                    "reason": resolution.reason,
                    "candidates_checked": resolution.candidates_checked,
                },
            }
        )
    return payload


def _build_summary(records) -> dict[str, object]:
    source_kind_summary: Counter[str] = Counter()
    confidence_summary: Counter[str] = Counter()
    timezone_status_summary: Counter[str] = Counter()
    metadata_error_kind_summary: Counter[str] = Counter()

    metadata_available_count = 0
    exiftool_available_count = 0
    warning_count = 0
    parseable_candidate_count = 0
    unparseable_candidate_count = 0

    for record in records:
        inspection = record["inspection"]
        resolution = record["resolution"]
        source_kind_summary[resolution.source_kind] += 1
        confidence_summary[resolution.confidence] += 1
        timezone_status_summary[resolution.timezone_status] += 1
        if inspection.metadata_available:
            metadata_available_count += 1
        if inspection.exiftool_available:
            exiftool_available_count += 1
        if inspection.error or inspection.metadata_error_kind:
            warning_count += 1
        if inspection.metadata_error_kind:
            metadata_error_kind_summary[inspection.metadata_error_kind] += 1
        parseable, unparseable = _candidate_parse_counts(inspection)
        parseable_candidate_count += parseable
        unparseable_candidate_count += unparseable

    source_kind_dict = dict(source_kind_summary)
    return {
        "total_files": len(records),
        "metadata_available_count": metadata_available_count,
        "exiftool_available_count": exiftool_available_count,
        "warning_count": warning_count,
        "metadata": source_kind_dict.get("metadata", 0),
        "filename": source_kind_dict.get("filename", 0),
        "file_system": source_kind_dict.get("file_system", 0),
        "warnings": warning_count,
        "source_kind_summary": source_kind_dict,
        "confidence_summary": dict(confidence_summary),
        "timezone_status_summary": dict(timezone_status_summary),
        "metadata_error_kind_summary": dict(metadata_error_kind_summary),
        "parseable_candidate_count": parseable_candidate_count,
        "unparseable_candidate_count": unparseable_candidate_count,
    }


def _print_counter_block(label: str, counter: dict[str, int]) -> None:
    if not counter:
        print(f"{label}: none")
        return
    rendered = " | ".join(f"{key}={value}" for key, value in sorted(counter.items()))
    print(f"{label}: {rendered}")


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

    print(f"Inspect summary: total={summary['total_files']} | metadata-available={summary['metadata_available_count']} | exiftool-available={summary['exiftool_available_count']} | warnings={summary['warning_count']}")
    _print_counter_block("  Resolution sources", summary["source_kind_summary"])
    _print_counter_block("  Confidence summary", summary["confidence_summary"])
    _print_counter_block("  Timezone summary", summary["timezone_status_summary"])
    _print_counter_block("  Metadata issues", summary["metadata_error_kind_summary"])
    print(f"  Candidate parseability: parseable={summary['parseable_candidate_count']} | unparseable={summary['unparseable_candidate_count']}")
    print()

    for record in records:
        item = record["inspection"]
        resolution = record["resolution"]
        parseable_candidates, unparseable_candidates = _candidate_parse_counts(item)
        print(item.path)
        print(f"  Resolved:           {resolution.resolved_value}")
        print(f"  Source:             {resolution.source_kind}:{resolution.source_label}")
        print(f"  Confidence:         {resolution.confidence}")
        print(f"  Timezone:           {resolution.timezone_status}")
        print(f"  Fallback:           {item.file_modified_value}")
        print(f"  Metadata tags:      {item.metadata_tag_count}")
        print(f"  Metadata available: {item.metadata_available}")
        print(f"  ExifTool available: {item.exiftool_available}")
        print(f"  Candidate parsing:  parseable={parseable_candidates} | unparseable={unparseable_candidates}")
        print(f"  Reason:             {resolution.reason}")
        if item.metadata_error_kind:
            print(f"  Metadata issue:     {item.metadata_error_kind}")
        if item.error:
            print(f"  Error:              {item.error}")
        if item.date_candidates:
            print("  Candidates:")
            for candidate in item.date_candidates:
                parseable = parse_datetime_value(candidate.value) is not None
                parse_state = "parseable" if parseable else "unparseable"
                print(f"    - [{candidate.priority_index}] {candidate.source_tag}: {candidate.value} ({parse_state})")
        else:
            print("  Candidates: none")
        print()

    return 0
