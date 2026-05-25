"""Library browser bridge for the Tauri desktop app."""

from __future__ import annotations

import argparse as _ap
import json
import os
import sys
from pathlib import Path


def _emit(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _fail(message: str, exit_code: int = 1) -> int:
    print(json.dumps({"error": message}), file=sys.stderr)
    return exit_code


def cmd_browse() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    root = Path(payload.get("root_dir", ""))
    if not str(root) or not root.exists():
        return _fail("root_dir required and must exist")

    max_depth = payload.get("max_depth", 3)
    extensions = set(
        payload.get("extensions", [])
        or [
            ".jpg", ".jpeg", ".png", ".mp4", ".mov", ".cr2", ".cr3", ".nef",
            ".arw", ".dng", ".tiff", ".bmp", ".gif", ".heic", ".webp",
        ]
    )

    files: list[dict] = []
    for current, dirs, filenames in os.walk(root):
        depth = len(Path(current).relative_to(root).parts)
        if depth > max_depth:
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in sorted(filenames):
            fp = Path(current) / f
            if fp.suffix.lower() in extensions:
                try:
                    size = fp.stat().st_size
                except OSError:
                    size = 0
                files.append({
                    "path": str(fp),
                    "name": f,
                    "relative": str(fp.relative_to(root)),
                    "size": size,
                    "suffix": fp.suffix.lower(),
                })

    _emit({
        "kind": "browse",
        "root": str(root),
        "file_count": len(files),
        "depth": max_depth,
        "files": files[:5000],
    })
    return 0


def build_parser() -> _ap.ArgumentParser:
    parser = _ap.ArgumentParser(prog="media_manager.bridge_library")
    parser.add_argument("action", choices=["browse"])
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv or sys.argv[1:])
    return cmd_browse() if args.action == "browse" else 1


if __name__ == "__main__":
    raise SystemExit(main())
