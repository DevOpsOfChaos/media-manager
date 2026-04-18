from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core.renamer import RenamePlannerOptions, build_rename_dry_run, execute_rename_dry_run
from .core.state import write_command_run_log, write_execution_journal, write_history_artifacts

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
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply planned rename operations instead of only printing the dry-run plan.",
    )
    return parser


def _count_by_label(values: list[str]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for value in values:
        summary[value] = summary.get(value, 0) + 1
    return dict(sorted(summary.items()))


def _dry_run_summaries(dry_run) -> dict[str, dict[str, int]]:
    statuses: list[str] = []
    reasons: list[str] = []
    source_kinds: list[str] = []
    confidences: list[str] = []
    for item in dry_run.entries:
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
    statuses = [str(entry.status) for entry in execution_result.entries]
    actions = [str(entry.action) for entry in execution_result.entries]
    reasons = [str(entry.reason) for entry in execution_result.entries]
    return {
        "status_summary": _count_by_label(statuses),
        "action_summary": _count_by_label(actions),
        "reason_summary": _count_by_label(reasons),
    }


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
        **_dry_run_summaries(dry_run),
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
            **_execution_summaries(execution_result),
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


def _build_journal_entries(execution_result) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for entry in execution_result.entries:
        reversible = False
        undo_action = None
        undo_from_path = None
        undo_to_path = None

        if entry.action == "renamed":
            reversible = True
            undo_action = "rename_back"
            undo_from_path = str(entry.target_path) if entry.target_path is not None else None
            undo_to_path = str(entry.source_path)

        entries.append(
            {
                "source_path": str(entry.source_path),
                "target_path": None if entry.target_path is None else str(entry.target_path),
                "outcome": entry.action,
                "reason": entry.reason,
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
    payload = _build_json_payload(dry_run, execution_result)
    exit_code = 0 if execution_result.error_count == 0 and dry_run.missing_source_count == 0 else 1

    explicit_journal_entries = _build_journal_entries(execution_result) if args.apply else None
    history_artifacts = None

    if args.run_log is not None:
        write_command_run_log(
            args.run_log,
            command_name="rename",
            apply_requested=args.apply,
            exit_code=exit_code,
            payload=payload,
        )

    if args.apply and args.journal is not None:
        write_execution_journal(
            args.journal,
            command_name="rename",
            apply_requested=True,
            exit_code=exit_code,
            entries=explicit_journal_entries or [],
        )

    if args.history_dir is not None:
        history_artifacts = write_history_artifacts(
            args.history_dir,
            command_name="rename",
            apply_requested=args.apply,
            exit_code=exit_code,
            payload=payload,
            journal_entries=explicit_journal_entries if args.apply else None,
        )

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return exit_code

    title = "Rename apply summary" if args.apply else "Rename dry-run summary"
    print(title)
    print(f"  Sources: {len(dry_run.options.source_dirs)}")
    print(f"  Missing sources: {dry_run.missing_source_count}")
    print(f"  Media files: {dry_run.media_file_count}")
    print(f"  Planned: {dry_run.planned_count}")
    print(f"  Skipped: {dry_run.skipped_count}")
    print(f"  Conflicts: {dry_run.conflict_count}")
    print(f"  Errors: {dry_run.error_count}")
    _print_summary_block("\nStatus summary", payload["status_summary"])
    _print_summary_block("\nReason summary", payload["reason_summary"])
    _print_summary_block("\nResolution sources", payload["resolution_source_summary"])
    _print_summary_block("\nConfidence summary", payload["confidence_summary"])

    if args.apply:
        print(f"  Renamed: {execution_result.renamed_count}")
        execution = payload["execution"]
        _print_summary_block("\nExecution statuses", execution["status_summary"])
        _print_summary_block("\nExecution actions", execution["action_summary"])
        _print_summary_block("\nExecution reasons", execution["reason_summary"])

    if args.show_files and execution_result.entries:
        print("\nRename entries:")
        for entry in execution_result.entries:
            target_display = "-" if entry.target_path is None else str(entry.target_path)
            print(
                f"  - [{entry.status}] {entry.source_path} -> {target_display} | {entry.reason}"
            )

    if args.run_log is not None:
        print(f"\nWrote run log: {args.run_log}")
    if args.apply and args.journal is not None:
        print(f"Wrote execution journal: {args.journal}")
    if history_artifacts is not None:
        print(f"Wrote history run log: {history_artifacts['run_log_path']}")
        if "execution_journal_path" in history_artifacts:
            print(f"Wrote history journal: {history_artifacts['execution_journal_path']}")

    return exit_code
