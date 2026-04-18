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
from .core.state import write_command_run_log, write_execution_journal, write_history_artifacts


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
        "--history-dir",
        type=Path,
        help="Optional directory where an auto-named run log and, for apply mode, execution journal are written.",
    )
    parser.add_argument(
        "--exiftool-path",
        type=Path,
        default=None,
        help="Optional explicit path to the exiftool executable.",
    )
    return parser


def _count_by_label(values: list[str]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for value in values:
        summary[value] = summary.get(value, 0) + 1
    return dict(sorted(summary.items()))


def _plan_summaries(plan) -> dict[str, dict[str, int]]:
    statuses: list[str] = []
    reasons: list[str] = []
    source_kinds: list[str] = []
    confidences: list[str] = []
    for item in plan.entries:
        statuses.append(str(item.status))
        reasons.append(str(item.reason))
        if item.resolution is not None:
            source_kinds.append(str(item.resolution.source_kind))
            confidences.append(str(item.resolution.confidence))
    return {
        "status_summary": _count_by_label(statuses),
        "reason_summary": _count_by_label(reasons),
        "resolution_source_summary": _count_by_label(source_kinds),
        "confidence_summary": _count_by_label(confidences),
    }


def _execution_summaries(execution_result) -> dict[str, dict[str, int]]:
    outcomes = [str(item.outcome) for item in execution_result.entries]
    reasons = [str(item.reason) for item in execution_result.entries]
    return {
        "outcome_summary": _count_by_label(outcomes),
        "reason_summary": _count_by_label(reasons),
    }


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
        **_plan_summaries(plan),
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
            **_execution_summaries(execution_result),
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


def _print_summary_block(title: str, summary: dict[str, int]) -> None:
    if not summary:
        return
    print(title)
    for key, value in summary.items():
        print(f"  {key}: {value}")


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

    explicit_journal_entries = _build_journal_entries(execution_result) if execution_result is not None else None
    history_artifacts = None

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
            entries=explicit_journal_entries or [],
        )

    if args.history_dir is not None:
        history_artifacts = write_history_artifacts(
            args.history_dir,
            command_name="organize",
            apply_requested=args.apply,
            exit_code=exit_code,
            payload=payload,
            journal_entries=explicit_journal_entries if args.apply else None,
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
    _print_summary_block("\nStatus summary", payload["status_summary"])
    _print_summary_block("\nReason summary", payload["reason_summary"])
    _print_summary_block("\nResolution sources", payload["resolution_source_summary"])
    _print_summary_block("\nConfidence summary", payload["confidence_summary"])

    if execution_result is not None:
        print("\nExecution")
        print(f"  Executed: {execution_result.executed_count}")
        print(f"  Copied: {execution_result.copied_count}")
        print(f"  Moved: {execution_result.moved_count}")
        print(f"  Skipped: {execution_result.skipped_count}")
        print(f"  Conflicts: {execution_result.conflict_count}")
        print(f"  Errors: {execution_result.error_count}")
        execution = payload["execution"]
        _print_summary_block("\nExecution outcomes", execution["outcome_summary"])
        _print_summary_block("\nExecution reasons", execution["reason_summary"])

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
    if history_artifacts is not None:
        print(f"Wrote history run log: {history_artifacts['run_log_path']}")
        if "execution_journal_path" in history_artifacts:
            print(f"Wrote history journal: {history_artifacts['execution_journal_path']}")

    return exit_code
