"""File operation bridges for the Tauri desktop app — open, delete, rename, reveal."""

from __future__ import annotations

import argparse as _ap
import json
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

from media_manager.bridge_base import emit as _emit, fail as _fail, read_stdin_json
from media_manager.core.platform_utils import open_file as _open_file, reveal_in_explorer as _reveal_in_explorer

logger = logging.getLogger(__name__)


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
        logger.info("File open: %s", path)
        _open_file(path)
        _emit({"status": "opened", "path": str(path)})
        return 0
    except OSError as exc:
        logger.error("File open failed: %s: %s", path, exc)
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
        logger.info("File reveal: %s", path)
        _reveal_in_explorer(path)
        _emit({"status": "revealed", "path": str(path)})
        return 0
    except OSError as exc:
        logger.error("File reveal failed: %s: %s", path, exc)
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
        logger.info("File delete: %s", path)
        import send2trash
        send2trash.send2trash(str(path))
        _emit({"status": "deleted", "path": str(path)})
        return 0
    except ImportError:
        try:
            if sys.platform == "win32":
                from send2trash import send2trash
                send2trash(str(path))
            else:
                subprocess.run(["gio", "trash", "--", str(path)], check=False)
            _emit({"status": "deleted", "path": str(path)})
            return 0
        except (OSError, subprocess.SubprocessError, RuntimeError) as exc:
            logger.error("File delete fallback failed: %s: %s", path, exc)
            return _fail(f"Could not delete file: {exc}")
        except (ImportError, OSError, ValueError, RuntimeError) as exc:
            logger.error("File delete unexpected error: %s: %s", path, exc)
            return _fail(f"Could not delete file: {exc}")
    except (OSError, RuntimeError) as exc:
        logger.error("File delete failed: %s: %s", path, exc)
        return _fail(f"Could not delete file: {exc}")
    except (ImportError, ValueError) as exc:
        logger.error("File delete unexpected error: %s: %s", path, exc)
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
        logger.info("File rename: %s -> %s", path, new_name)
        path.rename(new_path)
        _emit({"status": "renamed", "old_path": str(path), "new_path": str(new_path), "new_name": new_name})
        return 0
    except OSError as exc:
        logger.error("File rename failed: %s -> %s: %s", path, new_name, exc)
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
        logger.info("File export: %s -> %s", source, target)
        img = Image.open(source)
        ratio = width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((width, new_height), Image.LANCZOS)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(target, "JPEG", quality=quality)
        _emit({"status": "exported", "source": str(source), "target": str(target), "width": width, "height": new_height})
        return 0
    except ImportError:
        return _fail("Pillow (PIL) is required for image export. Install with: pip install Pillow")
    except (OSError, ValueError, RuntimeError) as exc:
        logger.error("File export failed: %s: %s", source, exc)
        return _fail(f"Export failed: {exc}")
    except ImportError as exc:
        logger.error("File export unexpected error: %s: %s", source, exc)
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

    _emit({
        "status": "ok",
        "total_checked": len(file_paths),
        "missing_count": len(missing),
        "size_changed_count": len(size_changed),
        "missing": missing,
        "size_changed": size_changed,
        "healthy": len(missing) == 0 and len(size_changed) == 0,
    })
    return 0


