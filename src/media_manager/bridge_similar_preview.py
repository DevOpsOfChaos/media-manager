"""Similar images preview bridge for the Tauri desktop app.

Called by the Rust backend via subprocess:
    python -m media_manager.bridge_similar_preview

Reads SimilarImageScanConfig JSON from stdin.
Output: scan result JSON on stdout. Errors: JSON on stderr.

This bridge ONLY calls scan_similar_images() — it never deletes,
moves, or modifies files. The destructive apply path is not imported.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from media_manager.similar_images import (
    SimilarImageScanConfig,
    scan_similar_images,
)


def _emit(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _fail(message: str, exit_code: int = 1) -> int:
    print(json.dumps({"error": message}), file=sys.stderr)
    return exit_code


def _serialize_member(member) -> dict:
    return {
        "path": str(member.path),
        "hash_hex": member.hash_hex,
        "distance": member.distance,
        "width": member.width,
        "height": member.height,
    }


def _serialize_group(group) -> dict:
    return {
        "anchor_path": str(group.anchor_path),
        "members": [_serialize_member(m) for m in group.members],
    }


def cmd_preview() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return _fail("Empty stdin. Expected JSON SimilarImageScanConfig.")

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON input: {exc}")

    source_dirs_raw = payload.get("source_dirs", [])
    if not source_dirs_raw:
        return _fail("source_dirs is required and must be non-empty.")

    config = SimilarImageScanConfig(
        source_dirs=[Path(p) for p in source_dirs_raw],
        hash_size=payload.get("hash_size", 8),
        max_distance=payload.get("max_distance", 6),
        include_patterns=tuple(payload.get("include_patterns", ())),
        exclude_patterns=tuple(payload.get("exclude_patterns", ())),
    )

    try:
        result = scan_similar_images(config)
    except Exception as exc:
        return _fail(f"Similar image scan failed: {exc}")

    output: dict = {
        "kind": "preview",
        "scanned_files": result.scanned_files,
        "image_files": result.image_files,
        "hashed_files": result.hashed_files,
        "candidate_pairs_checked": result.candidate_pairs_checked,
        "exact_hash_pairs": result.exact_hash_pairs,
        "similar_pairs": result.similar_pairs,
        "similar_groups": [_serialize_group(g) for g in result.similar_groups],
        "errors": result.errors,
        "decode_errors": result.decode_errors,
        "skipped_filtered_files": result.skipped_filtered_files,
    }
    _emit(output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media_manager.bridge_similar_preview",
        description="Similar images preview bridge (read-only, never modifies files).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    return cmd_preview()


if __name__ == "__main__":
    raise SystemExit(main())
