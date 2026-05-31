"""Background scan bridge -- runs on startup to check for changes."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from media_manager.bridge_base import emit as _emit, fail as _fail, get_app_dir
from media_manager.core.incremental_scan import scan_incremental

logger = logging.getLogger(__name__)


def cmd_check() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return _fail("Empty stdin. Expected JSON payload with source_dirs.")

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        return _fail(f"Invalid JSON: {e}")

    source_dirs = [Path(p) for p in payload.get("source_dirs", []) if p]
    if not source_dirs:
        return _emit({"status": "no_sources", "message": "No source directories configured."})

    state_path = get_app_dir() / "cache" / "incremental_scan_state.json"

    try:
        result = scan_incremental(source_dirs, state_path)
        result["status"] = "ok"
        _emit(result)
    except Exception as e:
        return _fail(f"Scan failed: {e}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media_manager.bridge_background",
        description="Background scan bridge for Tauri desktop app.",
    )
    parser.add_argument(
        "action",
        choices=["check"],
        help="Operation to perform.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if args.action == "check":
        return cmd_check()

    return _fail(f"Unknown action: {args.action}", exit_code=2)


if __name__ == "__main__":
    raise SystemExit(main())
