"""Base utilities for Tauri bridge modules."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def emit(payload: dict) -> None:
    """Write JSON payload to stdout."""
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def fail(message: str, exit_code: int = 1) -> int:
    """Write error JSON to stderr and return exit code."""
    print(json.dumps({"error": message}), file=sys.stderr)
    return exit_code


def get_app_dir() -> Path:
    """Get the media-manager application data directory."""
    return Path(os.environ.get("MEDIA_MANAGER_HOME", Path.home() / ".media-manager")).resolve()


def validate_app_path(path: Path) -> Path:
    """Ensure a path resolves inside the app directory. Raises ValueError if not."""
    resolved = path.resolve()
    app_dir = get_app_dir()
    try:
        resolved.relative_to(app_dir)
    except ValueError:
        raise ValueError(f"Path {resolved} is outside app directory {app_dir}")
    return resolved

