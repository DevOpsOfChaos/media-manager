"""Organize preview bridge for the Tauri desktop app.

Called by the Rust backend via subprocess:
    python -m media_manager.bridge_organize_preview

Reads OrganizePlannerOptions JSON from stdin.
Output: preview/dry-run JSON on stdout. Errors: JSON on stderr.

This bridge NEVER modifies files. It calls build_organize_dry_run()
and explicitly marks the result as a preview.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from media_manager.core.job_queue import JobQueue
from media_manager.core.organizer import OrganizePlannerOptions, build_organize_dry_run
from media_manager.core.outcome_report import build_plan_outcome_report
from media_manager.core.review_report import build_review_export

from media_manager.bridge_base import emit as _emit, fail as _fail

logger = logging.getLogger(__name__)


def _serialize_entry(entry) -> dict:
    """Serialize a single OrganizePlanEntry to JSON-safe dict."""
    resolution = entry.resolution
    resolution_dict = None
    if resolution is not None:
        resolution_dict = {
            "path": str(resolution.path),
            "resolved_datetime": resolution.resolved_datetime.isoformat() if resolution.resolved_datetime else None,
            "resolved_value": resolution.resolved_value,
            "source_kind": resolution.source_kind,
            "source_label": resolution.source_label,
            "confidence": resolution.confidence,
            "timezone_status": resolution.timezone_status,
            "reason": resolution.reason,
            "candidates_checked": resolution.candidates_checked,
        }

    entry_dict: dict = {
        "source_path": str(entry.source_path),
        "source_root": str(entry.source_root),
        "relative_source_path": str(entry.scanned_file.relative_path),
        "extension": entry.scanned_file.extension,
        "size_bytes": entry.scanned_file.size_bytes,
        "status": entry.status,
        "reason": entry.reason,
        "operation_mode": entry.operation_mode,
        "target_relative_dir": str(entry.target_relative_dir) if entry.target_relative_dir else None,
        "target_path": str(entry.target_path) if entry.target_path else None,
        "resolution": resolution_dict,
        "group_id": entry.group_id,
        "group_kind": entry.group_kind,
        "associated_file_count": entry.associated_file_count,
        "association_warning_count": entry.association_warning_count,
    }
    return entry_dict


def cmd_preview() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return _fail("Empty stdin. Expected JSON OrganizePlannerOptions.")

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON input: {exc}")

    try:
        source_dirs_raw = payload.get("source_dirs", [])
        if not source_dirs_raw:
            return _fail("source_dirs is required and must be non-empty.")

        target_root_raw = payload.get("target_root", "")
        if not target_root_raw:
            return _fail("target_root is required.")

        queue = JobQueue()
        if queue.has_pending_or_running("organize", {"source_dirs": source_dirs_raw, "target_root": target_root_raw}):
            return _fail("An identical organize job is already pending or running.")

        source_dirs = []
        missing_sources = []
        for p in source_dirs_raw:
            resolved = Path(p).resolve()
            if resolved.exists():
                source_dirs.append(resolved)
            else:
                missing_sources.append(str(p))
        if not source_dirs:
            return _fail(f"None of the source directories exist: {missing_sources}")
        target_root = Path(target_root_raw).resolve()

        logger.info("Starting organize preview: %d source dirs -> %s", len(source_dirs), target_root)

        options = OrganizePlannerOptions(
            source_dirs=tuple(source_dirs),
            target_root=target_root,
            pattern=payload.get("pattern", "{year}/{year_month_day}"),
            recursive=payload.get("recursive", True),
            include_hidden=payload.get("include_hidden", False),
            follow_symlinks=payload.get("follow_symlinks", False),
            operation_mode=payload.get("operation_mode", "copy"),
            include_associated_files=payload.get("include_associated_files", False),
            conflict_policy=payload.get("conflict_policy", "conflict"),
            include_patterns=tuple(payload.get("include_patterns", ())),
            exclude_patterns=tuple(payload.get("exclude_patterns", ())),
            batch_size=payload.get("batch_size", 0),
            date_source=payload.get("date_source", "auto"),
        )
    except (TypeError, ValueError) as exc:
        logger.error("Organize preview: invalid options: %s", exc)
        return _fail(f"Invalid options: {exc}")

    # Build dry-run — this NEVER modifies files
    try:
        dry_run = build_organize_dry_run(options)
    except Exception as exc:
        logger.error("Organize preview: plan build failed: %s", exc)
        return _fail(f"Preview failed: {exc}")

    job = queue.create("organize", {
        "source_dirs": [str(p) for p in source_dirs],
        "target_root": str(target_root),
        "pattern": options.pattern,
    })
    queue.complete(job.job_id, {"planned_count": dry_run.planned_count})

    # Build review candidates
    try:
        review = build_review_export({"organize": dry_run.entries})
        review_candidate_count = review.get("candidate_count", 0) if isinstance(review, dict) else 0
    except Exception:
        review = None
        review_candidate_count = 0

    # Build outcome report
    outcome_report = build_plan_outcome_report(
        command_name="organize_preview",
        conflict_policy=options.conflict_policy,
        planned_count=dry_run.planned_count,
        skipped_count=dry_run.skipped_count,
        conflict_count=dry_run.conflict_count,
        error_count=dry_run.error_count,
        missing_source_count=dry_run.missing_source_count,
        review_candidate_count=review_candidate_count,
        status_summary=dry_run.status_summary,
        reason_summary=dry_run.reason_summary,
    )

    result: dict = {
        "kind": "preview",
        "dry_run": True,
        "options": {
            "source_dirs": [str(p) for p in options.source_dirs],
            "target_root": str(options.target_root),
            "pattern": options.pattern,
            "recursive": options.recursive,
            "include_hidden": options.include_hidden,
            "follow_symlinks": options.follow_symlinks,
            "operation_mode": options.operation_mode,
            "include_associated_files": options.include_associated_files,
            "conflict_policy": options.conflict_policy,
            "include_patterns": list(options.include_patterns),
            "exclude_patterns": list(options.exclude_patterns),
            "batch_size": options.batch_size,
            "date_source": options.date_source,
        },
        "scan_summary": {
            "source_dirs": [str(p) for p in dry_run.scan_summary.source_dirs],
            "missing_sources": [str(p) for p in dry_run.scan_summary.missing_sources],
            "source_count": dry_run.scan_summary.source_count,
            "media_file_count": dry_run.scan_summary.media_file_count,
            "total_size_bytes": dry_run.scan_summary.total_size_bytes,
        },
        "planned_count": dry_run.planned_count,
        "skipped_count": dry_run.skipped_count,
        "conflict_count": dry_run.conflict_count,
        "error_count": dry_run.error_count,
        "missing_source_count": dry_run.missing_source_count,
        "media_file_count": dry_run.media_file_count,
        "media_group_count": dry_run.media_group_count,
        "associated_file_count": dry_run.associated_file_count,
        "association_warning_count": dry_run.association_warning_count,
        "status_summary": dry_run.status_summary,
        "reason_summary": dry_run.reason_summary,
        "resolution_source_summary": dry_run.resolution_source_summary,
        "confidence_summary": dry_run.confidence_summary,
        "group_kind_summary": dry_run.group_kind_summary,
        "outcome_report": outcome_report,
        "entries": [_serialize_entry(e) for e in dry_run.entries],
    }
    _emit(result)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media_manager.bridge_organize_preview",
        description="Organize preview bridge for Tauri desktop app (read-only, never modifies files).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    return cmd_preview()


if __name__ == "__main__":
    raise SystemExit(main())
