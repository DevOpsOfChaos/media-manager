"""Auto-tagging bridge for the Tauri desktop app.

Provides single-file and batch tag generation from file metadata (EXIF, GPS, camera).
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from media_manager.bridge_base import emit as _emit, fail as _fail, read_stdin_json
from media_manager.core.auto_tagger import extract_deep_metadata, generate_tags

logger = logging.getLogger(__name__)


def cmd_auto_tag() -> int:
    """Generate automatic tags for a file."""
    payload = read_stdin_json()
    path = Path(payload["path"])

    deep_meta = extract_deep_metadata(path)
    tags = generate_tags(deep_meta, path.name)

    _emit({
        "path": str(path),
        "tags": tags,
        "tag_count": len(tags),
    })
    return 0


def cmd_auto_tag_batch() -> int:
    """Generate tags for multiple files."""
    payload = read_stdin_json()
    paths = payload.get("paths", [])[:200]

    results = []
    for path in paths:
        deep_meta = extract_deep_metadata(Path(path))
        tags = generate_tags(deep_meta, Path(path).name)
        results.append({"path": path, "tags": tags})

    tag_counts: dict[str, int] = {}
    for r in results:
        for tag in r["tags"]:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    _emit({
        "files": results,
        "tag_cloud": dict(sorted(tag_counts.items(), key=lambda x: -x[1])[:50]),
    })
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="media_manager.bridge_autotag")
    parser.add_argument("action", choices=["auto-tag", "auto-tag-batch"])
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv or sys.argv[1:])
    if args.action == "auto-tag":
        return cmd_auto_tag()
    if args.action == "auto-tag-batch":
        return cmd_auto_tag_batch()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
