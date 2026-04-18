from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core.organizer import DEFAULT_ORGANIZE_PATTERN
from .core.state import write_command_run_log
from .core.workflows import (
    DEFAULT_CLEANUP_RENAME_TEMPLATE,
    CleanupWorkflowOptions,
    build_cleanup_workflow_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager cleanup",
        description="Build a guided cleanup workflow report across scan, duplicates, organize, and rename.",
    )
    parser.add_argument(
        "--source",
        dest="sources",
        action="append",
        type=Path,
        required=True,
        help="Source directory. Repeat the flag to add multiple source folders.",
    )
    parser.add_argument("--target", type=Path, required=True, help="Target directory root for organize planning.")
    parser.add_argument(
        "--organize-pattern",
        default=DEFAULT_ORGANIZE_PATTERN,
        help="Organize pattern used for the embedded organize dry-run section.",
    )
    parser.add_argument(
        "--rename-template",
        default=DEFAULT_CLEANUP_RENAME_TEMPLATE,
        help="Rename template used for the embedded rename dry-run section.",
    )
    parser.add_argument(
        "--duplicate-policy",
        choices=["first", "newest", "oldest"],
        help="Optional keep-selection policy for exact duplicate planning.",
    )
    parser.add_argument(
        "--duplicate-mode",
        choices=["copy", "move", "delete"],
        default="copy",
        help="Interpret duplicate decisions for copy, move, or delete planning. Default: copy.",
    )
    parser.add_argument("--non-recursive", action="store_true", help="Only scan the top level of each source folder.")
    parser.add_argument("--include-hidden", action="store_true", help="Include hidden files and hidden folders.")
    parser.add_argument("--show-files", action="store_true", help="Print detailed workflow section entries.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    parser.add_argument("--run-log", type=Path, help="Optional JSON run-log path for this cleanup workflow command.")
    parser.add_argument(
        "--exiftool-path",
        type=Path,
        default=None,
        help="Optional explicit path to the exiftool executable.",
    )
    return parser


def _build_payload(report) -> dict[str, object]:
    return {
        "sources": [str(path) for path in report.options.source_dirs],
        "target_root": str(report.options.target_root),
        "organize_pattern": report.options.organize_pattern,
        "rename_template": report.options.rename_template,
        "duplicate_policy": report.options.duplicate_policy,
        "duplicate_mode": report.options.duplicate_mode,
        "scan": {
            "missing_sources": [str(path) for path in report.scan_summary.missing_sources],
            "media_file_count": report.media_file_count,
            "skipped_hidden_paths": report.scan_summary.skipped_hidden_paths,
            "skipped_non_media_files": report.scan_summary.skipped_non_media_files,
        },
        "duplicates": {
            "exact_groups": len(report.duplicate_scan_result.exact_groups),
            "duplicate_files": report.duplicate_scan_result.exact_duplicate_files,
            "extra_duplicates": report.duplicate_scan_result.exact_duplicates,
            "errors": report.duplicate_scan_result.errors,
            "decisions_count": report.decisions_count,
            "resolved_groups": report.duplicate_workflow.cleanup_plan.resolved_groups,
            "unresolved_groups": report.duplicate_workflow.cleanup_plan.unresolved_groups,
            "planned_removals": len(report.duplicate_workflow.cleanup_plan.planned_removals),
            "estimated_reclaimable_bytes": report.duplicate_workflow.cleanup_plan.estimated_reclaimable_bytes,
        },
        "organize": {
            "planned_count": report.organize_plan.planned_count,
            "skipped_count": report.organize_plan.skipped_count,
            "conflict_count": report.organize_plan.conflict_count,
            "error_count": report.organize_plan.error_count,
        },
        "rename": {
            "planned_count": report.rename_dry_run.planned_count,
            "skipped_count": report.rename_dry_run.skipped_count,
            "conflict_count": report.rename_dry_run.conflict_count,
            "error_count": report.rename_dry_run.error_count,
        },
    }


def _print_detailed_sections(report) -> None:
    if report.duplicate_scan_result.exact_groups:
        print("\nDuplicate groups:")
        for index, group in enumerate(report.duplicate_scan_result.exact_groups, start=1):
            print(f"  [{index}] files={len(group.files)} size={group.file_size} bytes")
            for path in group.files:
                print(f"    - {path}")

    if report.organize_plan.entries:
        print("\nOrganize entries:")
        for entry in report.organize_plan.entries:
            target_text = str(entry.target_path) if entry.target_path else "-"
            print(f"  - [{entry.status}] {entry.source_path} -> {target_text} | {entry.reason}")

    if report.rename_dry_run.entries:
        print("\nRename entries:")
        for entry in report.rename_dry_run.entries:
            target_text = str(entry.target_path) if entry.target_path else "-"
            print(f"  - [{entry.status}] {entry.source_path} -> {target_text} | {entry.reason}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    invalid_sources = [path for path in args.sources if not path.is_dir()]
    if invalid_sources:
        parser.error(
            "The following source directories do not exist or are not directories: "
            + ", ".join(str(path) for path in invalid_sources)
        )

    report = build_cleanup_workflow_report(
        CleanupWorkflowOptions(
            source_dirs=tuple(args.sources),
            target_root=args.target,
            organize_pattern=args.organize_pattern,
            rename_template=args.rename_template,
            recursive=not args.non_recursive,
            include_hidden=args.include_hidden,
            duplicate_policy=args.duplicate_policy,
            duplicate_mode=args.duplicate_mode,
            exiftool_path=args.exiftool_path,
        )
    )
    payload = _build_payload(report)
    exit_code = 0 if not report.has_errors else 1

    if args.run_log is not None:
        write_command_run_log(
            args.run_log,
            command_name="cleanup",
            apply_requested=False,
            exit_code=exit_code,
            payload=payload,
        )

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return exit_code

    print("Cleanup workflow summary")
    print(f"  Sources: {len(report.options.source_dirs)}")
    print(f"  Missing sources: {report.missing_source_count}")
    print(f"  Media files: {report.media_file_count}")
    print("\nDuplicates")
    print(f"  Exact groups: {len(report.duplicate_scan_result.exact_groups)}")
    print(f"  Duplicate files: {report.duplicate_scan_result.exact_duplicate_files}")
    print(f"  Extra duplicates: {report.duplicate_scan_result.exact_duplicates}")
    print(f"  Decisions: {report.decisions_count}")
    print(f"  Resolved groups: {report.duplicate_workflow.cleanup_plan.resolved_groups}")
    print(f"  Unresolved groups: {report.duplicate_workflow.cleanup_plan.unresolved_groups}")
    print("\nOrganize")
    print(f"  Planned: {report.organize_plan.planned_count}")
    print(f"  Skipped: {report.organize_plan.skipped_count}")
    print(f"  Conflicts: {report.organize_plan.conflict_count}")
    print(f"  Errors: {report.organize_plan.error_count}")
    print("\nRename")
    print(f"  Planned: {report.rename_dry_run.planned_count}")
    print(f"  Skipped: {report.rename_dry_run.skipped_count}")
    print(f"  Conflicts: {report.rename_dry_run.conflict_count}")
    print(f"  Errors: {report.rename_dry_run.error_count}")

    if args.show_files:
        _print_detailed_sections(report)

    return exit_code
