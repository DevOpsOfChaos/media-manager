"""Runtime diagnostics bridge for the Tauri desktop app.

Called by the Rust backend via subprocess:
    python -m media_manager.bridge_diagnostics

Output: JSON on stdout. Errors: JSON on stderr.
Reports Python version, import health, and settings path status.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def _emit(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _fail(message: str) -> int:
    print(json.dumps({"error": message}), file=sys.stderr)
    return 1


def _check_import(module_name: str) -> dict:
    try:
        __import__(module_name)
        return {"ok": True}
    except ImportError as exc:
        return {"ok": False, "error": str(exc)}


def cmd_diagnostics() -> int:
    py_version = sys.version

    mm_import = _check_import("media_manager")
    bs_import = _check_import("media_manager.bridge_settings")

    # Resolve settings path (same logic as bridge_settings)
    from media_manager.bridge_settings import _resolve_settings_path
    settings_path = _resolve_settings_path()

    result = {
        "python_version": py_version,
        "media_manager_import": mm_import,
        "bridge_settings_import": bs_import,
        "settings_path": str(settings_path),
        "settings_file_exists": settings_path.is_file(),
    }
    _emit(result)
    return 0


def main(argv: list[str] | None = None) -> int:
    return cmd_diagnostics()


if __name__ == "__main__":
    raise SystemExit(main())
