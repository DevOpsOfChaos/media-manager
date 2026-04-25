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
from .core.outcome_report import build_execution_outcome_report, build_plan_outcome_report
from .core.review_report import build_review_export
from .core.report_export import build_review_file_payload, write_json_report
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
        "--include-associated-files",
        action="store_true",
        help="Group known sidecars and explicit sibling media pairs with the main media file.",
    )
    parser.add_argument(
        "--conflict-policy",
        choices=["conflict", "skip"],
        default="conflict",
        help="How to handle existing target paths. Default: conflict.",
    )
    parser.add_argument(
        "--include-pattern",
        dest="include_patterns",
        action="append",
        default=[],
        help="Only include files whose name, relative path, or path matches this pattern. Repeat to add patterns.",
    )
    parser.add_argument(
        "--exclude-pattern",
        dest="exclude_patterns",
        action="append",
        default=[],
        help="Exclude files whose name, relative path, or path matches this pattern. Repeat to add patterns.",
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
        "--report-json",
        type=Path,
        help="Optional path where the full JSON report is written without requiring --json stdout.",
    )
    parser.add_argument(
        "--review-json",
        type=Path,
        help="Optional path where a compact review-focused JSON report is written.",
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


def _warning_payloads(entry) -> list[dict[str, object]]:
    media_group = getattr(entry, "media_group", None)
    if media_group is None:
        return []
    return [
        {
            "path": str(item.path),
            "warning_code": item.warning_code,
            "message": item.message,
        }
        for item in getattr(media_group, "association_warnings", ())
    ]


def _member_target_payloads(entry) -> list[dict[str, object]]:
    media_group = getattr(entry, "media_group", None)
    if media_group is not None:
        role_by_path = {member.path: member.role for member in media_group.members}
        ordered_paths = [member.path for member in media_group.members]
    else:
        role_by_path = {entry.source_path: "main"}
        ordered_paths = [entry.source_path]

    group_target_paths = getattr(entry, "group_target_paths", {entry.source_path: entry.target_path})

    rows = []
    for source_path in ordered_paths:
        rows.append(
            {
                "source_path": str(source_path),
                "target_path": None if group_target_paths.get(source_path) is None else str(group_target_paths[source_path]),
                "role": role_by_path.get(source_path, "associated"),
                "is_main_file": source_path == entry.source_path,
            }
        )
    return rows


def _build_payload(plan, execution_result) -> dict[str, object]:
    include_associated_files = bool(getattr(plan.options, "include_associated_files", False))
    media_group_count = int(getattr(plan, "media_group_count", len(getattr(plan, "entries", []))))
    associated_file_count = int(getattr(plan, "associated_file_count", 0))
    association_warning_count = int(getattr(plan, "association_warning_count", 0))
    group_kind_summary = dict(sorted(getattr(plan, "group_kind_summary", {"single": media_group_count}).items()))

    plan_summaries = _plan_summaries(plan)
    review_export = build_review_export({"organize": plan.entries})
    payload = {
        "sources": [str(path) for path in plan.options.source_dirs],
        "target_root": str(plan.options.target_root),
        "pattern": plan.options.pattern,
        "operation_mode": plan.options.operation_mode,
        "conflict_policy": getattr(plan.options, "conflict_policy", "conflict"),
        "include_patterns": list(getattr(plan.options, "include_patterns", ())),
        "exclude_patterns": list(getattr(plan.options, "exclude_patterns", ())),
        "include_associated_files": include_associated_files,
        "missing_sources": [str(path) for path in plan.scan_summary.missing_sources],
        "media_file_count": plan.media_file_count,
        "skipped_filtered_files": int(getattr(plan.scan_summary, "skipped_filtered_files", 0)),
        "media_group_count": media_group_count,
        "associated_file_count": associated_file_count,
        "association_warning_count": association_warning_count,
        "group_kind_summary": group_kind_summary,
        "planned_count": plan.planned_count,
        "skipped_count": plan.skipped_count,
        "conflict_count": plan.conflict_count,
        "error_count": plan.error_count,
        **plan_summaries,
        "review": review_export,
        "outcome_report": build_plan_outcome_report(
            command_name="organize",
            conflict_policy=getattr(plan.options, "conflict_policy", "conflict"),
            planned_count=plan.planned_count,
            skipped_count=plan.skipped_count,
            conflict_count=plan.conflict_count,
            error_count=plan.error_count,
            missing_source_count=getattr(plan, "missing_source_count", len(getattr(plan.scan_summary, "missing_sources", ()))),
            status_summary=plan_summaries["status_summary"],
            reason_summary=plan_summaries["reason_summary"],
        ),
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
                "group_id": getattr(item, "group_id", None),
                "group_kind": getattr(item, "group_kind", "single"),
                "main_file": str(item.source_path),
                "associated_files": [str(path) for path in getattr(item, "associated_paths", ())],
                "associated_file_count": int(getattr(item, "associated_file_count", 0)),
                "association_warnings": _warning_payloads(item),
                "member_targets": _member_target_payloads(item),
            }
            for item in plan.entries
        ],
    }
    if execution_result is not None:
        execution_summaries = _execution_summaries(execution_result)
        payload["execution"] = {
            "processed_count": execution_result.processed_count,
            "executed_count": execution_result.executed_count,
            "copied_count": execution_result.copied_count,
            "moved_count": execution_result.moved_count,
            "skipped_count": execution_result.skipped_count,
            "conflict_count": execution_result.conflict_count,
            "error_count": execution_result.error_count,
            **execution_summaries,
            "outcome_report": build_execution_outcome_report(
                command_name="organize",
                apply_requested=True,
                processed_count=execution_result.processed_count,
                executed_count=execution_result.executed_count,
                skipped_count=execution_result.skipped_count,
                conflict_count=execution_result.conflict_count,
                error_count=execution_result.error_count,
                status_summary=execution_result.outcome_summary,
                reason_summary=execution_summaries["reason_summary"],
            ),
            "entries": [
                {
                    "source_path": str(item.source_path),
                    "target_path": str(item.target_path) if item.target_path else None,
                    "outcome": item.outcome,
                    "reason": item.reason,
                    "group_id": getattr(item, "group_id", None),
                    "group_kind": getattr(item, "group_kind", getattr(item.plan_entry, "group_kind", "single")),
                    "main_file": str(item.plan_entry.source_path),
                    "associated_files": [str(path) for path in getattr(item.plan_entry, "associated_paths", ())],
                    "associated_file_count": int(getattr(item.plan_entry, "associated_file_count", 0)),
                    "association_warnings": _warning_payloads(item.plan_entry),
                    "member_results": [
                        {
                            "source_path": str(member.source_path),
                            "target_path": None if member.target_path is None else str(member.target_path),
                            "role": member.role,
                            "is_main_file": member.is_main_file,
                            "outcome": member.outcome,
                            "reason": member.reason,
                        }
                        for member in getattr(item, "member_results", ())
                    ],
                }
                for item in execution_result.entries
            ],
        }
    return payload


