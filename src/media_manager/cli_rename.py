
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core.renamer import RenamePlannerOptions, build_rename_dry_run, execute_rename_dry_run

DEFAULT_RENAME_TEMPLATE = "{date:%Y-%m-%d_%H-%M-%S}_{stem}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager rename",
        description="Build or execute a rename plan for one or more source folders.",
    )
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
        default=DEFAULT_RENAME_TEMPLATE,
        help=(
            "Rename template. Supports tokens such as {date:%%Y-%%m-%%d_%%H-%%M-%%S}, "
            "{stem}, {suffix}, {year}, {month}, {day}, {hour}, {minute}, {second}, "
            "{year_month}, {year_month_day}, {source_name}, and {index}."
        ),
    )
    parser.add_argument(
        "--non-recursive",
        action="store_true",
        help="Only scan the top level of each source folder.",
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files and hidden folders.",
    )
    parser.add_argument(
        "--show-files",
        action="store_true",
        help="Print individual rename entries in addition to the summary.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    parser.add_argument(
        "--exiftool-path",
        type=Path,
        default=None,
        help="Optional explicit path to the exiftool executable.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply planned rename operations instead of only printing the dry-run plan.",
    )
    return parser


def _build_json_payload(dry_run, execution_result) -> dict[str, object]:
    payload = {
        "template": dry_run.options.template,
        "sources": [str(path) for path in dry_run.options.source_dirs],
        "missing_sources": [str(path) for path in dry_run.scan_summary.missing_sources],
        "media_file_count": dry_run.media_file_count,
        "planned_count": dry_run.planned_count,
        "skipped_count": dry_run.skipped_count,
        "conflict_count": dry_run.conflict_count,
        "error_count": dry_run.error_count,
        "entries": [
            {
                "source_path": str(item.source_path),
                "target_path": None if item.target_path is None else str(item.target_path),
                "rendered_name": item.rendered_name,
                "status": item.status,
                "reason": item.reason,
                "resolved_value": None if item.resolution is None else item.resolution.resolved_value,
                "source_kind": None if item.resolution is None else item.resolution.source_kind,
                "source_label": None if item.resolution is None else item.resolution.source_label,
                "confidence": None if item.resolution is None else item.resolution.confidence,
            }
            for item in dry_run.entries
        ],
    }
    if execution_result is not None:
        payload["execution"] = {
            "apply_requested": execution_result.apply_requested,
            "processed_count": execution_result.processed_count,
            "preview_count": execution_result.preview_count,
            "renamed_count": execution_result.renamed_count,
            "skipped_count": execution_result.skipped_count,
            "conflict_count": execution_result.conflict_count,
            "error_count": execution_result.error_count,
            "entries": [
                {
                    "source_path": str(entry.source_path),
                    "target_path": None if entry.target_path is None else str(entry.target_path),
                    "status": entry.status,
                    "reason": entry.reason,
                    "action": entry.action,
                }
                for entry in execution_result.entries
            ],
        }
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    invalid_sources = [path for path in args.sources if not path.is_dir()]
    if invalid_sources:
        parser.error(
            "The following source directories do not exist or are not directories: "
            + ", ".join(str(path) for path in invalid_sources)
        )

    dry_run = build_rename_dry_run(
        RenamePlannerOptions(
            source_dirs=tuple(args.sources),
            template=args.template,
            recursive=not args.non_recursive,
            include_hidden=args.include_hidden,
            exiftool_path=args.exiftool_path,
        )
    )
    execution_result = execute_rename_dry_run(dry_run, apply=args.apply)

    if args.json:
        print(json.dumps(_build_json_payload(dry_run, execution_result), indent=2, ensure_ascii=False))
        return 0 if execution_result.error_count == 0 and dry_run.missing_source_count == 0 else 1

    title = "Rename apply summary" if args.apply else "Rename dry-run summary"
    print(title)
    print(f"  Sources: {len(dry_run.options.source_dirs)}")
    print(f"  Missing sources: {dry_run.missing_source_count}")
    print(f"  Media files: {dry_run.media_file_count}")
    print(f"  Planned: {dry_run.planned_count}")
    print(f"  Skipped: {dry_run.skipped_count}")
    print(f"  Conflicts: {dry_run.conflict_count}")
    print(f"  Errors: {dry_run.error_count}")

    if args.apply:
        print(f"  Renamed: {execution_result.renamed_count}")

    if args.show_files and execution_result.entries:
        print("\nRename entries:")
        for entry in execution_result.entries:
            target_display = "-" if entry.target_path is None else str(entry.target_path)
            print(
                f"  - [{entry.status}] {entry.source_path} -> {target_display} | {entry.reason}"
            )

    return 0 if execution_result.error_count == 0 and dry_run.missing_source_count == 0 else 1
