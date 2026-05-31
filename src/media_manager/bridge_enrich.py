"""Enriched metadata bridge for the Tauri desktop app.

Provides single-file and batch enriched metadata (EXIF, GPS, faces, colors, duplicates).
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import sys
from pathlib import Path

from media_manager.bridge_base import emit as _emit, fail as _fail

logger = logging.getLogger(__name__)


def _read_exif(path: Path) -> tuple[dict, dict | None]:
    """Return (exif_dict, gps_dict_or_None)."""
    try:
        from media_manager.exiftool import read_exiftool_metadata
        meta, success, _err_type, _err_msg = read_exiftool_metadata(path)
    except (ImportError, OSError, ValueError, RuntimeError):
        return {}, None

    if not success or not meta:
        return {}, None

    exif: dict = {}
    camera = meta.get("Model") or meta.get("CameraModelName")
    if camera:
        exif["camera"] = str(camera)
    lens = meta.get("LensModel") or meta.get("LensID")
    if lens:
        exif["lens"] = str(lens)
    iso = meta.get("ISO")
    if iso is not None:
        exif["iso"] = int(float(str(iso)))
    aperture = meta.get("FNumber") or meta.get("Aperture")
    if aperture is not None:
        exif["aperture"] = str(aperture)
    shutter = meta.get("ShutterSpeed") or meta.get("ExposureTime")
    if shutter is not None:
        exif["shutter"] = str(shutter)
    focal = meta.get("FocalLength") or meta.get("FocalLength35efl")
    if focal is not None:
        exif["focal_length"] = str(focal)
    date_taken = meta.get("DateTimeOriginal") or meta.get("CreateDate")
    if date_taken:
        exif["date_taken"] = str(date_taken)
    orientation = meta.get("Orientation")
    if orientation:
        exif["orientation"] = str(orientation)
    software = meta.get("Software")
    if software:
        exif["software"] = str(software)
    w = float(str(meta.get("ImageWidth", 0)))
    h = float(str(meta.get("ImageHeight", 0)))
    if w > 0 and h > 0:
        exif["megapixels"] = round(w * h / 1e6, 1)

    gps = None
    lat = meta.get("GPSLatitude")
    lon = meta.get("GPSLongitude")
    if lat is not None and lon is not None:
        gps = {
            "lat": str(lat),
            "lon": str(lon),
        }
        alt = meta.get("GPSAltitude")
        if alt is not None:
            gps["alt"] = str(alt)

    return exif, gps


def _read_faces(path: Path) -> list[dict]:
    """Look up known faces for a file from the people catalog."""
    try:
        from media_manager.bridge_people import _get_app_dir
        app_dir = _get_app_dir()
        catalog_dirs = list((app_dir / "people").rglob("*.json"))
    except Exception:
        return []
    if not catalog_dirs:
        return []

    faces: list[dict] = []
    for catalog_path in catalog_dirs[:3]:
        try:
            data = json.loads(catalog_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        for person_id, person in data.get("persons", {}).items():
            for emb in person.get("embeddings", []):
                if emb.get("source_path") == str(path) or str(emb.get("source_path")) == str(path):
                    face = {
                        "person_id": person_id,
                        "name": person.get("name") or person_id,
                    }
                    box = emb.get("box")
                    if box and isinstance(box, list) and len(box) == 4:
                        face["box"] = {"x": box[0], "y": box[1], "w": box[2], "h": box[3]}
                    faces.append(face)
    return faces


def _read_colors(path: Path) -> list[str] | None:
    """Extract dominant colors from an image using PIL."""
    suffix = path.suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff", ".tif"}:
        return None
    try:
        from PIL import Image
    except ImportError:
        return None

    try:
        img = Image.open(path).convert("RGB")
        img = img.resize((50, 50))
        pixels = list(img.getdata())
        from collections import Counter
        counter = Counter(pixels)
        top = counter.most_common(5)
        return [f"#{r:02x}{g:02x}{b:02x}" for (r, g, b), _ in top]
    except OSError:
        return None


def _check_duplicates(path: Path) -> bool:
    """Quick size-based duplicate check in the parent directory."""
    try:
        file_size = path.stat().st_size
    except OSError:
        return False
    parent = path.parent
    try:
        for sibling in parent.iterdir():
            if sibling == path:
                continue
            if not sibling.is_file():
                continue
            try:
                if sibling.stat().st_size == file_size:
                    return True
            except OSError:
                continue
    except OSError:
        return False
    return False


def _build_enriched_entry(path: Path, meta: dict | None = None) -> dict:
    """Build a single enriched metadata entry for a file."""
    result: dict = {
        "path": str(path),
        "file": {
            "size": 0,
            "modified": "",
            "extension": path.suffix.lower(),
        },
    }

    try:
        st = path.stat()
        result["file"]["size"] = st.st_size
        result["file"]["modified"] = datetime.datetime.fromtimestamp(st.st_mtime, tz=datetime.timezone.utc).isoformat()
    except OSError:
        pass

    if meta is not None:
        exif, gps = _parse_meta_dict(meta, path)
    else:
        exif, gps = _read_exif(path)

    result["exif"] = exif
    result["gps"] = gps

    result["faces"] = _read_faces(path)
    result["colors"] = _read_colors(path)
    result["has_duplicates"] = _check_duplicates(path)

    return result


def _parse_meta_dict(meta: dict, path: Path) -> tuple[dict, dict | None]:
    """Parse EXIF and GPS from a raw metadata dict (used in batch path)."""
    exif: dict = {}
    camera = meta.get("Model") or meta.get("CameraModelName")
    if camera:
        exif["camera"] = str(camera)
    lens = meta.get("LensModel") or meta.get("LensID")
    if lens:
        exif["lens"] = str(lens)
    iso = meta.get("ISO")
    if iso is not None:
        exif["iso"] = int(float(str(iso)))
    aperture = meta.get("FNumber") or meta.get("Aperture")
    if aperture is not None:
        exif["aperture"] = str(aperture)
    shutter = meta.get("ShutterSpeed") or meta.get("ExposureTime")
    if shutter is not None:
        exif["shutter"] = str(shutter)
    focal = meta.get("FocalLength") or meta.get("FocalLength35efl")
    if focal is not None:
        exif["focal_length"] = str(focal)
    date_taken = meta.get("DateTimeOriginal") or meta.get("CreateDate")
    if date_taken:
        exif["date_taken"] = str(date_taken)
    orientation = meta.get("Orientation")
    if orientation:
        exif["orientation"] = str(orientation)
    software = meta.get("Software")
    if software:
        exif["software"] = str(software)
    w = float(str(meta.get("ImageWidth", 0)))
    h = float(str(meta.get("ImageHeight", 0)))
    if w > 0 and h > 0:
        exif["megapixels"] = round(w * h / 1e6, 1)

    gps = None
    lat = meta.get("GPSLatitude")
    lon = meta.get("GPSLongitude")
    if lat is not None and lon is not None:
        gps = {"lat": str(lat), "lon": str(lon)}
        alt = meta.get("GPSAltitude")
        if alt is not None:
            gps["alt"] = str(alt)

    return exif, gps


# ── Bridge commands ──


def cmd_enrich() -> int:
    """Return all enriched metadata for a single file."""
    raw = sys.stdin.read()
    if not raw.strip():
        return _fail("Empty stdin")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    path = Path(payload.get("path", ""))
    if not path.is_file():
        return _fail(f"File not found: {path}")

    result = _build_enriched_entry(path)
    _emit(result)
    return 0


def cmd_enrich_batch() -> int:
    """Return enriched metadata for a batch of files."""
    raw = sys.stdin.read()
    if not raw.strip():
        return _fail("Empty stdin")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    paths_raw = payload.get("paths", [])
    max_files = min(len(paths_raw), 100)
    paths = [Path(p) for p in paths_raw[:max_files]]

    meta_map: dict[Path, dict] = {}
    try:
        from media_manager.core.exiftool_persistent import get_persistent_exiftool
        persistent = get_persistent_exiftool()
        meta_map = persistent.read_metadata_batch(paths)
    except Exception:
        pass

    if not meta_map:
        try:
            from media_manager.exiftool import read_exiftool_metadata_batch
            meta_map = read_exiftool_metadata_batch(paths)
        except Exception:
            pass

    results = []
    for p in paths:
        meta = meta_map.get(p)
        results.append(_build_enriched_entry(p, meta))

    _emit({
        "files": results,
        "total_requested": len(paths_raw),
        "returned": len(results),
    })
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="media_manager.bridge_enrich")
    parser.add_argument("action", choices=["enrich", "enrich-batch"])
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv or sys.argv[1:])
    if args.action == "enrich":
        return cmd_enrich()
    if args.action == "enrich-batch":
        return cmd_enrich_batch()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
