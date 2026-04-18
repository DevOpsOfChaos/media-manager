from __future__ import annotations

import argparse
import json
from pathlib import Path

from .duplicate_session_store import (
    DuplicateSessionRestoreResult,
    restore_duplicate_session,
    save_duplicate_session_snapshot,
)
from .duplicate_workflow import (
    build_duplicate_decisions,
    build_duplicate_workflow_bundle,
    execute_duplicate_workflow_bundle,
)
from .duplicates import DuplicateScanConfig, scan_exact_duplicates


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="media-manager duplicates")
    parser.add_argument(
        "--source",
        dest="sources",
        action="append",
        type=Path,
        required=True,
        help="Source directory. Repeat the flag to add multiple source folders.",
    )
    parser.add_argument(
        "--show-groups",
        action="store_true",
        help="Print all confirmed exact duplicate groups.",
    )
    parser.add_argument(
        "--show-session",
        action="store_true",
        help="Print duplicate session restore details when a session is loaded.",
    )
    parser.add_argument(
        "--policy",
        choices=["first", "newest", "oldest"],
        help="Auto-select one keep candidate per exact duplicate group.",
    )
    parser.add_argument(
        "--mode",
        choices=["copy", "move", "delete"],
        default="copy",
        help="Interpret duplicate decisions for copy, move, or delete planning. Default: copy.",
    )
    parser.add_argument(
        "--target",
        type=Path,
        help="Optional target root used for copy/move dry-run planning.",
    )
    parser.add_argument(
        "--load-session",
        type=Path,
        help="Load exact-duplicate keep decisions from a saved session snapshot.",
    )
    parser.add_argument(
        "--save-session",
        type=Path,
        help="Save the current exact-duplicate keep decisions as a session snapshot.",
    )
    parser.add_argument(
        "--show-plan",
        action="store_true",
        help="Print cleanup-plan, dry-run, and execution-preview counters.",
    )
    parser.add_argument(
        "--json-report",
        type=Path,
        help="Write a JSON report with scan, decision, dry-run, and execution-preview data.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Execute the currently executable delete rows. Only valid with --mode delete.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Required confirmation switch for --apply.",
    )
    return parser


def _print_duplicate_groups(result) -> None:
    for index, group in enumerate(result.exact_groups, start=1):
        same_name = "yes" if group.same_name else "no"
        same_suffix = "yes" if group.same_suffix else "no"
        print(
            f"\n[Group {index}] size={group.file_size} bytes | files={len(group.files)} | "
            f"same-name={same_name} | same-suffix={same_suffix}"
        )
        for path in group.files:
            print(f" - {path}")


def _validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    invalid_sources = [path for path in args.sources if not path.is_dir()]
    if invalid_sources:
        parser.error(
            "The following source directories do not exist or are not directories: "
            + ", ".join(str(path) for path in invalid_sources)
        )

    if args.target is not None and args.mode == "delete":
        parser.error("--target cannot be used together with --mode delete.")

    if args.apply and args.mode != "delete":
        parser.error("--apply is currently only supported together with --mode delete.")

    if args.apply and not args.yes:
        parser.error("--apply requires --yes for explicit confirmation.")


def _session_info_from_restore_result(
    requested_path: Path | None,
    restore_result: DuplicateSessionRestoreResult | None,
) -> dict[str, object]:
    if requested_path is None:
        return {
            "requested": False,
            "requested_path": None,
            "status": "not_requested",
            "reason": "no duplicate session snapshot was requested",
            "loaded_decisions": 0,
            "snapshot": None,
            "saved_path": None,
            "saved_decisions": 0,
        }

    snapshot = restore_result.snapshot if restore_result is not None else None
    return {
        "requested": True,
        "requested_path": str(requested_path),
        "status": restore_result.status if restore_result is not None else "error",
        "reason": restore_result.reason if restore_result is not None else "session restore result was unavailable",
        "loaded_decisions": len(restore_result.decisions) if restore_result is not None else 0,
        "snapshot": None
        if snapshot is None
        else {
            "schema_version": snapshot.schema_version,
            "created_at_utc": snapshot.created_at_utc,
            "exact_group_count": snapshot.exact_group_count,
            "decision_count": snapshot.decision_count,
        },
        "saved_path": None,
        "saved_decisions": 0,
    }


