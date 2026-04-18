from __future__ import annotations

import argparse
import json
from pathlib import Path

from .duplicate_session_store import restore_duplicate_decisions, save_duplicate_session_snapshot
from .duplicate_workflow import (
    build_duplicate_decisions,
    build_duplicate_workflow_bundle,
    execute_duplicate_workflow_bundle,
)
from .duplicates import DuplicateScanConfig, scan_exact_duplicates
from .similar_images import SimilarImageScanConfig, scan_similar_images
from .similar_review import build_similar_review_report


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
        help="Write a JSON report with scan, decision, dry-run, execution-preview, and similar-image data.",
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

    if args.similar_threshold < 0:
        parser.error("--similar-threshold must be zero or greater.")

    if args.show_similar_review and not args.similar_images:
        parser.error("--show-similar-review requires --similar-images.")


def _build_decisions(result, args: argparse.Namespace) -> dict[str, str]:
    decisions: dict[str, str] = {}

    if args.load_session is not None:
        decisions.update(restore_duplicate_decisions(args.load_session, result.exact_groups))

    if args.policy:
        auto_decisions = build_duplicate_decisions(result.exact_groups, args.policy)
        for group_id, keep_path in auto_decisions.items():
            decisions.setdefault(group_id, keep_path)

    return decisions


def _write_json_report(path: Path, result, bundle, execution_result, *, similar_result=None, similar_review=None) -> None:
    payload = {
        "scan": {
            "scanned_files": result.scanned_files,
            "size_candidate_files": result.size_candidate_files,
            "hashed_files": result.hashed_files,
            "exact_groups": len(result.exact_groups),
            "duplicate_files": result.exact_duplicate_files,
            "extra_duplicates": result.exact_duplicates,
            "errors": result.errors,
        },
        "similar_images": None if similar_result is None else {
            "scanned_files": similar_result.scanned_files,
            "image_files": similar_result.image_files,
            "hashed_files": similar_result.hashed_files,
            "similar_pairs": similar_result.similar_pairs,
            "group_count": len(similar_result.similar_groups),
            "errors": similar_result.errors,
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
            "previewed_rows": execution_result.previewed_rows,
            "deleted_rows": execution_result.deleted_rows,
            "deferred_rows": execution_result.deferred_rows,
            "blocked_rows": execution_result.blocked_rows,
            "blocked_associated_rows": execution_result.blocked_associated_rows,
            "blocked_missing_survivor_rows": execution_result.blocked_missing_survivor_rows,
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

    similar_result = None
    similar_review = None
    if args.similar_images or args.show_similar_groups:
        similar_result = scan_similar_images(
            SimilarImageScanConfig(
                source_dirs=args.sources,
                max_distance=args.similar_threshold,
            )
        )
        print(
            f"Similar images: scanned={similar_result.scanned_files} | images={similar_result.image_files} | "
            f"hashed={similar_result.hashed_files} | groups={len(similar_result.similar_groups)} | "
            f"pairs={similar_result.similar_pairs} | errors={similar_result.errors}"
        )
        if args.show_similar_groups and similar_result.similar_groups:
            _print_similar_groups(similar_result)

    if similar_result is not None:
        similar_review = build_similar_review_report(
            similar_result.similar_groups,
            keep_policy=args.similar_policy,
        )
        if args.show_similar_review and similar_review.rows:
            _print_similar_review(similar_review)

    decisions = _build_decisions(result, args)
    bundle = build_duplicate_workflow_bundle(
        result.exact_groups,
        decisions,
        args.mode,
        target_root=args.target,
    )

    if args.save_session is not None:
        save_duplicate_session_snapshot(args.save_session, result.exact_groups, bundle.decisions)
        print(f"Saved duplicate session: {args.save_session}")

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
            f"deleted={execution_result.deleted_rows} | "
            f"blocked={execution_result.blocked_rows} | "
            f"errors={execution_result.error_rows}"
        )

    if args.json_report is not None:
        _write_json_report(
            args.json_report,
            result,
            bundle,
            execution_result,
            similar_result=similar_result,
            similar_review=similar_review,
        )
        print(f"Wrote JSON report: {args.json_report}")

    if execution_result is not None and execution_result.error_rows > 0:
        return 2
    if similar_result is not None and similar_result.errors > 0:
        return 1
    return 0 if result.errors == 0 else 1
