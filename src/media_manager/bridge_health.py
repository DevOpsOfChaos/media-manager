"""File health check bridge for the Tauri desktop app.

Reads health check options JSON from stdin.
Runs file health checks on given paths or directories.
Output: health report JSON on stdout. Errors: JSON on stderr.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from media_manager.bridge_base import emit as _emit, fail as _fail
from media_manager.core.file_health import check_file_health, scan_directory_health

logger = logging.getLogger(__name__)


def cmd_check_file() -> int:
    """Check health of a single file. Expects {"path": "..."} on stdin."""
    raw = sys.stdin.read()
    if not raw.strip():
        return _fail("Empty stdin. Expected JSON with 'path' field.")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    path = Path(payload.get("path", ""))
    if not path.exists():
        return _fail(f"File not found: {path}")

    try:
        result = check_file_health(path)
        _emit(result)
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        logger.error("Health check failed: %s", exc)
        return _fail(f"Health check failed: {exc}")


def cmd_scan_directory() -> int:
    """Scan a directory for file health issues. Expects {"source_dir": "...", "max_files": 1000} on stdin."""
    raw = sys.stdin.read()
    if not raw.strip():
        return _fail("Empty stdin. Expected JSON with 'source_dir' field.")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    source_dir = Path(payload.get("source_dir", ""))
    if not source_dir.is_dir():
        return _fail(f"Source directory not found: {source_dir}")

    max_files = int(payload.get("max_files", 1000))

    try:
        result = scan_directory_health(source_dir, max_files=max_files)
        _emit(result)
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        logger.error("Directory health scan failed: %s", exc)
        return _fail(f"Directory health scan failed: {exc}")


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        prog="media_manager.bridge_health",
        description="File health check bridge for Tauri desktop app.",
    )


def main(argv: list[str] | None = None) -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "scan-directory":
        return cmd_scan_directory()
    return cmd_check_file()


if __name__ == "__main__":
    raise SystemExit(main())
