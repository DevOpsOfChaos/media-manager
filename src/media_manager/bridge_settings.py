"""Settings bridge for the Tauri desktop app.

Called by the Rust backend via subprocess:
    python -m media_manager.bridge_settings read
    python -m media_manager.bridge_settings write   (reads JSON from stdin)
    python -m media_manager.bridge_settings reset

Output: JSON on stdout. Errors: JSON on stderr.

Settings file path:
    Default: ~/.media-manager/gui-settings.json
    Override: --settings-path CLI argument
    Override: MEDIA_MANAGER_SETTINGS_PATH env variable
    Precedence: CLI arg > env var > default
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from media_manager.core.gui_settings_model import (
    default_gui_settings,
    load_gui_settings,
    normalize_gui_settings,
    write_gui_settings,
)

DEFAULT_SETTINGS_PATH = Path.home() / ".media-manager" / "gui-settings.json"


def _resolve_settings_path(cli_path: str | None = None) -> Path:
    """Resolve the settings file path.

    Precedence: CLI argument > MEDIA_MANAGER_SETTINGS_PATH env > default.
    """
    if cli_path:
        return Path(cli_path)
    env_path = os.environ.get("MEDIA_MANAGER_SETTINGS_PATH")
    if env_path:
        return Path(env_path)
    return DEFAULT_SETTINGS_PATH


def _emit(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _fail(message: str, exit_code: int = 1) -> int:
    print(json.dumps({"error": message}), file=sys.stderr)
    return exit_code


def cmd_read(settings_path: Path) -> int:
    try:
        settings = load_gui_settings(settings_path)
    except OSError as exc:
        return _fail(f"Cannot read settings file {settings_path}: {exc}")
    _emit(dict(settings))
    return 0


def cmd_write(settings_path: Path) -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON input: {exc}")
    if not isinstance(payload, dict):
        return _fail("Expected a JSON object")
    normalized = normalize_gui_settings(payload)
    try:
        write_gui_settings(settings_path, normalized)
    except OSError as exc:
        return _fail(f"Cannot write settings file {settings_path}: {exc}")
    _emit(dict(normalized))
    return 0


def cmd_reset(settings_path: Path) -> int:
    defaults = default_gui_settings()
    try:
        write_gui_settings(settings_path, defaults)
    except OSError as exc:
        return _fail(f"Cannot write settings file {settings_path}: {exc}")
    _emit(dict(defaults))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media_manager.bridge_settings",
        description="Settings bridge for Tauri desktop app.",
    )
    parser.add_argument(
        "action",
        choices=["read", "write", "reset"],
        help="Operation to perform.",
    )
    parser.add_argument(
        "--settings-path",
        dest="settings_path",
        default=None,
        help="Override the settings JSON file path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    settings_path = _resolve_settings_path(args.settings_path)

    if args.action == "read":
        return cmd_read(settings_path)
    if args.action == "write":
        return cmd_write(settings_path)
    if args.action == "reset":
        return cmd_reset(settings_path)

    return _fail(f"Unknown action: {args.action}", exit_code=2)


if __name__ == "__main__":
    raise SystemExit(main())
