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


def cmd_export() -> int:
    """Resize and export an image."""
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    source = Path(payload.get("source", ""))
    target = Path(payload.get("target", ""))
    width = int(payload.get("width", 2048))
    quality = int(payload.get("quality", 85))

    if not source.is_file():
        return _fail(f"Source not found: {source}")

    try:
        from PIL import Image
        img = Image.open(source)
        ratio = width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((width, new_height), Image.LANCZOS)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(target, "JPEG", quality=quality)
        return _emit({"status": "exported", "source": str(source), "target": str(target), "width": width, "height": new_height})
    except ImportError:
        return _fail("Pillow (PIL) is required for image export. Install with: pip install Pillow")
    except Exception as exc:
        return _fail(f"Export failed: {exc}")


def cmd_integrity() -> int:
    """Check if files from a previously saved file list still exist."""
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    file_paths = payload.get("paths", [])
    if not file_paths:
        return _fail("paths list is required")

    missing = []
    size_changed = []
    for entry in file_paths:
        p = Path(entry.get("path", ""))
        if not p.exists():
            missing.append({"path": str(p), "expected_size": entry.get("size")})
        elif entry.get("size") is not None:
            try:
                if p.stat().st_size != entry["size"]:
                    size_changed.append({"path": str(p), "expected_size": entry["size"], "actual_size": p.stat().st_size})
            except OSError:
                missing.append({"path": str(p), "expected_size": entry.get("size")})

    return _emit({
        "status": "ok",
        "total_checked": len(file_paths),
        "missing_count": len(missing),
        "size_changed_count": len(size_changed),
        "missing": missing,
        "size_changed": size_changed,
        "healthy": len(missing) == 0 and len(size_changed) == 0,
    })


def cmd_exif() -> int:
    """Read EXIF metadata for a file using ExifTool."""
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    path = Path(payload.get("path", ""))
    if not path.is_file():
        return _fail(f"File not found: {path}")

    try:
        from media_manager.exiftool import read_exiftool_metadata
        meta, success, error_type, error_msg = read_exiftool_metadata(path)
        if not success or meta is None:
            return _fail(f"Could not read EXIF: {error_msg or error_type or 'unknown error'}")

        return _emit({
            "status": "ok",
            "path": str(path),
            "metadata": {
                "camera": str(meta.get("Model", "")) or str(meta.get("CameraModelName", "")) or None,
                "lens": str(meta.get("LensModel", "")) or str(meta.get("LensID", "")) or None,
                "iso": meta.get("ISO"),
                "aperture": str(meta.get("FNumber", "")) or str(meta.get("Aperture", "")) or None,
                "shutter_speed": str(meta.get("ShutterSpeed", "")) or str(meta.get("ExposureTime", "")) or None,
                "focal_length": str(meta.get("FocalLength", "")) or str(meta.get("FocalLength35efl", "")) or None,
                "date_taken": str(meta.get("DateTimeOriginal", "")) or str(meta.get("CreateDate", "")) or None,
                "gps_latitude": str(meta.get("GPSLatitude", "")) or None,
                "gps_longitude": str(meta.get("GPSLongitude", "")) or None,
                "gps_altitude": str(meta.get("GPSAltitude", "")) or None,
                "image_width": meta.get("ImageWidth"),
                "image_height": meta.get("ImageHeight"),
                "megapixels": round(float(str(meta.get("ImageWidth", 0))) * float(str(meta.get("ImageHeight", 0))) / 1_000_000, 1) if meta.get("ImageWidth") and meta.get("ImageHeight") else None,
                "flash": str(meta.get("Flash", "")) or None,
                "orientation": str(meta.get("Orientation", "")) or None,
                "software": str(meta.get("Software", "")) or None,
                "artist": str(meta.get("Artist", "")) or str(meta.get("Creator", "")) or None,
                "copyright": str(meta.get("Copyright", "")) or None,
                "duration": meta.get("Duration"),
            },
        })
    except Exception as exc:
        return _fail(f"Could not read EXIF: {exc}")


_ACTIONS = {
    "open": cmd_open,
    "reveal": cmd_reveal,
    "delete": cmd_delete,
    "rename": cmd_rename,
    "exif": cmd_exif,
    "export": cmd_export,
    "integrity": cmd_integrity,
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
