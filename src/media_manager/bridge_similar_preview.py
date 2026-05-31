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
import logging
import sys
from pathlib import Path

from media_manager.bridge_base import emit as _emit, fail as _fail
from media_manager.constants import MAX_SIMILAR_IMAGES, MAX_SIMILAR_PAIRS

logger = logging.getLogger(__name__)


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


def _progress_to_stderr(message: str) -> None:
    """Write progress message to stderr as structured JSON."""
    print(json.dumps({"kind": "progress", "phase": "similar_scan", "message": message}), file=sys.stderr)
    sys.stderr.flush()


def cmd_preview() -> int:
    """Scan similar images from stdin JSON config, emit similarity groups."""
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

    max_images = payload.get("max_images", MAX_SIMILAR_IMAGES)
    if not isinstance(max_images, int) or max_images < 1:
        max_images = MAX_SIMILAR_IMAGES

    # Guardrail: count image files before scanning
    from media_manager.sorter import stream_media_files
    from media_manager.media_formats import list_supported_similar_image_extensions
    supported = list_supported_similar_image_extensions()
    source_paths = [Path(p) for p in source_dirs_raw]
    image_count = sum(1 for _ in stream_media_files(source_paths, media_extensions=supported))
    # Estimate pair count: n*(n-1)/2
    estimated_pairs = image_count * (image_count - 1) // 2 if image_count > 1 else 0

    max_pairs = payload.get("max_pairs", MAX_SIMILAR_PAIRS)
    if not isinstance(max_pairs, int) or max_pairs < 1:
        max_pairs = MAX_SIMILAR_PAIRS

    if image_count > max_images or estimated_pairs > max_pairs:
        blocked_reasons = []
        if image_count > max_images:
            blocked_reasons.append(
                f"Too many image files ({image_count}). Maximum is {max_images}."
            )
        if estimated_pairs > max_pairs:
            blocked_reasons.append(
                f"Estimated {estimated_pairs:,} image pair comparisons would exceed the limit ({max_pairs:,})."
            )
        reason = " ".join(blocked_reasons)
        reason += " Narrow the source directory, increase max_images, or increase max_pairs."
        _emit({
            "kind": "preview",
            "scanned_files": 0,
            "image_files": 0,
            "hashed_files": 0,
            "candidate_pairs_checked": 0,
            "exact_hash_pairs": 0,
            "similar_pairs": 0,
            "similar_groups": [],
            "errors": 0,
            "decode_errors": 0,
            "skipped_filtered_files": 0,
            "guardrail": {
                "blocked": True,
                "reason": reason,
                "image_count": image_count,
                "max_images": max_images,
                "estimated_pairs": estimated_pairs,
                "max_pairs": max_pairs,
            },
        })
        return 0

    hash_sizes = payload.get("hash_sizes", [payload.get("hash_size", 8)])
    if not isinstance(hash_sizes, list) or len(hash_sizes) == 0:
        hash_sizes = [8]

    from media_manager.similar_images import SimilarImageScanConfig, scan_similar_images

    config = SimilarImageScanConfig(
        source_dirs=source_paths,
        hash_size=payload.get("hash_size", 8),
        hash_sizes=tuple(hash_sizes),
        max_distance=payload.get("max_distance", 6),
        include_patterns=tuple(payload.get("include_patterns", ())),
        exclude_patterns=tuple(payload.get("exclude_patterns", ())),
    )

    try:
        logger.info("Similar image scan: %d source dirs, %d image files", len(config.source_dirs), image_count)
        result = scan_similar_images(config, progress_callback=_progress_to_stderr)
    except (OSError, ValueError, RuntimeError, TypeError, ImportError) as exc:
        logger.error("Similar image scan failed: %s", exc)
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
    logger.info("Similar image scan: complete (%d groups)", len(result.similar_groups))
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
