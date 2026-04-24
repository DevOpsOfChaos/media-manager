from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core.organizer import DEFAULT_ORGANIZE_PATTERN
from .core.state import write_command_run_log
from .core.workflows import (
    DEFAULT_CLEANUP_RENAME_TEMPLATE,
    CleanupExecutionReport,
    CleanupWorkflowOptions,
    build_cleanup_workflow_report,
    execute_cleanup_workflow,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager cleanup",
        description="Build or execute a guided cleanup workflow across scan, duplicates, organize, and rename.",
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
        help="Organize pattern used for the embedded organize plan.",
    )
    parser.add_argument(
        "--rename-template",
        default=DEFAULT_CLEANUP_RENAME_TEMPLATE,
        help="Rename template used for the embedded rename plan.",
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
    parser.add_argument(
        "--include-associated-files",
        action="store_true",
        help="Group safe known associated files such as sidecars during embedded organize and rename planning.",
    )
    parser.add_argument(
        "--leftover-mode",
        choices=["off", "consolidate"],
        default="off",
        help="Optional cleanup of source leftovers after apply-organize. Default: off.",
    )
    parser.add_argument(
        "--leftover-dir-name",
        default="_remaining_files",
        help="Directory name used for consolidated leftovers under each source root.",
    )
    parser.add_argument("--show-files", action="store_true", help="Print detailed workflow section entries.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    parser.add_argument("--run-log", type=Path, help="Optional JSON run-log path for this cleanup workflow command.")
    parser.add_argument(
        "--journal",
        type=Path,
        help="Optional execution journal path for an applied cleanup step.",
    )
    apply_group = parser.add_mutually_exclusive_group()
    apply_group.add_argument("--apply-organize", action="store_true", help="Execute the embedded organize plan.")
    apply_group.add_argument("--apply-rename", action="store_true", help="Execute the embedded rename plan.")
    parser.add_argument(
        "--exiftool-path",
        type=Path,
        default=None,
        help="Optional explicit path to the exiftool executable.",
    )
    return parser


def _warning_payloads(obj) -> list[dict[str, object]]:
    warnings = getattr(obj, "association_warnings", ()) or ()
    payloads: list[dict[str, object]] = []
    for item in warnings:
        payloads.append(
            {
                "path": str(item.path),
                "warning_code": item.warning_code,
                "message": item.message,
            }
        )
    return payloads


def _member_target_payloads(obj) -> list[dict[str, object]]:
    members = getattr(obj, "member_targets", ()) or ()
    payloads: list[dict[str, object]] = []
    for item in members:
        payloads.append(
            {
                "source_path": str(item.source_path),
                "target_path": str(item.target_path),
                "role": getattr(item, "role", None),
                "is_main_file": bool(getattr(item, "is_main_file", getattr(item, "role", None) == "main")),
            }
        )
    return payloads


def _member_result_payloads(entry) -> list[dict[str, object]]:
    results = getattr(entry, "member_results", ()) or ()
    payloads: list[dict[str, object]] = []
    for item in results:
        status = getattr(item, "status", getattr(item, "outcome", None))
        action = getattr(item, "action", getattr(item, "outcome", None))
        payloads.append(
            {
                "source_path": str(item.source_path),
                "target_path": None if item.target_path is None else str(item.target_path),
                "status": status,
                "reason": item.reason,
                "action": action,
                "role": getattr(item, "role", None),
                "is_main_file": bool(getattr(item, "is_main_file", getattr(item, "role", None) == "main")),
            }
        )
    return payloads


def _leftover_payload(result) -> dict[str, object]:
    return {
        "requested": bool(getattr(result, "requested", False)),
        "mode": getattr(result, "mode", "off"),
        "directory_name": getattr(result, "directory_name", "_remaining_files"),
        "file_count": int(getattr(result, "file_count", 0)),
        "removed_empty_directory_count": int(getattr(result, "removed_empty_directory_count", 0)),
        "conflict_count": int(getattr(result, "conflict_count", 0)),
        "error_count": int(getattr(result, "error_count", 0)),
        "entries": [
            {
                "source_root": str(item.source_root),
                "source_path": str(item.source_path),
                "target_path": str(item.target_path),
                "conflict_resolved": bool(getattr(item, "conflict_resolved", False)),
            }
            for item in (getattr(result, "entries", ()) or ())
        ],
        "removed_empty_directories": [str(path) for path in (getattr(result, "removed_empty_directories", ()) or ())],
    }


def _build_payload(report, execution_report: CleanupExecutionReport | None) -> dict[str, object]:
    payload = {
        "sources": [str(path) for path in report.options.source_dirs],
        "target_root": str(report.options.target_root),
        "organize_pattern": report.options.organize_pattern,
        "rename_template": report.options.rename_template,
        "duplicate_policy": report.options.duplicate_policy,
        "duplicate_mode": report.options.duplicate_mode,
        "include_associated_files": bool(getattr(report.options, "include_associated_files", False)),
        "leftover_mode": getattr(report.options, "leftover_mode", "off"),
        "leftover_dir_name": getattr(report.options, "leftover_dir_name", "_remaining_files"),
        "media_group_count": int(getattr(report, "media_group_count", len(report.organize_plan.entries))),
        "associated_file_count": int(getattr(report, "associated_file_count", 0)),
        "association_warning_count": int(getattr(report, "association_warning_count", 0)),
        "group_kind_summary": dict(
            sorted(getattr(report, "group_kind_summary", {"single": len(report.organize_plan.entries)}).items())
        ),
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
            "media_group_count": int(getattr(report.organize_plan, "media_group_count", len(report.organize_plan.entries))),
            "associated_file_count": int(getattr(report.organize_plan, "associated_file_count", 0)),
            "association_warning_count": int(getattr(report.organize_plan, "association_warning_count", 0)),
            "group_kind_summary": dict(
                sorted(getattr(report.organize_plan, "group_kind_summary", {"single": len(report.organize_plan.entries)}).items())
            ),
        },
        "rename": {
            "planned_count": report.rename_dry_run.planned_count,
            "skipped_count": report.rename_dry_run.skipped_count,
            "conflict_count": report.rename_dry_run.conflict_count,
            "error_count": report.rename_dry_run.error_count,
            "media_group_count": int(getattr(report.rename_dry_run, "media_group_count", len(report.rename_dry_run.entries))),
            "associated_file_count": int(getattr(report.rename_dry_run, "associated_file_count", 0)),
            "association_warning_count": int(getattr(report.rename_dry_run, "association_warning_count", 0)),
            "group_kind_summary": dict(
                sorted(getattr(report.rename_dry_run, "group_kind_summary", {"single": len(report.rename_dry_run.entries)}).items())
            ),
        },
    }
    if execution_report is not None:
        if execution_report.apply_step == "organize" and execution_report.organize_result is not None:
            execution_payload = {
                "apply_step": "organize",
                "journal_path": None if execution_report.journal_path is None else str(execution_report.journal_path),
                "executed_count": execution_report.organize_result.executed_count,
                "copied_count": execution_report.organize_result.copied_count,
                "moved_count": execution_report.organize_result.moved_count,
                "skipped_count": execution_report.organize_result.skipped_count,
                "conflict_count": execution_report.organize_result.conflict_count,
                "error_count": execution_report.organize_result.error_count,
                "entries": [
                    {
                        "source_path": str(item.source_path),
                        "target_path": None if item.target_path is None else str(item.target_path),
                        "outcome": item.outcome,
                        "reason": item.reason,
                        "group_id": getattr(item, "group_id", getattr(getattr(item, "plan_entry", None), "group_id", None)),
                        "group_kind": getattr(item, "group_kind", getattr(getattr(item, "plan_entry", None), "group_kind", None)),
                        "main_file": str(getattr(getattr(item, "plan_entry", None), "source_path", item.source_path)),
                        "associated_files": [str(path) for path in getattr(getattr(item, "plan_entry", None), "associated_paths", ())],
                        "associated_file_count": int(getattr(getattr(item, "plan_entry", None), "associated_file_count", 0)),
                        "association_warnings": _warning_payloads(getattr(item, "plan_entry", None)),
                        "member_results": _member_result_payloads(item),
                    }
                    for item in execution_report.organize_result.entries
                ],
            }
            if execution_report.leftover_result is not None:
                execution_payload["leftover"] = _leftover_payload(execution_report.leftover_result)
            payload["execution"] = execution_payload
        elif execution_report.apply_step == "rename" and execution_report.rename_result is not None:
            payload["execution"] = {
                "apply_step": "rename",
                "journal_path": None if execution_report.journal_path is None else str(execution_report.journal_path),
                "renamed_count": execution_report.rename_result.renamed_count,
                "skipped_count": execution_report.rename_result.skipped_count,
                "conflict_count": execution_report.rename_result.conflict_count,
                "error_count": execution_report.rename_result.error_count,
                "entries": [
                    {
                        "source_path": str(item.source_path),
                        "target_path": None if item.target_path is None else str(item.target_path),
                        "status": item.status,
                        "reason": item.reason,
                        "action": item.action,
                        "group_id": getattr(item, "group_id", getattr(getattr(item, "plan_entry", None), "group_id", None)),
                        "group_kind": getattr(item, "group_kind", getattr(getattr(item, "plan_entry", None), "group_kind", None)),
                        "main_file": str(getattr(getattr(item, "plan_entry", None), "source_path", item.source_path)),
                        "associated_files": [str(path) for path in getattr(getattr(item, "plan_entry", None), "associated_paths", ())],
                        "associated_file_count": int(getattr(getattr(item, "plan_entry", None), "associated_file_count", 0)),
                        "association_warnings": _warning_payloads(getattr(item, "plan_entry", None)),
                        "member_results": _member_result_payloads(item),
                    }
                    for item in execution_report.rename_result.entries
                ],
            }
    return payload


def _print_detailed_sections(report, execution_report: CleanupExecutionReport | None) -> None:
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

    if execution_report is not None:
        print("\nExecution entries:")
        if execution_report.apply_step == "organize" and execution_report.organize_result is not None:
            for entry in execution_report.organize_result.entries:
                target_text = str(entry.target_path) if entry.target_path else "-"
                print(f"  - [{entry.outcome}] {entry.source_path} -> {target_text} | {entry.reason}")
            if execution_report.leftover_result is not None:
                print("\nLeftover consolidation entries:")
                for item in execution_report.leftover_result.entries:
                    print(f"  - [moved] {item.source_path} -> {item.target_path}")
        elif execution_report.apply_step == "rename" and execution_report.rename_result is not None:
            for entry in execution_report.rename_result.entries:
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

    if args.journal is not None and not (args.apply_organize or args.apply_rename):
        parser.error("--journal requires either --apply-organize or --apply-rename.")
    if args.leftover_mode != "off" and not args.apply_organize:
        parser.error("--leftover-mode currently requires --apply-organize.")

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
            include_associated_files=args.include_associated_files,
            leftover_mode=args.leftover_mode,
            leftover_dir_name=args.leftover_dir_name,
        )
    )

    execution_report = None
    apply_requested = False
    if args.apply_organize:
        execution_report = execute_cleanup_workflow(report, apply_step="organize", journal_path=args.journal)
        apply_requested = True
    elif args.apply_rename:
        execution_report = execute_cleanup_workflow(report, apply_step="rename", journal_path=args.journal)
        apply_requested = True

    payload = _build_payload(report, execution_report)
    exit_code = 0 if not report.has_errors else 1
    if execution_report is not None and execution_report.error_count > 0:
        exit_code = 1

    if args.run_log is not None:
        write_command_run_log(
            args.run_log,
            command_name="cleanup",
            apply_requested=apply_requested,
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
    print(f"  Media groups: {getattr(report, 'media_group_count', len(report.organize_plan.entries))}")
    print(f"  Associated files: {getattr(report, 'associated_file_count', 0)}")
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

    if execution_report is not None:
        print("\nExecution")
        print(f"  Apply step: {execution_report.apply_step}")
        if execution_report.apply_step == "organize" and execution_report.organize_result is not None:
            print(f"  Executed: {execution_report.organize_result.executed_count}")
            print(f"  Copied: {execution_report.organize_result.copied_count}")
            print(f"  Moved: {execution_report.organize_result.moved_count}")
            print(f"  Skipped: {execution_report.organize_result.skipped_count}")
            print(f"  Conflicts: {execution_report.organize_result.conflict_count}")
            print(f"  Errors: {execution_report.organize_result.error_count}")
            if execution_report.leftover_result is not None:
                print(f"  Leftover files moved: {execution_report.leftover_result.file_count}")
                print(f"  Empty directories removed: {execution_report.leftover_result.removed_empty_directory_count}")
                print(f"  Leftover conflicts resolved: {execution_report.leftover_result.conflict_count}")
        elif execution_report.apply_step == "rename" and execution_report.rename_result is not None:
            print(f"  Renamed: {execution_report.rename_result.renamed_count}")
            print(f"  Skipped: {execution_report.rename_result.skipped_count}")
            print(f"  Conflicts: {execution_report.rename_result.conflict_count}")
            print(f"  Errors: {execution_report.rename_result.error_count}")
        if execution_report.journal_path is not None:
            print(f"  Journal: {execution_report.journal_path}")

    if args.show_files:
        _print_detailed_sections(report, execution_report)

    if args.run_log is not None:
        print(f"\nWrote run log: {args.run_log}")

    return exit_code