def _build_decisions(result, args: argparse.Namespace) -> tuple[dict[str, str], dict[str, object]]:
    decisions: dict[str, str] = {}
    restore_result = None
    session_info: dict[str, object]

    if args.load_session is not None:
        restore_result = restore_duplicate_session(args.load_session, result.exact_groups)
        decisions.update(restore_result.decisions)
        session_info = _session_info_from_restore_result(args.load_session, restore_result)
    else:
        session_info = _session_info_from_restore_result(None, None)

    if args.policy:
        auto_decisions = build_duplicate_decisions(result.exact_groups, args.policy)
        for group_id, keep_path in auto_decisions.items():
            decisions.setdefault(group_id, keep_path)

    return decisions, session_info


def _write_json_report(path: Path, result, bundle, execution_result, session_info: dict[str, object]) -> None:
    payload = {
        "session": session_info,
        "scan": {
            "scanned_files": result.scanned_files,
            "size_candidate_files": result.size_candidate_files,
            "hashed_files": result.hashed_files,
            "exact_groups": len(result.exact_groups),
            "duplicate_files": result.exact_duplicate_files,
            "extra_duplicates": result.exact_duplicates,
            "errors": result.errors,
        },
        "decisions": bundle.decisions,
        "cleanup_plan": {
            "total_groups": bundle.cleanup_plan.total_groups,
            "resolved_groups": bundle.cleanup_plan.resolved_groups,
            "unresolved_groups": bundle.cleanup_plan.unresolved_groups,
            "planned_removals": len(bundle.cleanup_plan.planned_removals),
            "estimated_reclaimable_bytes": bundle.cleanup_plan.estimated_reclaimable_bytes,
        },
        "dry_run": {
            "ready": bundle.dry_run.ready,
            "planned_count": bundle.dry_run.planned_count,
            "blocked_count": bundle.dry_run.blocked_count,
            "delete_count": bundle.dry_run.delete_count,
            "exclude_from_copy_count": bundle.dry_run.exclude_from_copy_count,
            "exclude_from_move_count": bundle.dry_run.exclude_from_move_count,
            "rows": [
                {
                    "action_type": row.action_type,
                    "group_id": row.group_id,
                    "operation_mode": row.operation_mode,
                    "source_path": str(row.source_path),
                    "survivor_path": str(row.survivor_path) if row.survivor_path else None,
                    "target_path": str(row.target_path) if row.target_path else None,
                    "file_size": row.file_size,
                    "reason": row.reason,
                    "status": row.status,
                }
                for row in [*bundle.dry_run.planned_actions, *bundle.dry_run.blocked_actions]
            ],
        },
        "execution_preview": {
            "ready": bundle.execution_preview.ready,
            "executable_count": bundle.execution_preview.executable_count,
            "deferred_count": bundle.execution_preview.deferred_count,
            "blocked_count": bundle.execution_preview.blocked_count,
            "delete_count": bundle.execution_preview.delete_count,
            "rows": [
                {
                    "row_type": row.row_type,
                    "status": row.status,
                    "group_id": row.group_id,
                    "operation_mode": row.operation_mode,
                    "source_path": str(row.source_path),
                    "survivor_path": str(row.survivor_path) if row.survivor_path else None,
                    "target_path": str(row.target_path) if row.target_path else None,
                    "file_size": row.file_size,
                    "reason": row.reason,
                }
                for row in bundle.execution_preview.rows
            ],
        },
        "execution_run": None
        if execution_result is None
        else {
            "processed_rows": execution_result.processed_rows,
            "executable_rows": execution_result.executable_rows,
            "executed_rows": execution_result.executed_rows,
            "deferred_rows": execution_result.deferred_rows,
            "blocked_rows": execution_result.blocked_rows,
            "error_rows": execution_result.error_rows,
            "entries": [
                {
                    "row_type": entry.row_type,
                    "status": entry.status,
                    "source_path": str(entry.source_path),
                    "survivor_path": str(entry.survivor_path) if entry.survivor_path else None,
                    "target_path": str(entry.target_path) if entry.target_path else None,
                    "outcome": entry.outcome,
                    "reason": entry.reason,
                }
                for entry in execution_result.entries
            ],
        },
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _print_workflow_summary(bundle) -> None:
    print(
        "Plan: "
        f"resolved={bundle.cleanup_plan.resolved_groups} | "
        f"unresolved={bundle.cleanup_plan.unresolved_groups} | "
        f"planned-removals={len(bundle.cleanup_plan.planned_removals)} | "
        f"estimated-reclaimable={bundle.cleanup_plan.estimated_reclaimable_bytes} bytes"
    )
    print(
        "Dry run: "
        f"ready={bundle.dry_run.ready} | "
        f"planned={bundle.dry_run.planned_count} | "
        f"blocked={bundle.dry_run.blocked_count} | "
        f"delete={bundle.dry_run.delete_count} | "
        f"exclude-from-copy={bundle.dry_run.exclude_from_copy_count} | "
        f"exclude-from-move={bundle.dry_run.exclude_from_move_count}"
    )
    print(
        "Execution preview: "
        f"ready={bundle.execution_preview.ready} | "
        f"executable={bundle.execution_preview.executable_count} | "
        f"deferred={bundle.execution_preview.deferred_count} | "
        f"blocked={bundle.execution_preview.blocked_count} | "
        f"delete={bundle.execution_preview.delete_count}"
    )


def _print_session_info(session_info: dict[str, object]) -> None:
    print("Session:")
    print(f"  Requested: {session_info['requested']}")
    print(f"  Status: {session_info['status']}")
    print(f"  Reason: {session_info['reason']}")
    if session_info.get("requested_path"):
        print(f"  Requested path: {session_info['requested_path']}")
    if session_info.get("snapshot"):
        snapshot = session_info["snapshot"]
        print(
            "  Snapshot: "
            f"schema={snapshot['schema_version']} | "
            f"created={snapshot['created_at_utc'] or '-'} | "
            f"groups={snapshot['exact_group_count']} | "
            f"decisions={snapshot['decision_count']}"
        )
    print(f"  Loaded decisions: {session_info['loaded_decisions']}")
    if session_info.get("saved_path"):
        print(f"  Saved path: {session_info['saved_path']}")
        print(f"  Saved decisions: {session_info['saved_decisions']}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _validate_args(parser, args)

    result = scan_exact_duplicates(DuplicateScanConfig(source_dirs=args.sources))
    print(
        f"Scanned: {result.scanned_files} | Size candidates: {result.size_candidate_files} | "
        f"Hashed: {result.hashed_files} | Exact groups: {len(result.exact_groups)} | "
        f"Duplicate files: {result.exact_duplicate_files} | Extra duplicates: {result.exact_duplicates} | Errors: {result.errors}"
    )

    if args.show_groups and result.exact_groups:
        _print_duplicate_groups(result)

    decisions, session_info = _build_decisions(result, args)
    bundle = build_duplicate_workflow_bundle(
        result.exact_groups,
        decisions,
        args.mode,
        target_root=args.target,
    )

    if args.save_session is not None:
        snapshot = save_duplicate_session_snapshot(args.save_session, result.exact_groups, bundle.decisions)
        session_info["saved_path"] = str(args.save_session)
        session_info["saved_decisions"] = snapshot.decision_count
        print(f"Saved duplicate session: {args.save_session}")

    if args.show_session or args.load_session:
        _print_session_info(session_info)

    if args.show_plan or args.policy or args.load_session or args.apply:
        _print_workflow_summary(bundle)
        print(f"Decisions: {len(bundle.decisions)}")

    execution_result = None
    if args.apply:
        execution_result = execute_duplicate_workflow_bundle(bundle, apply=True)
        print(
            "Execution run: "
            f"processed={execution_result.processed_rows} | "
            f"executed={execution_result.executed_rows} | "
            f"deferred={execution_result.deferred_rows} | "
            f"blocked={execution_result.blocked_rows} | "
            f"errors={execution_result.error_rows}"
        )

    if args.json_report is not None:
        _write_json_report(args.json_report, result, bundle, execution_result, session_info)
        print(f"Wrote JSON report: {args.json_report}")

    if execution_result is not None:
        if execution_result.error_rows > 0:
            return 2
        if args.apply and (execution_result.blocked_rows > 0 or execution_result.deferred_rows > 0):
            return 3
    return 0 if result.errors == 0 else 1
