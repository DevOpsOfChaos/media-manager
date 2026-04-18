from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core.state import execute_undo_journal


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager undo",
        description="Preview or execute rollback actions from a structured execution journal.",
    )
    parser.add_argument("--journal", type=Path, required=True, help="Execution journal JSON file.")
    parser.add_argument("--apply", action="store_true", help="Execute the recorded undo actions.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    parser.add_argument("--show-files", action="store_true", help="Print one line per undo entry.")
    return parser


def _build_payload(result) -> dict[str, object]:
    return {
        "journal_path": str(result.journal_path),
        "journal_command_name": result.journal_command_name,
        "original_apply_requested": result.original_apply_requested,
        "original_exit_code": result.original_exit_code,
        "apply_requested": result.apply_requested,
        "entry_count": result.entry_count,
        "reversible_entry_count": result.reversible_entry_count,
        "planned_count": result.planned_count,
        "ready_to_apply_count": result.ready_to_apply_count,
        "undone_count": result.undone_count,
        "skipped_count": result.skipped_count,
        "error_count": result.error_count,
        "status_summary": result.status_summary,
        "undo_action_summary": result.undo_action_summary,
        "reason_summary": result.reason_summary,
        "entries": [
            {
                "undo_action": item.undo_action,
                "source_path": None if item.source_path is None else str(item.source_path),
                "target_path": None if item.target_path is None else str(item.target_path),
                "status": item.status,
                "reason": item.reason,
            }
            for item in result.entries
        ],
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

    result = execute_undo_journal(args.journal, apply=args.apply)
    payload = _build_payload(result)
    exit_code = 0 if result.error_count == 0 else 1

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return exit_code

    title = "Undo apply summary" if args.apply else "Undo preview summary"
    print(title)
    print(f"  Journal: {result.journal_path}")
    print(f"  Original command: {result.journal_command_name}")
    print(f"  Reversible entries: {result.reversible_entry_count}")
    print(f"  Planned: {result.planned_count}")
    print(f"  Ready to apply: {result.ready_to_apply_count}")
    print(f"  Undone: {result.undone_count}")
    print(f"  Skipped: {result.skipped_count}")
    print(f"  Errors: {result.error_count}")
    _print_summary_block("\nUndo status summary", result.status_summary)
    _print_summary_block("\nUndo action summary", result.undo_action_summary)
    _print_summary_block("\nUndo reason summary", result.reason_summary)

    if args.show_files and result.entries:
        print("\nUndo entries:")
        for item in result.entries:
            source_text = "-" if item.source_path is None else str(item.source_path)
            target_text = "-" if item.target_path is None else str(item.target_path)
            print(f"  - [{item.status}] {item.undo_action} | from={source_text} | to={target_text} | {item.reason}")

    return exit_code
