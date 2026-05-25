"""File operation bridges for the Tauri desktop app — open, delete, rename, reveal."""

from __future__ import annotations

import argparse as _ap
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def _emit(payload: dict) -> int:
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def _fail(message: str, exit_code: int = 1) -> int:
    print(json.dumps({"error": message}), file=sys.stderr)
    return exit_code


def cmd_open() -> int:
    """Open a file with the system default application."""
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    path = Path(payload.get("path", ""))
    if not path.is_file():
        return _fail(f"File not found: {path}")

    try:
        os.startfile(str(path))
        return _emit({"status": "opened", "path": str(path)})
    except OSError as exc:
        return _fail(f"Could not open file: {exc}")


def cmd_reveal() -> int:
    """Reveal a file in the system file explorer."""
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    path = Path(payload.get("path", ""))
    if not path.exists():
        return _fail(f"Path not found: {path}")

    try:
        if sys.platform == "win32":
            subprocess.run(["explorer", "/select,", str(path)], check=False)
        elif sys.platform == "darwin":
            subprocess.run(["open", "-R", str(path)], check=False)
        else:
            subprocess.run(["xdg-open", str(path.parent)], check=False)
        return _emit({"status": "revealed", "path": str(path)})
    except OSError as exc:
        return _fail(f"Could not reveal file: {exc}")


def cmd_delete() -> int:
    """Move a file to trash (uses send2trash)."""
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    path = Path(payload.get("path", ""))
    if not path.is_file():
        return _fail(f"File not found: {path}")

    try:
        import send2trash
        send2trash.send2trash(str(path))
        return _emit({"status": "deleted", "path": str(path)})
    except ImportError:
        try:
            if sys.platform == "win32":
                import winshell
                from send2trash import send2trash
                send2trash(str(path))
            else:
                subprocess.run(["gio", "trash", str(path)], check=False)
            return _emit({"status": "deleted", "path": str(path)})
        except Exception as exc:
            return _fail(f"Could not delete file: {exc}")
    except Exception as exc:
        return _fail(f"Could not delete file: {exc}")


def cmd_rename() -> int:
    """Rename a file."""
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    path = Path(payload.get("path", ""))
    new_name = payload.get("new_name", "")
    if not path.is_file():
        return _fail(f"File not found: {path}")
    if not new_name:
        return _fail("new_name is required")

    new_path = path.parent / new_name
    if new_path.exists():
        return _fail(f"Target already exists: {new_path}")

    try:
        path.rename(new_path)
        return _emit({"status": "renamed", "old_path": str(path), "new_path": str(new_path), "new_name": new_name})
    except OSError as exc:
        return _fail(f"Could not rename file: {exc}")


_ACTIONS = {
    "open": cmd_open,
    "reveal": cmd_reveal,
    "delete": cmd_delete,
    "rename": cmd_rename,
}


def build_parser() -> _ap.ArgumentParser:
    parser = _ap.ArgumentParser(prog="media_manager.bridge_file_ops")
    parser.add_argument("action", choices=list(_ACTIONS.keys()))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv or sys.argv[1:])
    handler = _ACTIONS.get(args.action)
    if handler is None:
        return _fail(f"Unknown action: {args.action}")
    return handler()


if __name__ == "__main__":
    raise SystemExit(main())
