from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core.organizer import (
    DEFAULT_ORGANIZE_PATTERN,
    OrganizePlannerOptions,
    build_organize_dry_run,
    execute_organize_plan,
)
from .core.state import write_command_run_log, write_execution_journal


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager organize",
        description="Build or execute an organize plan from one or more source folders.",
    )
    parser.add_argument(
        "--source",
        dest="sources",
        action="append",
        type=Path,
        required=True,
        help="Source directory. Repeat the flag to add multiple source folders.",
    )
    parser.add_argument("--target", type=Path, required=True, help="Target directory root.")
    parser.add_argument(
        "--pattern",
        default=DEFAULT_ORGANIZE_PATTERN,
        help=(
            "Relative target directory pattern. "
            "Supported tokens: {year}, {month}, {day}, {year_month}, {year_month_day}, {source_name}."
        ),
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--copy", action="store_true", help="Plan copy-oriented organization (default).")
    mode_group.add_argument("--move", action="store_true", help="Plan move-oriented organization.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Execute the planned organize entries.",
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
        help="Print one line per plan or execution entry.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    parser.add_argument(
        "--run-log",
        type=Path,
        help="Optional path for a structured JSON run log.",
    )
    parser.add_argument(
        "--journal",
        type=Path,
        help="Optional path for a structured execution journal. Only meaningful with --apply.",
    )
    parser.add_argument(
        "--exiftool-path",
        type=Path,
        default=None,
        help="Optional explicit path to the exiftool executable.",
    )
    return parser


def _build_payload(plan, execution_result) -> dict[str, object]:
    payload = {
        "sources": [str(path) for path in plan.options.source_dirs],
        "target_root": str(plan.options.target_root),
        "pattern": plan.options.pattern,
        "operation_mode": plan.options.operation_mode,
        "missing_sources": [str(path) for path in plan.scan_summary.missing_sources],
        "media_file_count": plan.media_file_count,
        "planned_count": plan.planned_count,
        "skipped_count": plan.skipped_count,
        "conflict_count": plan.conflict_count,
        "error_count": plan.error_count,
        "status_summary": plan.status_summary,
        "reason_summary": plan.reason_summary,
        "resolution_source_summary": plan.resolution_source_summary,
        "confidence_summary": plan.confidence_summary,
        "entries": [
            {
                "source_root": str(item.source_root),
                "source_path": str(item.source_path),
                "relative_source_path": item.scanned_file.relative_path.as_posix(),
                "status": item.status,
                "reason": item.reason,
                "operation_mode": item.operation_mode,
                "target_relative_dir": item.target_relative_dir.as_posix() if item.target_relative_dir else None,
                "target_path": str(item.target_path) if item.target_path else None,
                "resolved_value": item.resolution.resolved_value if item.resolution else None,
                "source_kind": item.resolution.source_kind if item.resolution else None,
                "source_label": item.resolution.source_label if item.resolution else None,
                "confidence": item.resolution.confidence if item.resolution else None,
            }
            for item in plan.entries
        ],
    }
    if execution_result is not None:
        payload["execution"] = {
            "processed_count": execution_result.processed_count,
            "executed_count": execution_result.executed_count,
            "copied_count": execution_result.copied_count,
            "moved_count": execution_result.moved_count,
            "skipped_count": execution_result.skipped_count,
            "conflict_count": execution_result.conflict_count,
            "error_count": execution_result.error_count,
            "outcome_summary": execution_result.outcome_summary,
            "reason_summary": execution_result.reason_summary,
            "entries": [
                {
                    "source_path": str(item.source_path),
                    "target_path": str(item.target_path) if item.target_path else None,
                    "outcome": item.outcome,
                    "reason": item.reason,
                }
                for item in execution_result.entries
            ],
        }
    return payload


def _build_journal_entries(execution_result) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for item in execution_result.entries:
        reversible = False
        undo_action = None
        undo_from_path = None
        undo_to_path = None

        if item.outcome == "copied":
            reversible = True
            undo_action = "delete_target"
            undo_from_path = str(item.target_path) if item.target_path is not None else None
        elif item.outcome == "moved":
            reversible = True
            undo_action = "move_back"
            undo_from_path = str(item.target_path) if item.target_path is not None else None
            undo_to_path = str(item.source_path)

        entries.append(
            {
                "source_path": str(item.source_path),
                "target_path": None if item.target_path is None else str(item.target_path),
                "outcome": item.outcome,
                "reason": item.reason,
                "reversible": reversible,
                "undo_action": undo_action,
                "undo_from_path": undo_from_path,
                "undo_to_path": undo_to_path,
            }
        )
    return entries


def _print_counter_block(label: str, counter: dict[str, int]) -> None:
    if not counter:
        print(f"{label}: none")
        return
    rendered = " | ".join(f"{key}={value}" for key, value in sorted(counter.items()))
    print(f"{label}: {rendered}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    operation_mode = "move" if args.move else "copy"
    plan = build_organize_dry_run(
        OrganizePlannerOptions(
            source_dirs=tuple(args.sources),
            target_root=args.target,
            pattern=args.pattern,
            recursive=not args.non_recursive,
            include_hidden=args.include_hidden,
            operation_mode=operation_mode,
            exiftool_path=args.exiftool_path,
        )
    )
    execution_result = execute_organize_plan(plan) if args.apply else None

    payload = _build_payload(plan, execution_result)
    has_errors = plan.error_count > 0 or plan.missing_source_count > 0
    if execution_result is not None:
        has_errors = has_errors or execution_result.error_count > 0
    exit_code = 0 if not has_errors else 1

    if args.run_log is not None:
        write_command_run_log(
            args.run_log,
            command_name="organize",
            apply_requested=args.apply,
            exit_code=exit_code,
            payload=payload,
        )

    if args.apply and args.journal is not None and execution_result is not None:
        write_execution_journal(
            args.journal,
            command_name="organize",
            apply_requested=True,
            exit_code=exit_code,
            entries=_build_journal_entries(execution_result),
        )

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return exit_code

    print("Organize plan")
    print(f"  Sources: {len(plan.options.source_dirs)}")
    print(f"  Missing sources: {plan.missing_source_count}")
    print(f"  Media files scanned: {plan.media_file_count}")
    print(f"  Planned: {plan.planned_count}")
    print(f"  Skipped: {plan.skipped_count}")
    print(f"  Conflicts: {plan.conflict_count}")
    print(f"  Errors: {plan.error_count}")
    _print_counter_block("  Status summary", plan.status_summary)
    _print_counter_block("  Reason summary", plan.reason_summary)
    _print_counter_block("  Resolution sources", plan.resolution_source_summary)
    _print_counter_block("  Confidence summary", plan.confidence_summary)

    if execution_result is not None:
        print("\nExecution")
        print(f"  Executed: {execution_result.executed_count}")
        print(f"  Copied: {execution_result.copied_count}")
        print(f"  Moved: {execution_result.moved_count}")
        print(f"  Skipped: {execution_result.skipped_count}")
        print(f"  Conflicts: {execution_result.conflict_count}")
        print(f"  Errors: {execution_result.error_count}")
        _print_counter_block("  Outcome summary", execution_result.outcome_summary)
        _print_counter_block("  Execution reasons", execution_result.reason_summary)

    if plan.scan_summary.missing_sources:
        print("\nMissing sources:")
        for path in plan.scan_summary.missing_sources:
            print(f"  - {path}")

    if args.show_files:
        print("\nEntries:")
        for item in plan.entries:
            target_text = str(item.target_path) if item.target_path else "-"
            resolved_text = item.resolution.resolved_value if item.resolution else "-"
            print(
                f"  - [{item.status}] {item.source_path} -> {target_text} | "
                f"date={resolved_text} | reason={item.reason}"
            )
        if execution_result is not None:
            print("\nExecution entries:")
            for item in execution_result.entries:
                target_text = str(item.target_path) if item.target_path else "-"
                print(f"  - [{item.outcome}] {item.source_path} -> {target_text} | reason={item.reason}")

    if args.run_log is not None:
        print(f"\nWrote run log: {args.run_log}")
    if args.apply and args.journal is not None and execution_result is not None:
        print(f"Wrote execution journal: {args.journal}")

    return exit_code