def _build_journal_entries(execution_result) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for item in execution_result.entries:
        associated_files = [str(path) for path in getattr(item.plan_entry, "associated_paths", ())]
        warnings = _warning_payloads(item.plan_entry)
        for member in getattr(item, "member_results", ()): 
            reversible = False
            undo_action = None
            undo_from_path = None
            undo_to_path = None

            if member.outcome == "copied":
                reversible = True
                undo_action = "delete_target"
                undo_from_path = str(member.target_path) if member.target_path is not None else None
            elif member.outcome == "moved":
                reversible = True
                undo_action = "move_back"
                undo_from_path = str(member.target_path) if member.target_path is not None else None
                undo_to_path = str(member.source_path)

            entries.append(
                {
                    "source_path": str(member.source_path),
                    "target_path": None if member.target_path is None else str(member.target_path),
                    "outcome": member.outcome,
                    "reason": member.reason,
                    "reversible": reversible,
                    "undo_action": undo_action,
                    "undo_from_path": undo_from_path,
                    "undo_to_path": undo_to_path,
                    "group_id": item.group_id,
                    "group_kind": item.group_kind,
                    "main_file": str(item.plan_entry.source_path),
                    "associated_files": associated_files,
                    "associated_file_count": item.plan_entry.associated_file_count,
                    "association_warnings": warnings,
                    "role": member.role,
                    "is_main_file": member.is_main_file,
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
            include_associated_files=args.include_associated_files,
            conflict_policy=args.conflict_policy,
            include_patterns=tuple(args.include_patterns),
            exclude_patterns=tuple(args.exclude_patterns),
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

    if args.report_json is not None:
        write_json_report(args.report_json, payload)
    if args.review_json is not None:
        write_json_report(args.review_json, build_review_file_payload("organize", payload))

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
    if plan.options.include_associated_files:
        print(f"  Media groups: {plan.media_group_count}")
        print(f"  Associated files: {plan.associated_file_count}")
        print(f"  Association warnings: {plan.association_warning_count}")
    print(f"  Planned: {plan.planned_count}")
    print(f"  Skipped: {plan.skipped_count}")
    print(f"  Conflicts: {plan.conflict_count}")
    print(f"  Errors: {plan.error_count}")
    outcome_report = payload["outcome_report"]
    print("\nOutcome report")
    print(f"  Status: {outcome_report['status']}")
    print(f"  Next action: {outcome_report['next_action']}")
    if payload.get("review", {}).get("candidate_count", 0):
        print("\nReview")
        print(f"  Candidates: {payload['review']['candidate_count']}")
        print(f"  Reasons: {payload['review']['reason_summary']}")
    _print_summary_block("\nStatus summary", payload["status_summary"])
    _print_summary_block("\nReason summary", payload["reason_summary"])
    _print_summary_block("\nResolution sources", payload["resolution_source_summary"])
    _print_summary_block("\nConfidence summary", payload["confidence_summary"])
    if plan.options.include_associated_files:
        _print_summary_block("\nGroup kinds", payload["group_kind_summary"])

    if execution_result is not None:
        print("\nExecution")
        print(f"  Executed: {execution_result.executed_count}")
        print(f"  Copied: {execution_result.copied_count}")
        print(f"  Moved: {execution_result.moved_count}")
        print(f"  Skipped: {execution_result.skipped_count}")
        print(f"  Conflicts: {execution_result.conflict_count}")
        print(f"  Errors: {execution_result.error_count}")
        execution = payload["execution"]
        execution_outcome = execution["outcome_report"]
        print(f"  Outcome status: {execution_outcome['status']}")
        print(f"  Next action: {execution_outcome['next_action']}")
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
            extra = f" | group={item.group_kind} | associated={item.associated_file_count}" if item.group_kind else ""
            print(
                f"  - [{item.status}] {item.source_path} -> {target_text} | "
                f"date={resolved_text} | reason={item.reason}{extra}"
            )
        if execution_result is not None:
            print("\nExecution entries:")
            for item in execution_result.entries:
                target_text = str(item.target_path) if item.target_path else "-"
                extra = f" | group={item.group_kind}" if item.group_kind else ""
                print(f"  - [{item.outcome}] {item.source_path} -> {target_text} | reason={item.reason}{extra}")

    if args.run_log is not None:
        print(f"\nWrote run log: {args.run_log}")
    if args.report_json is not None:
        print(f"Wrote JSON report: {args.report_json}")
    if args.review_json is not None:
        print(f"Wrote review JSON: {args.review_json}")
    if args.apply and args.journal is not None and execution_result is not None:
        print(f"Wrote execution journal: {args.journal}")
    if history_artifacts is not None:
        print(f"Wrote history run log: {history_artifacts['run_log_path']}")
        if "execution_journal_path" in history_artifacts:
            print(f"Wrote history journal: {history_artifacts['execution_journal_path']}")

    return exit_code
