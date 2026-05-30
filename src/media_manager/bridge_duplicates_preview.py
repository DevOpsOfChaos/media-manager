"""Duplicates preview bridge for the Tauri desktop app.

Called by the Rust backend via subprocess:
    python -m media_manager.bridge_duplicates_preview

Reads DuplicateScanConfig JSON from stdin.
Output: scan result JSON on stdout. Errors: JSON on stderr.

This bridge ONLY calls scan_exact_duplicates() — it never deletes,
moves, or modifies files. The destructive apply path is not imported.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from media_manager.duplicates import (
    DuplicateScanConfig,
    scan_exact_duplicates,
)

from media_manager.bridge_base import emit as _emit, fail as _fail

logger = logging.getLogger(__name__)


def _progress_to_stderr(message: str) -> None:
    """Write progress message as JSON to stderr for the Rust bridge to forward."""
    print(json.dumps({"progress": message}), file=sys.stderr, flush=True)


def _serialize_group(group) -> dict:
    return {
        "files": [str(p) for p in group.files],
        "file_size": group.file_size,
        "sample_digest": group.sample_digest,
        "full_digest": group.full_digest,
        "same_name": group.same_name,
        "same_suffix": group.same_suffix,
        "extension_summary": group.extension_summary,
        "media_kind_summary": group.media_kind_summary,
    }


def cmd_preview() -> int:
    """Scan exact duplicates from stdin JSON config, emit preview result."""
    raw = sys.stdin.read()
    if not raw.strip():
        return _fail("Empty stdin. Expected JSON DuplicateScanConfig.")

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON input: {exc}")

    source_dirs_raw = payload.get("source_dirs", [])
    if not source_dirs_raw:
        return _fail("source_dirs is required and must be non-empty.")

    config = DuplicateScanConfig(
        source_dirs=[Path(p) for p in source_dirs_raw],
        include_patterns=tuple(payload.get("include_patterns", ())),
        exclude_patterns=tuple(payload.get("exclude_patterns", ())),
    )

    try:
        logger.info("Starting duplicate scan preview: %d source dirs", len(config.source_dirs))
        result = scan_exact_duplicates(config, progress_callback=_progress_to_stderr)
    except Exception as exc:
        logger.exception("Duplicate scan preview failed")
        return _fail(f"Duplicate scan failed: {exc}")

    output: dict = {
        "kind": "preview",
        "scanned_files": result.scanned_files,
        "size_candidate_groups": result.size_candidate_groups,
        "size_candidate_files": result.size_candidate_files,
        "sampled_files": result.sampled_files,
        "hashed_files": result.hashed_files,
        "exact_groups": [_serialize_group(g) for g in result.exact_groups],
        "exact_duplicate_files": result.exact_duplicate_files,
        "exact_duplicates": result.exact_duplicates,
        "errors": result.errors,
        "skipped_filtered_files": result.skipped_filtered_files,
        "extension_summary": result.extension_summary,
        "media_kind_summary": result.media_kind_summary,
    }
    _emit(output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media_manager.bridge_duplicates_preview",
        description="Duplicates preview bridge for Tauri desktop app (read-only scan, never modifies files).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    return cmd_preview()


if __name__ == "__main__":
    raise SystemExit(main())
