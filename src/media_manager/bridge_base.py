"""Base utilities for Tauri bridge modules."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def read_stdin_json() -> dict:
    """Read and parse JSON from stdin. Returns empty dict on empty input."""
    import sys as _sys
    raw = _sys.stdin.read()
    if not raw.strip():
        return {}
    return json.loads(raw)


def emit(payload: dict) -> int:
    """Write JSON payload to stdout and return 0."""
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def fail(message: str, exit_code: int = 1) -> int:
    """Write error JSON to stderr and return exit code."""
    print(json.dumps({"error": message}), file=sys.stderr)
    return exit_code


def emit_progress_json(current: int, total: int, stage: str = "", label: str = "") -> None:
    """Write a progress JSON line to stderr for the Rust host to forward."""
    elapsed = 0.0
    pct = round(current / max(total, 1) * 100, 1)
    eta = 0.0
    payload = {
        "kind": "progress",
        "current": current,
        "total": total,
        "percent": pct,
        "stage": stage,
        "label": label,
        "eta_seconds": round(eta, 1),
        "elapsed_seconds": round(elapsed, 1),
    }
    print(json.dumps(payload, ensure_ascii=False), file=sys.stderr, flush=True)


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

