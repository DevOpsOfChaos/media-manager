from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core.state import write_command_run_log, write_execution_journal, write_history_artifacts
from .core.workflows import TripWorkflowOptions, build_trip_dry_run, execute_trip_plan, parse_trip_date


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager trip",
        description="Build or execute a trip collection workflow from a capture-date range.",
    )
    parser.add_argument(
        "--source",
        dest="sources",
        action="append",
        type=Path,
        required=True,
        help="Source directory. Repeat the flag to add multiple source folders.",
    )
    parser.add_argument("--target", type=Path, required=True, help="Trip collection target root.")
    parser.add_argument("--label", required=True, help="Trip label, for example Italy_2025.")
    parser.add_argument("--start", required=True, help="Inclusive trip start date in YYYY-MM-DD format.")
    parser.add_argument("--end", required=True, help="Inclusive trip end date in YYYY-MM-DD format.")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--link", action="store_true", help="Create hard links for matched trip files (default).")
    mode_group.add_argument("--copy", action="store_true", help="Copy matched trip files into the collection.")
    parser.add_argument("--apply", action="store_true", help="Execute the trip workflow plan.")
    parser.add_argument("--non-recursive", action="store_true", help="Only scan the top level of each source folder.")
    parser.add_argument("--include-hidden", action="store_true", help="Include hidden files and folders.")
    parser.add_argument("--show-files", action="store_true", help="Print one line per plan or execution entry.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    parser.add_argument("--run-log", type=Path, help="Optional JSON run-log output path.")
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


def _build_payload(dry_run, execution_result) -> dict[str, object]:
    payload = {
        "sources": [str(path) for path in dry_run.options.source_dirs],
        "target_root": str(dry_run.options.target_root),
        "label": dry_run.options.label,
        "start_date": dry_run.options.start_date.isoformat(),
        "end_date": dry_run.options.end_date.isoformat(),
        "mode": dry_run.options.mode,
        "missing_sources": [str(path) for path in dry_run.scan_summary.missing_sources],
        "media_file_count": dry_run.media_file_count,
        "selected_count": dry_run.selected_count,
        "planned_count": dry_run.planned_count,
        "skipped_count": dry_run.skipped_count,
        "conflict_count": dry_run.conflict_count,
        "error_count": dry_run.error_count,
        "status_summary": dry_run.status_summary,
        "reason_summary": dry_run.reason_summary,
        "resolution_source_summary": dry_run.resolution_source_summary,
        "confidence_summary": dry_run.confidence_summary,
        "entries": [
            {
                "source_root": str(item.source_root),
                "source_path": str(item.source_path),
                "relative_source_path": item.scanned_file.relative_path.as_posix(),
                "status": item.status,
                "reason": item.reason,
                "mode": item.mode,
                "target_path": None if item.target_path is None else str(item.target_path),
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
            "executed_count": execution_result.executed_count,
            "linked_count": execution_result.linked_count,
            "copied_count": execution_result.copied_count,
            "skipped_count": execution_result.skipped_count,
            "conflict_count": execution_result.conflict_count,
            "error_count": execution_result.error_count,
            "outcome_summary": execution_result.outcome_summary,
            "reason_summary": execution_result.reason_summary,
            "entries": [
                {
                    "source_path": str(item.source_path),
                    "target_path": None if item.target_path is None else str(item.target_path),
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

        if item.outcome in {"linked", "copied"}:
            reversible = True
            undo_action = "delete_target"
            undo_from_path = str(item.target_path) if item.target_path is not None else None

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

    invalid_sources = [path for path in args.sources if not path.is_dir()]
    if invalid_sources:
        parser.error(
            "The following source directories do not exist or are not directories: "
            + ", ".join(str(path) for path in invalid_sources)
        )

    start_date = parse_trip_date(args.start)
    end_date = parse_trip_date(args.end)
    mode = "copy" if args.copy else "link"

    dry_run = build_trip_dry_run(
        TripWorkflowOptions(
            source_dirs=tuple(args.sources),
            target_root=args.target,
            label=args.label,
            start_date=start_date,
            end_date=end_date,
            recursive=not args.non_recursive,
            include_hidden=args.include_hidden,
            mode=mode,
            exiftool_path=args.exiftool_path,
        )
    )
    execution_result = execute_trip_plan(dry_run, apply=args.apply) if args.apply else None

    has_errors = dry_run.error_count > 0 or dry_run.missing_source_count > 0
    if execution_result is not None:
        has_errors = has_errors or execution_result.error_count > 0
    exit_code = 0 if not has_errors else 1

    payload = _build_payload(dry_run, execution_result)

    history_artifacts = None
    journal_entries = _build_journal_entries(execution_result) if execution_result is not None else None

    if args.run_log is not None:
        write_command_run_log(
            args.run_log,
            command_name="trip",
            apply_requested=args.apply,
            exit_code=exit_code,
            payload=payload,
        )

    if args.apply and args.journal is not None and execution_result is not None:
        write_execution_journal(
            args.journal,
            command_name="trip",
            apply_requested=True,
            exit_code=exit_code,
            entries=journal_entries or [],
        )

    if args.history_dir is not None:
        history_artifacts = write_history_artifacts(
            args.history_dir,
            command_name="trip",
            apply_requested=args.apply,
            exit_code=exit_code,
            payload=payload,
            journal_entries=journal_entries if args.apply else None,
        )

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return exit_code

    title = "Trip apply summary" if args.apply else "Trip dry-run summary"
    print(title)
    print(f"  Sources: {len(dry_run.options.source_dirs)}")
    print(f"  Missing sources: {dry_run.missing_source_count}")
    print(f"  Media files: {dry_run.media_file_count}")
    print(f"  Selected: {dry_run.selected_count}")
    print(f"  Planned: {dry_run.planned_count}")
    print(f"  Skipped: {dry_run.skipped_count}")
    print(f"  Conflicts: {dry_run.conflict_count}")
    print(f"  Errors: {dry_run.error_count}")
    _print_summary_block("\nStatus summary", payload["status_summary"])
    _print_summary_block("\nReason summary", payload["reason_summary"])
    _print_summary_block("\nResolution sources", payload["resolution_source_summary"])
    _print_summary_block("\nConfidence summary", payload["confidence_summary"])

    if execution_result is not None:
        print("\nExecution")
        print(f"  Executed: {execution_result.executed_count}")
        print(f"  Linked: {execution_result.linked_count}")
        print(f"  Copied: {execution_result.copied_count}")
        print(f"  Skipped: {execution_result.skipped_count}")
        print(f"  Conflicts: {execution_result.conflict_count}")
        print(f"  Errors: {execution_result.error_count}")
        execution = payload["execution"]
        _print_summary_block("\nExecution outcomes", execution["outcome_summary"])
        _print_summary_block("\nExecution reasons", execution["reason_summary"])

    if args.show_files:
        print("\nEntries:")
        for item in dry_run.entries:
            target_text = str(item.target_path) if item.target_path is not None else "-"
            resolved_text = item.resolution.resolved_value if item.resolution is not None else "-"
            print(f"  - [{item.status}] {item.source_path} -> {target_text} | date={resolved_text} | reason={item.reason}")
        if execution_result is not None:
            print("\nExecution entries:")
            for item in execution_result.entries:
                target_text = str(item.target_path) if item.target_path is not None else "-"
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