def cmd_contact_sheet() -> int:
    """Generate a contact sheet PDF from a list of image paths."""
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    image_paths = payload.get("paths", [])
    output_path = payload.get("output", "")
    title = payload.get("title", "Contact Sheet")
    cols = int(payload.get("cols", 4))
    thumb_size = int(payload.get("thumb_size", 200))

    if not image_paths:
        return _fail("paths list is required")
    if not output_path:
        return _fail("output path is required")

    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return _fail("Pillow (PIL) is required. Install with: pip install Pillow")

    rows = (len(image_paths) + cols - 1) // cols
    margin = 20
    spacing = 10
    label_height = 24

    canvas_w = cols * thumb_size + (cols + 1) * spacing + 2 * margin
    canvas_h = rows * (thumb_size + label_height) + (rows + 1) * spacing + 2 * margin + 40

    canvas = Image.new("RGB", (canvas_w, canvas_h), "white")
    draw = ImageDraw.Draw(canvas)

    try:
        font_title = ImageFont.truetype("arial.ttf", 18)
    except OSError:
        font_title = ImageFont.load_default()
    try:
        font_label = ImageFont.truetype("arial.ttf", 11)
    except OSError:
        font_label = ImageFont.load_default()

    draw.text((margin, margin), title, fill="black", font=font_title)

    for idx, img_path_str in enumerate(image_paths):
        row = idx // cols
        col = idx % cols

        x = margin + col * (thumb_size + spacing)
        y = margin + 40 + row * (thumb_size + label_height + spacing)

        try:
            img = Image.open(img_path_str)
            img.thumbnail((thumb_size, thumb_size), Image.LANCZOS)
            ox = x + (thumb_size - img.width) // 2
            oy = y + (thumb_size - img.height) // 2
            canvas.paste(img, (ox, oy))
        except (OSError, ValueError, RuntimeError):
            draw.rectangle([x, y, x + thumb_size, y + thumb_size], outline="gray")
            draw.text((x + 5, y + thumb_size // 2 - 10), "Error", fill="red", font=font_label)

        name = Path(img_path_str).name
        if len(name) > 20:
            name = name[:17] + "..."
        draw.text((x, y + thumb_size + 2), name, fill="black", font=font_label)

    canvas.save(output_path, "PDF", resolution=150)
    _emit({
        "status": "created",
        "output": output_path,
        "images": len(image_paths),
        "cols": cols,
        "rows": rows,
    })
    return 0


def cmd_web_gallery() -> int:
    """Generate a simple static HTML photo gallery."""
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    image_paths = payload.get("paths", [])
    output_dir = payload.get("output_dir", "")
    title = payload.get("title", "Photo Gallery")
    thumb_size = int(payload.get("thumb_size", 300))

    if not image_paths:
        return _fail("paths list is required")
    if not output_dir:
        return _fail("output_dir is required")

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    thumbs_dir = out / "thumbs"
    thumbs_dir.mkdir(exist_ok=True)

    try:
        from PIL import Image
    except ImportError:
        return _fail("Pillow required")

    items_html = []
    for idx, img_path_str in enumerate(image_paths):
        src = Path(img_path_str)
        if not src.is_file():
            continue
        try:
            img = Image.open(src)
            thumb_name = f"thumb_{idx:04d}.jpg"
            thumb_path = thumbs_dir / thumb_name
            img.thumbnail((thumb_size, thumb_size), Image.LANCZOS)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(thumb_path, "JPEG", quality=80)

            items_html.append(f'''<div class="item">
  <a href="{src.as_uri()}" target="_blank">
    <img src="thumbs/{thumb_name}" alt="{src.name}" loading="lazy" />
  </a>
  <p>{src.name}</p>
</div>''')
        except (OSError, ValueError, RuntimeError):
            continue

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; background: #111; color: #eee; margin: 0; padding: 20px; }}
    h1 {{ text-align: center; margin-bottom: 20px; }}
    .gallery {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 12px; max-width: 1400px; margin: 0 auto; }}
    .item {{ background: #1a1a1a; border-radius: 8px; overflow: hidden; transition: transform 0.2s; }}
    .item:hover {{ transform: scale(1.02); }}
    .item img {{ width: 100%; height: 200px; object-fit: cover; display: block; }}
    .item p {{ padding: 8px 12px; font-size: 12px; color: #999; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <div class="gallery">
    {''.join(items_html)}
  </div>
  <p style="text-align:center;color:#666;margin-top:30px">Generated by Media Manager · {len(items_html)} photos</p>
</body>
</html>'''

    index_path = out / "index.html"
    index_path.write_text(html, encoding="utf-8")

    _emit({
        "status": "created",
        "output_dir": str(out),
        "index": str(index_path),
        "images": len(items_html),
    })


def cmd_backup() -> int:
    """Create a ZIP backup of the media-manager data directory."""

    import zipfile
    import datetime as _dt

    app_dir = Path(os.environ.get("MEDIA_MANAGER_HOME", Path.home() / ".media-manager"))
    if not app_dir.exists():
        return _fail(f"App directory not found: {app_dir}")

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
        _emit({
            "status": "backed_up",
            "path": str(backup_path),
            "size_mb": size_mb,
            "timestamp": timestamp,
        })
        logger.info("Backup complete: %s (%.1f MB)", backup_path, size_mb)
        return 0
    except (OSError, ValueError, RuntimeError, ImportError) as exc:
        logger.error("Backup failed: %s", exc)
        return _fail(f"Backup failed: {exc}")


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
        logger.info("EXIF read: %s", path)
        meta, success, error_type, error_msg = read_exiftool_metadata(path)
        if not success or meta is None:
            return _fail(f"Could not read EXIF: {error_msg or error_type or 'unknown error'}")

        _emit({
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
        return 0
    except (OSError, RuntimeError, ValueError, ImportError) as exc:
        logger.error("EXIF read failed: %s: %s", path, exc)
        return _fail(f"Could not read EXIF: {exc}")


def cmd_watermark() -> int:
    """Add a text watermark to an image."""
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    source = Path(payload.get("source", ""))
    target = Path(payload.get("target", ""))
    text = payload.get("text", "© Media Manager")
    position = payload.get("position", "bottom-right")
    opacity = int(payload.get("opacity", 50))
    font_size = int(payload.get("font_size", 36))

    if not source.is_file():
        return _fail(f"Source not found: {source}")
    if not target.parent.exists():
        target.parent.mkdir(parents=True, exist_ok=True)

    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.open(source).convert("RGBA")

        watermark = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)

        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except OSError:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        margin = 20

        pos_map = {
            "top-left": (margin, margin),
            "top-right": (img.width - tw - margin, margin),
            "bottom-left": (margin, img.height - th - margin),
            "bottom-right": (img.width - tw - margin, img.height - th - margin),
            "center": ((img.width - tw) // 2, (img.height - th) // 2),
        }
        x, y = pos_map.get(position, (margin, img.height - th - margin))

        fill = (255, 255, 255, int(255 * opacity / 100))
        draw.text((x, y), text, font=font, fill=fill)

        result = Image.alpha_composite(img, watermark)
        if target.suffix.lower() == ".png":
            result.save(target, "PNG")
        else:
            result = result.convert("RGB")
            result.save(target, "JPEG", quality=90)

        _emit({"status": "watermarked", "source": str(source), "target": str(target)})
        return 0
    except ImportError:
        return _fail("Pillow required")
    except (OSError, ValueError, RuntimeError, ImportError) as exc:
        logger.error("Watermark failed: %s", exc)
        return _fail(f"Watermark failed: {exc}")


def cmd_batch_delete() -> int:
    """Delete multiple files to trash."""
    payload = read_stdin_json()
    paths = payload.get("paths", [])

    results = []
    for path in paths[:100]:
        try:
            import send2trash
            send2trash.send2trash(str(path))
            results.append({"path": path, "status": "deleted"})
        except Exception as e:
            results.append({"path": path, "status": "error", "error": str(e)})

    _emit({"results": results, "total": len(paths), "deleted": sum(1 for r in results if r["status"] == "deleted")})
    return 0


def cmd_batch_copy() -> int:
    """Copy multiple files to a target directory."""
    payload = read_stdin_json()
    paths = payload.get("paths", [])
    target_dir = Path(payload["target_dir"])

    target_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for path in paths[:100]:
        try:
            shutil.copy2(path, target_dir / Path(path).name)
            results.append({"path": path, "status": "copied"})
        except Exception as e:
            results.append({"path": path, "status": "error", "error": str(e)})

    _emit({"results": results})
    return 0


def cmd_thumbnail() -> int:
    """Generate a thumbnail for a file."""
    payload = read_stdin_json()
    path = Path(payload["path"])
    size = payload.get("size", 256)

    try:
        from PIL import Image
        img = Image.open(path)
        img.thumbnail((size, size), Image.LANCZOS)

        import io, base64
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=70)
        b64 = base64.b64encode(buf.getvalue()).decode()

        _emit({
            "path": str(path),
            "thumbnail": f"data:image/jpeg;base64,{b64}",
            "width": img.width,
            "height": img.height,
        })
    except Exception as e:
        return _fail(f"Thumbnail failed: {e}")
    return 0


def cmd_thumbnails_batch() -> int:
    """Generate thumbnails for multiple files."""
    payload = read_stdin_json()
    paths = payload.get("paths", [])[:50]

    thumbnails = []
    for path in paths:
        try:
            from PIL import Image
            img = Image.open(path)
            img.thumbnail((128, 128), Image.LANCZOS)
            import io, base64
            buf = io.BytesIO()
            img.save(buf, "JPEG", quality=50)
            b64 = base64.b64encode(buf.getvalue()).decode()
            thumbnails.append(f"data:image/jpeg;base64,{b64}")
        except Exception:
            thumbnails.append("")

    _emit({"thumbnails": thumbnails})
    return 0


def cmd_watch_events() -> int:
    """Watch a directory for file changes."""
    payload = read_stdin_json()
    watch_dir = Path(payload["watch_dir"])

    known_files = {}
    for f in watch_dir.rglob("*"):
        if f.is_file():
            known_files[str(f)] = f.stat().st_mtime

    events = {"added": [], "modified": [], "deleted": []}

    current_files = {}
    for f in watch_dir.rglob("*"):
        if f.is_file():
            current_files[str(f)] = f.stat().st_mtime

    for path in current_files:
        if path not in known_files:
            events["added"].append(path)
        elif current_files[path] != known_files[path]:
            events["modified"].append(path)

    for path in known_files:
        if path not in current_files:
            events["deleted"].append(path)

    _emit({"events": events, "total_events": sum(len(v) for v in events.values())})
    return 0


_ACTIONS = {
    "open": cmd_open,
    "reveal": cmd_reveal,
    "delete": cmd_delete,
    "rename": cmd_rename,
    "exif": cmd_exif,
    "export": cmd_export,
    "integrity": cmd_integrity,
    "backup": cmd_backup,
    "contact_sheet": cmd_contact_sheet,
    "web_gallery": cmd_web_gallery,
    "watermark": cmd_watermark,
    "batch_delete": cmd_batch_delete,
    "batch_copy": cmd_batch_copy,
    "thumbnail": cmd_thumbnail,
    "thumbnails_batch": cmd_thumbnails_batch,
    "watch_events": cmd_watch_events,
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
