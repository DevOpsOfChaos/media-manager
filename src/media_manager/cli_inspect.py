from __future__ import annotations

import argparse
import json
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


def _count_by_label(values: list[str]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for value in values:
        summary[value] = summary.get(value, 0) + 1
    return dict(sorted(summary.items()))


def _record_candidate_stats(inspection) -> tuple[list[dict[str, object]], int, int]:
    rows: list[dict[str, object]] = []
    parseable_count = 0
    unparseable_count = 0
    for candidate in inspection.date_candidates:
        parseable = parse_datetime_value(candidate.value) is not None
        if parseable:
            parseable_count += 1
        else:
            unparseable_count += 1
        rows.append(
            {
                "source_tag": candidate.source_tag,
                "value": candidate.value,
                "priority_index": candidate.priority_index,
                "parseable": parseable,
            }
        )
    return rows, parseable_count, unparseable_count


def _build_summary(records) -> dict[str, object]:
    source_kinds: list[str] = []
    confidences: list[str] = []
    timezone_statuses: list[str] = []
    metadata_error_kinds: list[str] = []
    decision_policies: list[str] = []
    metadata_available_count = 0
    exiftool_available_count = 0
    warning_count = 0
    metadata_conflict_count = 0
    parseable_candidate_count = 0
    unparseable_candidate_count = 0

    for record in records:
        inspection = record["inspection"]
        resolution = record["resolution"]
        source_kinds.append(str(resolution.source_kind))
        confidences.append(str(resolution.confidence))
        timezone_statuses.append(str(resolution.timezone_status))
        policy = getattr(resolution, "decision_policy", None)
        if policy:
            decision_policies.append(str(policy))
        if getattr(resolution, "metadata_conflict", False):
            metadata_conflict_count += 1
        if inspection.metadata_available:
            metadata_available_count += 1
        if inspection.exiftool_available:
            exiftool_available_count += 1
        error_kind = getattr(inspection, "metadata_error_kind", None)
        if error_kind:
            metadata_error_kinds.append(str(error_kind))
        if inspection.error:
            warning_count += 1
        parseable_candidate_count += record["parseable_candidate_count"]
        unparseable_candidate_count += record["unparseable_candidate_count"]

    summary: dict[str, object] = {
        "total_files": len(records),
        "metadata_available_count": metadata_available_count,
        "exiftool_available_count": exiftool_available_count,
        "warning_count": warning_count,
        "source_kind_summary": _count_by_label(source_kinds),
        "confidence_summary": _count_by_label(confidences),
        "timezone_status_summary": _count_by_label(timezone_statuses),
        "metadata_error_kind_summary": _count_by_label(metadata_error_kinds),
        "decision_policy_summary": _count_by_label(decision_policies),
        "metadata_conflict_count": metadata_conflict_count,
        "parseable_candidate_count": parseable_candidate_count,
        "unparseable_candidate_count": unparseable_candidate_count,
        # backward-compatible keys
        "metadata": _count_by_label([item for item in source_kinds if item == "metadata"]).get("metadata", 0),
        "filename": _count_by_label([item for item in source_kinds if item == "filename"]).get("filename", 0),
        "file_system": _count_by_label([item for item in source_kinds if item == "file_system"]).get("file_system", 0),
        "warnings": warning_count,
    }
    return summary


def _build_payload(records) -> dict[str, object]:
    items = []
    for record in records:
        inspection = record["inspection"]
        resolution = record["resolution"]
        items.append(
            {
                "path": str(inspection.path),
                "selected_value": inspection.selected_value,
                "selected_source": inspection.selected_source,
                "file_modified_value": inspection.file_modified_value,
                "metadata_available": inspection.metadata_available,
                "exiftool_available": inspection.exiftool_available,
                "metadata_tag_count": getattr(inspection, "metadata_tag_count", 0),
                "metadata_error_kind": getattr(inspection, "metadata_error_kind", None),
                "error": inspection.error,
                "parseable_candidate_count": record["parseable_candidate_count"],
                "unparseable_candidate_count": record["unparseable_candidate_count"],
                "date_candidates": record["candidate_rows"],
                "resolution": {
                    "resolved_value": resolution.resolved_value,
                    "source_kind": resolution.source_kind,
                    "source_label": resolution.source_label,
                    "confidence": resolution.confidence,
                    "timezone_status": resolution.timezone_status,
                    "reason": resolution.reason,
                    "candidates_checked": resolution.candidates_checked,
                    "decision_policy": getattr(resolution, "decision_policy", None),
                    "metadata_conflict": getattr(resolution, "metadata_conflict", False),
                    "parseable_candidate_count": getattr(resolution, "parseable_candidate_count", record["parseable_candidate_count"]),
                    "unparseable_candidate_count": getattr(resolution, "unparseable_candidate_count", record["unparseable_candidate_count"]),
                },
            }
        )
    return {
        "summary": _build_summary(records),
        "files": items,
    }


def _print_summary_block(title: str, summary: dict[str, int]) -> None:
    if not summary:
        return
    print(title)
    for key, value in summary.items():
        print(f"  {key}: {value}")


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
        candidate_rows, parseable_count, unparseable_count = _record_candidate_stats(inspection)
        records.append(
            {
                "inspection": inspection,
                "resolution": resolution,
                "candidate_rows": candidate_rows,
                "parseable_candidate_count": parseable_count,
                "unparseable_candidate_count": unparseable_count,
            }
        )

    payload = _build_payload(records)

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0 if records else 1

    if not records:
        print("No media files found to inspect.")
        return 1

    if directories:
        print(f"Scanned {len(directories)} director{'y' if len(directories) == 1 else 'ies'} and selected {len(records)} file(s) for inspection.")
        print()

    summary = payload["summary"]
    print("Inspect summary")
    print(f"  Total files: {summary['total_files']}")
    print(f"  Metadata available: {summary['metadata_available_count']}")
    print(f"  ExifTool available: {summary['exiftool_available_count']}")
    print(f"  Warnings: {summary['warning_count']}")
    print(f"  Metadata conflicts: {summary['metadata_conflict_count']}")
    print(f"  Parseable candidates: {summary['parseable_candidate_count']}")
    print(f"  Unparseable candidates: {summary['unparseable_candidate_count']}")
    if summary["decision_policy_summary"]:
        compact = ", ".join(f"{key}={value}" for key, value in summary["decision_policy_summary"].items())
        print(f"Decision policies: {compact}")
    _print_summary_block("\nSource kinds", summary["source_kind_summary"])
    _print_summary_block("\nConfidence summary", summary["confidence_summary"])
    _print_summary_block("\nTimezone summary", summary["timezone_status_summary"])
    _print_summary_block("\nDecision policies", summary["decision_policy_summary"])
    _print_summary_block("\nMetadata error kinds", summary["metadata_error_kind_summary"])
    print()

    for record in records:
        item = record["inspection"]
        resolution = record["resolution"]
        print(item.path)
        print(f"  Resolved:   {resolution.resolved_value}")
        print(f"  Source:     {resolution.source_kind}:{resolution.source_label}")
        print(f"  Confidence: {resolution.confidence}")
        print(f"  Timezone:   {resolution.timezone_status}")
        print(f"  Fallback:   {item.file_modified_value}")
        print(f"  Reason:     {resolution.reason}")
        print(f"  Policy:     {getattr(resolution, 'decision_policy', '-')}")
        print(f"  Conflict:   {getattr(resolution, 'metadata_conflict', False)}")
        print(f"Metadata conflict:  {getattr(resolution, 'metadata_conflict', False)}")
        if item.error:
            print(f"  Error:      {item.error}")
        if record["candidate_rows"]:
            print("  Candidates:")
            for candidate in record["candidate_rows"]:
                parseable_marker = "parseable" if candidate["parseable"] else "unparseable"
                print(f"    - [{candidate['priority_index']}] {candidate['source_tag']}: {candidate['value']} ({parseable_marker})")
        else:
            print("  Candidates: none")
        print()

    return 0
