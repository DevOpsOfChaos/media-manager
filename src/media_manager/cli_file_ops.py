"""CLI for file operations — open, reveal, delete, rename, exif, backup, and more."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from media_manager.core.platform_utils import open_file as _open_file, reveal_in_explorer as _reveal_in_explorer


def _emit_json(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _error_json(message: str) -> dict:
    return {"status": "error", "message": message}


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

def cmd_open(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.is_file():
        payload = _error_json(f"File not found: {path}")
        if args.json:
            _emit_json(payload)
        else:
            print(f"Error: File not found: {path}", file=sys.stderr)
        return 1

    try:
        _open_file(path)
        payload = {"status": "opened", "path": str(path)}
    except OSError as exc:
        payload = _error_json(f"Could not open file: {exc}")
        if args.json:
            _emit_json(payload)
        else:
            print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        _emit_json(payload)
    else:
        print(f"Opened: {path}")
    return 0


def cmd_reveal(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.exists():
        payload = _error_json(f"Path not found: {path}")
        if args.json:
            _emit_json(payload)
        else:
            print(f"Error: Path not found: {path}", file=sys.stderr)
        return 1

    try:
        _reveal_in_explorer(path)
        payload = {"status": "revealed", "path": str(path)}
    except OSError as exc:
        payload = _error_json(f"Could not reveal file: {exc}")
        if args.json:
            _emit_json(payload)
        else:
            print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        _emit_json(payload)
    else:
        print(f"Revealed: {path}")
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.is_file():
        payload = _error_json(f"File not found: {path}")
        if args.json:
            _emit_json(payload)
        else:
            print(f"Error: File not found: {path}", file=sys.stderr)
        return 1

    try:
        import send2trash
        send2trash.send2trash(str(path))
        payload = {"status": "deleted", "path": str(path)}
    except ImportError:
        payload = _error_json("send2trash not installed. Run: pip install send2trash")
        if args.json:
            _emit_json(payload)
        else:
            print("Error: send2trash not installed.", file=sys.stderr)
        return 1
    except Exception as exc:
        payload = _error_json(f"Could not delete file: {exc}")
        if args.json:
            _emit_json(payload)
        else:
            print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        _emit_json(payload)
    else:
        print(f"Deleted: {path}")
    return 0


def cmd_backup(args: argparse.Namespace) -> int:
    import datetime as _dt
    import zipfile

    app_dir = Path(os.environ.get("MEDIA_MANAGER_HOME", Path.home() / ".media-manager"))
    if not app_dir.exists():
        payload = _error_json(f"App directory not found: {app_dir}")
        if args.json:
            _emit_json(payload)
        else:
            print(f"Error: App directory not found: {app_dir}", file=sys.stderr)
        return 1

    timestamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = app_dir.parent / f"media-manager-backup-{timestamp}.zip"

    try:
        with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in app_dir.rglob("*"):
                if file_path.is_file():
                    if "models" in file_path.parts or "__pycache__" in file_path.parts:
                        continue
                    arcname = file_path.relative_to(app_dir)
                    zf.write(file_path, arcname)

        size_mb = round(backup_path.stat().st_size / (1024 * 1024), 1)
        payload = {
            "status": "backed_up",
            "path": str(backup_path),
            "size_mb": size_mb,
            "timestamp": timestamp,
        }
    except Exception as exc:
        payload = _error_json(f"Backup failed: {exc}")
        if args.json:
            _emit_json(payload)
        else:
            print(f"Error: Backup failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        _emit_json(payload)
    else:
        print(f"Backup created: {backup_path} ({size_mb} MB)")
    return 0


def cmd_exif(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.is_file():
        payload = _error_json(f"File not found: {path}")
        if args.json:
            _emit_json(payload)
        else:
            print(f"Error: File not found: {path}", file=sys.stderr)
        return 1

    try:
        from media_manager.exiftool import read_exiftool_metadata
        meta, success, error_type, error_msg = read_exiftool_metadata(path)
        if not success or meta is None:
            payload = _error_json(f"Could not read EXIF: {error_msg or error_type or 'unknown error'}")
            if args.json:
                _emit_json(payload)
            else:
                print(f"Error: Could not read EXIF: {error_msg or error_type}", file=sys.stderr)
            return 1

        payload = {
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
        }
    except Exception as exc:
        payload = _error_json(f"Could not read EXIF: {exc}")
        if args.json:
            _emit_json(payload)
        else:
            print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        _emit_json(payload)
    else:
        md = payload["metadata"]
        print(f"EXIF for: {path}")
        if md["camera"]:
            print(f"  Camera:        {md['camera']}")
        if md["lens"]:
            print(f"  Lens:          {md['lens']}")
        if md["date_taken"]:
            print(f"  Date taken:    {md['date_taken']}")
        if md["iso"]:
            print(f"  ISO:           {md['iso']}")
        if md["aperture"]:
            print(f"  Aperture:      {md['aperture']}")
        if md["shutter_speed"]:
            print(f"  Shutter speed: {md['shutter_speed']}")
        if md["focal_length"]:
            print(f"  Focal length:  {md['focal_length']}")
        if md["gps_latitude"] and md["gps_longitude"]:
            print(f"  GPS:           {md['gps_latitude']}, {md['gps_longitude']}")
        if md["image_width"] and md["image_height"]:
            print(f"  Resolution:    {md['image_width']}x{md['image_height']} ({md['megapixels']} MP)")
    return 0


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager file-ops",
        description="File operations: open, reveal, delete, exif, backup.",
        epilog=(
            "Examples:\n"
            "  media-manager file-ops open --path photo.jpg\n"
            "  media-manager file-ops reveal --path photo.jpg\n"
            "  media-manager file-ops delete --path photo.jpg\n"
            "  media-manager file-ops exif --path photo.jpg\n"
            "  media-manager file-ops exif --path photo.jpg --json\n"
            "  media-manager file-ops backup\n"
        ),
    )
    subparsers = parser.add_subparsers(dest="action")

    open_p = subparsers.add_parser("open", help="Open a file with the system default application.")
    open_p.add_argument("--path", type=Path, required=True, help="Path to the file.")
    open_p.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    reveal_p = subparsers.add_parser("reveal", help="Reveal a file in the system file explorer.")
    reveal_p.add_argument("--path", type=Path, required=True, help="Path to the file or directory.")
    reveal_p.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    delete_p = subparsers.add_parser("delete", help="Move a file to trash.")
    delete_p.add_argument("--path", type=Path, required=True, help="Path to the file.")
    delete_p.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    exif_p = subparsers.add_parser("exif", help="Read EXIF metadata for a file.")
    exif_p.add_argument("--path", type=Path, required=True, help="Path to the file.")
    exif_p.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    backup_p = subparsers.add_parser("backup", help="Create a ZIP backup of the media-manager data directory.")
    backup_p.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    return parser


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

ACTION_HANDLERS = {
    "open": cmd_open,
    "reveal": cmd_reveal,
    "delete": cmd_delete,
    "exif": cmd_exif,
    "backup": cmd_backup,
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.action is None:
        parser.print_help()
        return 0

    handler = ACTION_HANDLERS.get(args.action)
    if handler is None:
        print(f"Unknown action: {args.action}", file=sys.stderr)
        return 1

    return handler(args)
