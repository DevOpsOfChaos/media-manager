"""Check file type by content (magic bytes), ignoring file extension."""

from __future__ import annotations

import argparse as _ap
import sys
from pathlib import Path

from media_manager.bridge_base import emit as _emit, fail as _fail, read_stdin_json
from media_manager.core.magic_bytes import detect_file_type


def cmd_detect() -> int:
    payload = read_stdin_json()
    path = Path(payload["path"])

    result = detect_file_type(path)
    if result:
        result["extension"] = path.suffix.lower()
        # Flag if extension doesn't match content
        ext_to_cat = {
            ".jpg": "photo", ".jpeg": "photo", ".png": "photo", ".mp4": "video",
            ".mov": "video", ".nef": "raw", ".cr2": "raw",
        }
        expected_cat = ext_to_cat.get(path.suffix.lower())
        if expected_cat and expected_cat != result["category"]:
            result["mismatch"] = True
            result["warning"] = (
                f"Extension {path.suffix} suggests {expected_cat} "
                f"but content is {result['category']}"
            )

        _emit(result)
    else:
        _emit({
            "path": str(path),
            "category": "unknown",
            "detected_by": "none",
            "confidence": 0,
        })
    return 0


def cmd_scan_media() -> int:
    """Scan directory and return only real media files (by content)."""
    payload = read_stdin_json()
    source_dir = Path(payload["source_dir"])
    max_files = payload.get("max_files", 1000)

    real_media = []
    fake_media = []
    count = 0

    for f in source_dir.rglob("*"):
        if not f.is_file():
            continue
        if count >= max_files:
            break

        result = detect_file_type(f)
        if result and result["category"] in ("photo", "video", "audio", "raw"):
            real_media.append({
                "path": str(f),
                "name": f.name,
                "type": result["description"],
            })
        else:
            fake_media.append({
                "path": str(f),
                "name": f.name,
                "reason": "Not a media file (content check)",
            })
        count += 1

    _emit({
        "real_media": real_media,
        "fake_media": fake_media,
        "total_scanned": count,
        "real_count": len(real_media),
        "fake_count": len(fake_media),
    })
    return 0


_ACTIONS = {
    "detect": cmd_detect,
    "scan_media": cmd_scan_media,
}


def build_parser() -> _ap.ArgumentParser:
    parser = _ap.ArgumentParser(prog="media_manager.bridge_magic")
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
