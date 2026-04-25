from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .cleanup_plan import build_exact_group_id
from .core.duplicate_decisions import (
    build_duplicate_decision_template,
    duplicate_decision_import_payload,
    load_duplicate_decision_file,
    write_duplicate_decision_template,
)
from .core.duplicate_report import (
    build_duplicate_outcome_report,
    build_duplicate_review_export,
    build_duplicate_summary,
)
from .core.run_artifacts import write_run_artifacts
from .core.report_export import write_json_report
from .core.state import (
    write_command_run_log,
    write_execution_journal,
    write_history_artifacts,
)
from .duplicate_session_store import (
    restore_duplicate_session,
    save_duplicate_session_snapshot,
)
from .duplicate_workflow import (
    build_duplicate_decisions,
    build_duplicate_workflow_bundle,
    execute_duplicate_workflow_bundle,
)
from .duplicates import DuplicateScanConfig, scan_exact_duplicates
from .media_formats import (
    extensions_for_media_kinds,
    normalize_extensions,
    summarize_supported_media_formats,
    unsupported_media_extensions,
)
from .similar_images import SimilarImageScanConfig, scan_similar_images
from .similar_review import build_similar_review_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="media-manager duplicates")
    parser.add_argument(
        "--source",
        dest="sources",
        action="append",
        type=Path,
        default=[],
        help="Source directory. Repeat the flag to add multiple source folders.",
    )
    parser.add_argument(
        "--show-groups",
        action="store_true",
        help="Print all confirmed exact duplicate groups.",
    )
    parser.add_argument(
        "--similar-images",
        action="store_true",
        help="Also scan images for likely visual duplicates using perceptual hashing.",
    )
    parser.add_argument(
        "--show-similar-groups",
        action="store_true",
        help="Print grouped similar-image candidates when --similar-images is enabled.",
    )
    parser.add_argument(
        "--show-similar-review",
        action="store_true",
        help="Print keep recommendations and review candidates for similar-image groups.",
    )
    parser.add_argument(
        "--similar-policy",
        choices=["first", "newest", "oldest"],
        default="first",
        help="Keep recommendation policy for similar-image review output. Default: first.",
    )
    parser.add_argument(
        "--similar-threshold",
        type=int,
        default=6,
        help="Maximum Hamming distance for likely similar images (default: 6).",
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
        "--include-pattern",
        action="append",
        default=[],
        help="Only include paths matching this glob-style pattern. Repeat to add multiple include rules.",
    )

    parser.add_argument(
        "--media-kind",
        action="append",
        choices=["all", "image", "raw-image", "video", "audio"],
        default=[],
        help="Restrict duplicate scanning by media kind. Repeat to combine kinds. Default: all supported media.",
    )
    parser.add_argument(
        "--include-extension",
        action="append",
        default=[],
        help="Only include this media extension for exact duplicate scanning, for example .mp4. Repeat to add more.",
    )
    parser.add_argument(
        "--exclude-extension",
        action="append",
        default=[],
        help="Exclude this media extension from exact duplicate scanning, for example .mov. Repeat to add more.",
    )
    parser.add_argument(
        "--list-supported-formats",
        action="store_true",
        help="Print supported media formats and duplicate capabilities, then exit.",
    )
    parser.add_argument(
        "--exclude-pattern",
        action="append",
        default=[],
        help="Exclude paths matching this glob-style pattern. Repeat to add multiple exclude rules.",
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
        "--import-decisions",
        type=Path,
        help="Import editable exact-duplicate keep decisions from a JSON decision file.",
    )
    parser.add_argument(
        "--export-decisions",
        type=Path,
        help="Write an editable exact-duplicate decision JSON file for review.",
    )
    parser.add_argument(
        "--save-session",
        type=Path,
        help="Save the current exact-duplicate keep decisions as a session snapshot.",
    )
    parser.add_argument(
        "--show-decisions",
        action="store_true",
        help="Print one line per exact-duplicate keep decision and where it came from.",
    )
    parser.add_argument(
        "--show-unresolved",
        action="store_true",
        help="Print unresolved exact duplicate groups and their candidate paths.",
    )
    parser.add_argument(
        "--show-plan",
        action="store_true",
        help="Print cleanup-plan, dry-run, and execution-preview counters.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the full machine-readable duplicate report to stdout.",
    )
    parser.add_argument(
        "--json-report",
        type=Path,
        help="Deprecated alias for --report-json. Write the full duplicate JSON report to a file.",
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        help="Write the full duplicate JSON report to a file.",
    )
    parser.add_argument(
        "--review-json",
        type=Path,
        help="Write a compact duplicate review JSON export to a file.",
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
        "--run-dir",
        type=Path,
        help="Optional directory where a structured run folder is written with command.json, report.json, review.json, summary.txt, and optional journal.json.",
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


def _print_similar_groups(result) -> None:
    for index, group in enumerate(result.similar_groups, start=1):
        print(f"\n[Similar Group {index}] files={len(group.members)} | anchor={group.anchor_path}")
        for member in group.members:
            marker = "anchor" if member.path == group.anchor_path else f"distance={member.distance}"
            print(f" - {member.path} ({marker})")


def _print_similar_review(report) -> None:
    current_group = None
    for row in report.rows:
        if row.group_index != current_group:
            current_group = row.group_index
            print(f"\n[Similar Review Group {current_group}] keep-policy={report.keep_policy}")
        print(
            f" - [{row.status}] {row.path} | keep={row.recommended_keep_path} | "
            f"distance-to-keep={row.distance_to_keep} | reason={row.reason}"
        )


def _validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if not args.sources:
        parser.error("--source is required unless --list-supported-formats is used.")

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

    if args.journal is not None and not args.apply:
        parser.error("--journal is only meaningful together with --apply.")

    if args.similar_threshold < 0:
        parser.error("--similar-threshold must be zero or greater.")

    if args.show_similar_review and not args.similar_images:
        parser.error("--show-similar-review requires --similar-images.")

    unsupported_include_extensions = unsupported_media_extensions(tuple(args.include_extension or ()))
    if unsupported_include_extensions:
        parser.error(
            "Unsupported --include-extension value(s): "
            + ", ".join(sorted(unsupported_include_extensions))
            + ". Use --list-supported-formats to inspect the supported media catalog."
        )

    unsupported_exclude_extensions = unsupported_media_extensions(tuple(args.exclude_extension or ()))
    if unsupported_exclude_extensions:
        parser.error(
            "Unsupported --exclude-extension value(s): "
            + ", ".join(sorted(unsupported_exclude_extensions))
            + ". Use --list-supported-formats to inspect the supported media catalog."
        )



def _duplicate_media_extensions_from_args(args: argparse.Namespace) -> frozenset[str] | None:
    selected_kinds = tuple(args.media_kind or ())
    include_extensions = normalize_extensions(tuple(args.include_extension or ()))
    exclude_extensions = normalize_extensions(tuple(args.exclude_extension or ()))

    extensions: set[str] | None = None
    if selected_kinds and "all" not in selected_kinds:
        extensions = extensions_for_media_kinds(selected_kinds)
    if include_extensions:
        extensions = set(include_extensions) if extensions is None else extensions & include_extensions
    if exclude_extensions:
        extensions = extensions_for_media_kinds(("all",)) if extensions is None else set(extensions)
        extensions -= exclude_extensions

    if extensions is None:
        return None
    return frozenset(sorted(extensions))


def _print_supported_formats() -> None:
    summary = summarize_supported_media_formats()
    print("Supported media formats")
    print(f"  Total extensions: {summary['total_extensions']}")
    print("  Media kinds:")
    for kind, count in summary["media_kind_summary"].items():
        print(f"    {kind}: {count}")
    print("\n  Extensions:")
    for item in summary["formats"]:
        exact = "yes" if item["exact_duplicates"] else "no"
        similar = "yes" if item["similar_images"] else "no"
        print(f"    {item['extension']:>6} | {item['media_kind']:<9} | exact={exact:<3} | similar={similar:<3} | {item['notes']}")

def _build_decisions(result, args: argparse.Namespace) -> tuple[dict[str, str], object | None, object | None]:
    decisions: dict[str, str] = {}
    session_restore = None
    decision_import = None

    if args.import_decisions is not None:
        decision_import = load_duplicate_decision_file(args.import_decisions, result.exact_groups)
        decisions.update(decision_import.decisions)

    if args.load_session is not None:
        session_restore = restore_duplicate_session(args.load_session, result.exact_groups)
        decisions.update(session_restore.decisions)

    if args.policy:
        auto_decisions = build_duplicate_decisions(result.exact_groups, args.policy)
        for group_id, keep_path in auto_decisions.items():
            decisions.setdefault(group_id, keep_path)

    return decisions, session_restore, decision_import


def _session_restore_payload(session_restore) -> dict[str, object] | None:
    if session_restore is None:
        return None

    snapshot = getattr(session_restore, "snapshot", None)
    return {
        "status": session_restore.status,
        "reason": session_restore.reason,
        "decision_count": len(getattr(session_restore, "decisions", {})),
        "snapshot_exact_group_count": None if snapshot is None else snapshot.exact_group_count,
        "snapshot_decision_count": None if snapshot is None else snapshot.decision_count,
    }


def _decision_origin_map(decisions: dict[str, str], session_restore, decision_import=None) -> dict[str, str]:
    import_group_ids = set() if decision_import is None else set(getattr(decision_import, "decisions", {}).keys())
    session_group_ids = set() if session_restore is None else set(getattr(session_restore, "decisions", {}).keys())
    origin: dict[str, str] = {}
    for group_id in decisions:
        if group_id in session_group_ids:
            origin[group_id] = "session"
        elif group_id in import_group_ids:
            origin[group_id] = "decision_file"
        else:
            origin[group_id] = "policy"
    return origin


def _build_decision_rows(exact_groups, decisions: dict[str, str], session_restore, decision_import=None) -> list[dict[str, object]]:
    origin_map = _decision_origin_map(decisions, session_restore, decision_import)
    rows: list[dict[str, object]] = []
    for group in exact_groups:
        group_id = build_exact_group_id(group)
        keep_path = decisions.get(group_id)
        rows.append(
            {
                "group_id": group_id,
                "file_size": group.file_size,
                "candidate_count": len(group.files),
                "keep_path": keep_path,
                "status": "decided" if keep_path else "unresolved",
                "origin": None if keep_path is None else origin_map.get(group_id, "policy"),
                "candidate_paths": [str(path) for path in group.files],
            }
        )
    return rows


def _build_decision_summary(exact_groups, decisions: dict[str, str], session_restore, decision_import=None) -> dict[str, object]:
    total_groups = len(exact_groups)
    import_group_ids = set() if decision_import is None else set(getattr(decision_import, "decisions", {}).keys())
    session_group_ids = set() if session_restore is None else set(getattr(session_restore, "decisions", {}).keys())
    decided_group_ids = set(decisions.keys())
    unresolved_group_ids = [build_exact_group_id(group) for group in exact_groups if build_exact_group_id(group) not in decided_group_ids]
    return {
        "total_groups": total_groups,
        "decided_groups": len(decided_group_ids),
        "undecided_groups": len(unresolved_group_ids),
        "from_decision_file_count": sum(1 for group_id in decided_group_ids if group_id in import_group_ids and group_id not in session_group_ids),
        "from_session_count": sum(1 for group_id in decided_group_ids if group_id in session_group_ids),
        "from_policy_count": sum(1 for group_id in decided_group_ids if group_id not in session_group_ids and group_id not in import_group_ids),
        "session_status": None if session_restore is None else getattr(session_restore, "status", None),
        "decision_file_status": None if decision_import is None else getattr(decision_import, "status", None),
        "unresolved_group_ids": unresolved_group_ids,
    }


def _print_decision_rows(rows: list[dict[str, object]]) -> None:
    for row in rows:
        if row["status"] == "decided":
            print(f" - [decided] {row['group_id']} | keep={row['keep_path']} | origin={row['origin']} | candidates={row['candidate_count']}")
        else:
            print(f" - [unresolved] {row['group_id']} | candidates={row['candidate_count']}")


def _print_unresolved_groups(bundle) -> None:
    for item in getattr(getattr(bundle, "cleanup_plan", None), "unresolved", []):
        print(f"\n[Unresolved Group] {item.group_id} | size={item.file_size} | candidates={len(item.candidate_paths)}")
        for path in item.candidate_paths:
            print(f" - {path}")


def _execution_preview_reason_summary(preview) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {"executable": {}, "deferred": {}, "blocked": {}}
    for row in getattr(preview, "rows", []):
        bucket = summary.get(row.status)
        if bucket is None:
            continue
        bucket[row.reason] = bucket.get(row.reason, 0) + 1
    return summary


def _build_execution_reason_summary(execution_result) -> dict[str, int]:
    summary: dict[str, int] = {}
    if execution_result is None:
        return summary
    for entry in execution_result.entries:
        reason = str(entry.reason)
        summary[reason] = summary.get(reason, 0) + 1
    return dict(sorted(summary.items()))


def _build_json_report_payload(
    result,
    bundle,
    execution_result,
    *,
    session_restore=None,
    decision_import=None,
    similar_result=None,
    similar_review=None,
    mode: str = "copy",
    policy: str | None = None,
    include_patterns: tuple[str, ...] = (),
    exclude_patterns: tuple[str, ...] = (),
    media_kinds: tuple[str, ...] = (),
    media_extensions: frozenset[str] | None = None,
    apply_requested: bool = False,
) -> dict[str, object]:
    cleanup_plan = getattr(bundle, "cleanup_plan", None)
    dry_run = getattr(bundle, "dry_run", None)
    execution_preview = getattr(bundle, "execution_preview", None)

    cleanup_total_groups = getattr(cleanup_plan, "total_groups", len(getattr(result, "exact_groups", [])))
    cleanup_resolved_groups = getattr(cleanup_plan, "resolved_groups", 0)
    cleanup_unresolved_groups = getattr(cleanup_plan, "unresolved_groups", 0)
    cleanup_planned_removals = getattr(cleanup_plan, "planned_removals", [])
    cleanup_estimated_reclaimable_bytes = getattr(cleanup_plan, "estimated_reclaimable_bytes", 0)
    cleanup_unresolved = getattr(cleanup_plan, "unresolved", [])

    planned_actions = list(getattr(dry_run, "planned_actions", []))
    blocked_actions = list(getattr(dry_run, "blocked_actions", []))
    preview_rows = list(getattr(execution_preview, "rows", []))

    decision_rows = _build_decision_rows(result.exact_groups, bundle.decisions, session_restore, decision_import)
    review_export = build_duplicate_review_export(
        scan_result=result,
        bundle=bundle,
        decision_rows=decision_rows,
        similar_review=similar_review,
    )
    outcome_report = build_duplicate_outcome_report(
        scan_result=result,
        bundle=bundle,
        execution_result=execution_result,
        apply_requested=apply_requested,
        mode=mode,
        policy=policy,
    )

    payload = {
        "command": "duplicates",
        "mode": mode,
        "policy": policy,
        "apply_requested": bool(apply_requested),
        "include_patterns": list(include_patterns),
        "exclude_patterns": list(exclude_patterns),
        "media_kinds": list(media_kinds),
        "media_extensions": None if media_extensions is None else sorted(media_extensions),
        "supported_formats": summarize_supported_media_formats(),
        "summary": build_duplicate_summary(result, bundle, execution_result),
        "outcome_report": outcome_report,
        "review": review_export,
        "scan": {
            "scanned_files": result.scanned_files,
            "size_candidate_files": result.size_candidate_files,
            "hashed_files": result.hashed_files,
            "exact_groups": len(result.exact_groups),
            "duplicate_files": result.exact_duplicate_files,
            "extra_duplicates": result.exact_duplicates,
            "errors": result.errors,
            "size_group_errors": getattr(result, "size_group_errors", 0),
            "sample_errors": getattr(result, "sample_errors", 0),
            "hash_errors": getattr(result, "hash_errors", 0),
            "compare_errors": getattr(result, "compare_errors", 0),
            "stage_errors": {
                "size_group_errors": getattr(result, "size_group_errors", 0),
                "sample_errors": getattr(result, "sample_errors", 0),
                "hash_errors": getattr(result, "hash_errors", 0),
                "compare_errors": getattr(result, "compare_errors", 0),
            },
            "skipped_filtered_files": getattr(result, "skipped_filtered_files", 0),
            "extension_summary": dict(sorted(getattr(result, "extension_summary", {}).items())),
            "media_kind_summary": dict(sorted(getattr(result, "media_kind_summary", {}).items())),
            "image_file_count": getattr(result, "image_file_count", 0),
            "raw_image_file_count": getattr(result, "raw_image_file_count", 0),
            "video_file_count": getattr(result, "video_file_count", 0),
            "audio_file_count": getattr(result, "audio_file_count", 0),
        },
        "similar_images": None if similar_result is None else {
            "scanned_files": similar_result.scanned_files,
            "image_files": similar_result.image_files,
            "hashed_files": similar_result.hashed_files,
            "similar_pairs": similar_result.similar_pairs,
            "group_count": len(similar_result.similar_groups),
            "errors": similar_result.errors,
            "skipped_filtered_files": getattr(similar_result, "skipped_filtered_files", 0),
            "groups": [
                {
                    "anchor_path": str(group.anchor_path),
                    "members": [
                        {
                            "path": str(member.path),
                            "hash_hex": member.hash_hex,
                            "distance": member.distance,
                        }
                        for member in group.members
                    ],
                }
                for group in similar_result.similar_groups
            ],
        },
        "similar_review": None if similar_review is None else {
            "keep_policy": similar_review.keep_policy,
            "group_count": similar_review.group_count,
            "row_count": similar_review.row_count,
            "keep_count": similar_review.keep_count,
            "review_candidate_count": similar_review.review_candidate_count,
            "rows": [
                {
                    "group_index": row.group_index,
                    "path": str(row.path),
                    "recommended_keep_path": str(row.recommended_keep_path),
                    "status": row.status,
                    "distance_to_keep": row.distance_to_keep,
                    "hash_hex": row.hash_hex,
                    "reason": row.reason,
                }
                for row in similar_review.rows
            ],
        },
        "session_restore": _session_restore_payload(session_restore),
        "decision_import": duplicate_decision_import_payload(decision_import),
        "decision_summary": _build_decision_summary(result.exact_groups, bundle.decisions, session_restore, decision_import),
        "decision_rows": decision_rows,
        "decisions": bundle.decisions,
        "cleanup_plan": {
            "total_groups": cleanup_total_groups,
            "resolved_groups": cleanup_resolved_groups,
            "unresolved_groups": cleanup_unresolved_groups,
            "planned_removals": len(cleanup_planned_removals),
            "estimated_reclaimable_bytes": cleanup_estimated_reclaimable_bytes,
            "unresolved": [
                {
                    "group_id": item.group_id,
                    "file_size": item.file_size,
                    "candidate_count": len(item.candidate_paths),
                    "candidate_paths": [str(path) for path in item.candidate_paths],
                }
                for item in cleanup_unresolved
            ],
        },
        "dry_run": {
            "ready": getattr(dry_run, "ready", False),
            "planned_count": getattr(dry_run, "planned_count", len(planned_actions)),
            "blocked_count": getattr(dry_run, "blocked_count", len(blocked_actions)),
            "delete_count": getattr(dry_run, "delete_count", 0),
            "exclude_from_copy_count": getattr(dry_run, "exclude_from_copy_count", 0),
            "exclude_from_move_count": getattr(dry_run, "exclude_from_move_count", 0),
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
                for row in [*planned_actions, *blocked_actions]
            ],
        },
        "execution_preview": {
            "ready": getattr(execution_preview, "ready", False),
            "executable_count": getattr(execution_preview, "executable_count", 0),
            "deferred_count": getattr(execution_preview, "deferred_count", 0),
            "blocked_count": getattr(execution_preview, "blocked_count", 0),
            "delete_count": getattr(execution_preview, "delete_count", 0),
            "reason_summary": _execution_preview_reason_summary(execution_preview),
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
                for row in preview_rows
            ],
        },
        "execution_run": None
        if execution_result is None
        else {
            "processed_rows": execution_result.processed_rows,
            "executable_rows": execution_result.executable_rows,
            "executed_rows": execution_result.executed_rows,
            "previewed_rows": getattr(execution_result, "previewed_rows", 0),
            "deleted_rows": getattr(execution_result, "deleted_rows", 0),
            "deferred_rows": execution_result.deferred_rows,
            "blocked_rows": execution_result.blocked_rows,
            "blocked_associated_rows": getattr(execution_result, "blocked_associated_rows", 0),
            "blocked_missing_survivor_rows": getattr(execution_result, "blocked_missing_survivor_rows", 0),
            "error_rows": execution_result.error_rows,
            "outcome_summary": {
                "preview-delete": getattr(execution_result, "previewed_rows", 0),
                "deleted": getattr(execution_result, "deleted_rows", 0),
                "deferred": execution_result.deferred_rows,
                "blocked": execution_result.blocked_rows,
                "error": execution_result.error_rows,
            },
            "reason_summary": _build_execution_reason_summary(execution_result),
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

    return payload


def _write_json_report(path: Path, *args, **kwargs) -> None:
    if len(args) == 1 and isinstance(args[0], dict) and not kwargs:
        payload = args[0]
    else:
        payload = _build_json_report_payload(*args, **kwargs)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _build_duplicate_journal_entries(execution_result) -> list[dict[str, object]]:
    if execution_result is None:
        return []

    entries: list[dict[str, object]] = []
    for entry in execution_result.entries:
        entries.append(
            {
                "source_path": str(entry.source_path),
                "target_path": None if entry.target_path is None else str(entry.target_path),
                "outcome": entry.outcome,
                "reason": entry.reason,
                "reversible": False,
                "undo_action": None,
                "undo_from_path": None,
                "undo_to_path": None,
            }
        )
    return entries


def _print_workflow_summary(bundle, *, session_restore=None) -> None:
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
    if session_restore is not None:
        payload = _session_restore_payload(session_restore)
        if payload is not None:
            print(
                "Session restore: "
                f"status={payload['status']} | decisions={payload['decision_count']} | "
                f"reason={payload['reason']}"
            )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    argv_for_artifacts = list(sys.argv[1:] if argv is None else argv)
    if args.list_supported_formats:
        _print_supported_formats()
        return 0
    _validate_args(parser, args)

    report_json_path = args.report_json if args.report_json is not None else args.json_report
    emit_text = not args.json
    media_extensions = _duplicate_media_extensions_from_args(args)

    result = scan_exact_duplicates(
        DuplicateScanConfig(
            source_dirs=args.sources,
            include_patterns=tuple(args.include_pattern or ()),
            exclude_patterns=tuple(args.exclude_pattern or ()),
            media_extensions=media_extensions,
        )
    )
    if emit_text:
        print(
            f"Scanned: {result.scanned_files} | Size candidates: {result.size_candidate_files} | "
            f"Hashed: {result.hashed_files} | Exact groups: {len(result.exact_groups)} | "
            f"Duplicate files: {result.exact_duplicate_files} | Extra duplicates: {result.exact_duplicates} | "
            f"Filtered: {getattr(result, 'skipped_filtered_files', 0)} | "
            f"Images: {getattr(result, 'image_file_count', 0)} | Raw: {getattr(result, 'raw_image_file_count', 0)} | "
            f"Videos: {getattr(result, 'video_file_count', 0)} | Audio: {getattr(result, 'audio_file_count', 0)} | "
            f"Errors: {result.errors}"
        )

    if emit_text and args.show_groups and result.exact_groups:
        _print_duplicate_groups(result)

    similar_result = None
    similar_review = None
    if args.similar_images or args.show_similar_groups:
        similar_result = scan_similar_images(
            SimilarImageScanConfig(
                source_dirs=args.sources,
                max_distance=args.similar_threshold,
                include_patterns=tuple(args.include_pattern or ()),
                exclude_patterns=tuple(args.exclude_pattern or ()),
                media_extensions=media_extensions,
            )
        )
        if emit_text:
            print(
                f"Similar images: scanned={similar_result.scanned_files} | images={similar_result.image_files} | "
                f"hashed={similar_result.hashed_files} | groups={len(similar_result.similar_groups)} | "
                f"pairs={similar_result.similar_pairs} | errors={similar_result.errors}"
            )
        if emit_text and args.show_similar_groups and similar_result.similar_groups:
            _print_similar_groups(similar_result)

    if similar_result is not None:
        similar_review = build_similar_review_report(
            similar_result.similar_groups,
            keep_policy=args.similar_policy,
        )
        if emit_text and args.show_similar_review and similar_review.rows:
            _print_similar_review(similar_review)

    decisions, session_restore, decision_import = _build_decisions(result, args)
    bundle = build_duplicate_workflow_bundle(
        result.exact_groups,
        decisions,
        args.mode,
        target_root=args.target,
    )

    if args.save_session is not None:
        save_duplicate_session_snapshot(args.save_session, result.exact_groups, bundle.decisions)
        if emit_text:
            print(f"Saved duplicate session: {args.save_session}")

    if args.export_decisions is not None:
        decision_payload = build_duplicate_decision_template(
            exact_groups=result.exact_groups,
            decisions=bundle.decisions,
            decision_origins=_decision_origin_map(bundle.decisions, session_restore, decision_import),
            mode=args.mode,
            policy=args.policy,
            include_patterns=tuple(args.include_pattern or ()),
            exclude_patterns=tuple(args.exclude_pattern or ()),
            media_kinds=tuple(args.media_kind or ()),
            media_extensions=media_extensions,
        )
        write_duplicate_decision_template(args.export_decisions, decision_payload)
        if emit_text:
            print(f"Wrote duplicate decision file: {args.export_decisions}")

    if emit_text and (args.show_plan or args.policy or args.load_session or args.import_decisions or args.apply):
        _print_workflow_summary(bundle, session_restore=session_restore)
        if decision_import is not None:
            print(
                "Decision import: "
                f"status={decision_import.status} | matched={decision_import.matched_decision_count} | "
                f"ignored={decision_import.ignored_decision_count} | reason={decision_import.reason}"
            )
        decision_summary = _build_decision_summary(result.exact_groups, bundle.decisions, session_restore, decision_import)
        print(
            f"Decision summary: decided={decision_summary['decided_groups']} | "
            f"undecided={decision_summary['undecided_groups']} | "
            f"from-file={decision_summary['from_decision_file_count']} | "
            f"from-session={decision_summary['from_session_count']} | "
            f"from-policy={decision_summary['from_policy_count']}"
        )
        print(f"Decisions: {len(bundle.decisions)}")

    if emit_text and args.show_decisions:
        print("Decision rows:")
        _print_decision_rows(_build_decision_rows(result.exact_groups, bundle.decisions, session_restore, decision_import))

    if emit_text and args.show_unresolved:
        _print_unresolved_groups(bundle)

    execution_result = None
    if args.apply:
        execution_result = execute_duplicate_workflow_bundle(bundle, apply=True)
        if emit_text:
            print(
                "Execution run: "
                f"processed={execution_result.processed_rows} | "
                f"executed={execution_result.executed_rows} | "
                f"deferred={execution_result.deferred_rows} | "
                f"blocked={execution_result.blocked_rows} | "
                f"errors={execution_result.error_rows}"
            )

    payload = _build_json_report_payload(
        result,
        bundle,
        execution_result,
        session_restore=session_restore,
        decision_import=decision_import,
        similar_result=similar_result,
        similar_review=similar_review,
        mode=args.mode,
        policy=args.policy,
        include_patterns=tuple(args.include_pattern or ()),
        exclude_patterns=tuple(args.exclude_pattern or ()),
        media_kinds=tuple(args.media_kind or ()),
        media_extensions=media_extensions,
        apply_requested=args.apply,
    )

    exit_code = 0
    if execution_result is not None and execution_result.error_rows > 0:
        exit_code = 2
    elif decision_import is not None and decision_import.status in {"missing", "error", "mismatch"}:
        exit_code = 1
    elif similar_result is not None and similar_result.errors > 0:
        exit_code = 1
    elif result.errors > 0:
        exit_code = 1

    explicit_journal_entries = _build_duplicate_journal_entries(execution_result) if execution_result is not None else None
    history_artifacts = None
    run_artifacts = None
    review_payload = {
        "command": "duplicates",
        "sources": [str(path) for path in args.sources],
        "mode": args.mode,
        "policy": args.policy,
        "include_patterns": list(args.include_pattern or ()),
        "exclude_patterns": list(args.exclude_pattern or ()),
        "media_kinds": list(args.media_kind or ()),
        "media_extensions": None if media_extensions is None else sorted(media_extensions),
        "decision_import": payload.get("decision_import"),
        "decision_summary": payload.get("decision_summary"),
        "outcome_report": payload.get("outcome_report"),
        "review": payload.get("review", {}),
    }

    if args.run_log is not None:
        write_command_run_log(
            args.run_log,
            command_name="duplicates",
            apply_requested=args.apply,
            exit_code=exit_code,
            payload=payload,
        )
        if emit_text:
            print(f"Wrote run log: {args.run_log}")

    if args.apply and args.journal is not None and execution_result is not None:
        write_execution_journal(
            args.journal,
            command_name="duplicates",
            apply_requested=True,
            exit_code=exit_code,
            entries=explicit_journal_entries or [],
        )
        if emit_text:
            print(f"Wrote execution journal: {args.journal}")

    if args.history_dir is not None:
        history_artifacts = write_history_artifacts(
            args.history_dir,
            command_name="duplicates",
            apply_requested=args.apply,
            exit_code=exit_code,
            payload=payload,
            journal_entries=explicit_journal_entries if args.apply else None,
        )

    if report_json_path is not None:
        _write_json_report(report_json_path, payload)
        if emit_text:
            print(f"Wrote JSON report: {report_json_path}")

    if args.review_json is not None:
        write_json_report(args.review_json, review_payload)
        if emit_text:
            print(f"Wrote review JSON: {args.review_json}")

    if args.run_dir is not None:
        run_artifacts = write_run_artifacts(
            args.run_dir,
            command_name="duplicates",
            argv=argv_for_artifacts,
            apply_requested=args.apply,
            exit_code=exit_code,
            payload=payload,
            review_payload=review_payload,
            journal_entries=explicit_journal_entries if args.apply else None,
        )

    if history_artifacts is not None:
        if emit_text:
            print(f"Wrote history run log: {history_artifacts['run_log_path']}")
            if "execution_journal_path" in history_artifacts:
                print(f"Wrote history journal: {history_artifacts['execution_journal_path']}")
    if run_artifacts is not None and emit_text:
        print(f"Wrote run artifacts: {run_artifacts['run_dir']}")

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))

    return exit_code
