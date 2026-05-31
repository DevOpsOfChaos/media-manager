"""Smart album suggestions bridge for the Tauri desktop app.

Reads file metadata JSON from stdin.
Analyzes metadata patterns to suggest album groupings.
Output: suggestions array JSON on stdout. Errors: JSON on stderr.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys

from media_manager.bridge_base import emit as _emit, fail as _fail
from media_manager.core.smart_albums import suggest_albums

logger = logging.getLogger(__name__)


def cmd_suggest() -> int:
    """Suggest smart albums from stdin file metadata."""
    raw = sys.stdin.read()
    if not raw.strip():
        return _fail("Empty stdin. Expected JSON with 'files_meta' field.")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    files_meta = payload.get("files_meta", [])
    if not isinstance(files_meta, list):
        return _fail("'files_meta' must be an array of file metadata objects.")

    try:
        suggestions = suggest_albums(files_meta)
        _emit({"suggestions": suggestions})
        return 0
    except (ValueError, TypeError, RuntimeError) as exc:
        logger.error("Smart album suggestions failed: %s", exc)
        return _fail(f"Smart album suggestions failed: {exc}")


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        prog="media_manager.bridge_smart_albums",
        description="Smart album suggestions bridge for Tauri desktop app.",
    )


def main(argv: list[str] | None = None) -> int:
    return cmd_suggest()


if __name__ == "__main__":
    raise SystemExit(main())
