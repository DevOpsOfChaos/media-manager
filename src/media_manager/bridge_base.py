"""Base utilities for Tauri bridge modules."""

from __future__ import annotations

import json
import sys


def emit(payload: dict) -> None:
    """Write JSON payload to stdout."""
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def fail(message: str, exit_code: int = 1) -> int:
    """Write error JSON to stderr and return exit code."""
    print(json.dumps({"error": message}), file=sys.stderr)
    return exit_code
