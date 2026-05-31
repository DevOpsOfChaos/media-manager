"""Automatic tag generation from file metadata."""

from datetime import datetime
from pathlib import Path


def extract_deep_metadata(path: Path) -> dict:
    """Extract nested metadata from a file, returning the structure expected by generate_tags."""
    deep: dict = {
        "camera": {},
        "shot": {},
        "gps": {},
        "meta_score": {"score": 0},
    }

    try:
        from media_manager.exiftool import read_exiftool_metadata
        meta, success, _err_type, _err_msg = read_exiftool_metadata(path)
    except (ImportError, OSError):
        return deep

    if not success or not meta:
        return deep

    score = 0

    make = meta.get("Make")
    if make:
        deep["camera"]["make"] = str(make)
        score += 10

    model = meta.get("Model") or meta.get("CameraModelName")
    if model:
        deep["camera"]["model"] = str(model)
        score += 10

    lens = meta.get("LensModel") or meta.get("LensID")
    if lens:
        deep["camera"]["lens"] = str(lens)
        score += 10

    dt_str = meta.get("DateTimeOriginal") or meta.get("CreateDate")
    if dt_str:
        deep["shot"]["datetime"] = str(dt_str)
        score += 15

    iso = meta.get("ISO")
    if iso is not None:
        deep["shot"]["iso"] = str(iso)
        score += 5

    focal = meta.get("FocalLength") or meta.get("FocalLength35efl")
    if focal is not None:
        deep["shot"]["focal_length"] = str(focal)
        score += 5

    flash = meta.get("Flash")
    if flash is not None:
        deep["shot"]["flash"] = str(flash)
        score += 5

    orientation = meta.get("Orientation")
    if orientation is not None:
        deep["shot"]["orientation"] = str(orientation)
        score += 5

    lat = meta.get("GPSLatitude")
    lon = meta.get("GPSLongitude")
    if lat is not None and lon is not None:
        deep["gps"]["latitude"] = str(lat)
        deep["gps"]["longitude"] = str(lon)
        score += 10
        alt = meta.get("GPSAltitude")
        if alt is not None:
            deep["gps"]["altitude"] = str(alt)

    deep["meta_score"]["score"] = min(score, 100)
    return deep


def generate_tags(deep_meta: dict, filename: str) -> list[str]:
    """Generate smart tags from file metadata."""
    tags = set()

    if deep_meta.get("camera", {}).get("make"):
        tags.add(f"camera:{deep_meta['camera']['make']}")
    if deep_meta.get("camera", {}).get("model"):
        tags.add(f"camera:{deep_meta['camera']['model']}")
    if deep_meta.get("camera", {}).get("lens"):
        tags.add(f"lens:{deep_meta['camera']['lens'][:30]}")

    dt_str = deep_meta.get("shot", {}).get("datetime", "")
    if dt_str:
        try:
            dt = datetime.strptime(str(dt_str)[:10], "%Y:%m:%d")
            tags.add(f"year:{dt.year}")
            tags.add(f"month:{dt.year}-{dt.month:02d}")
            tags.add(f"day:{dt.strftime('%Y-%m-%d')}")

            month = dt.month
            if month in (12, 1, 2):
                tags.add("season:winter")
            elif month in (3, 4, 5):
                tags.add("season:spring")
            elif month in (6, 7, 8):
                tags.add("season:summer")
            else:
                tags.add("season:autumn")

            hour = dt.hour if len(str(dt_str)) > 11 else 12
            if 5 <= hour < 12:
                tags.add("time:morning")
            elif 12 <= hour < 17:
                tags.add("time:afternoon")
            elif 17 <= hour < 21:
                tags.add("time:evening")
            else:
                tags.add("time:night")

            if dt.weekday() >= 5:
                tags.add("weekend")

            decade = (dt.year // 10) * 10
            tags.add(f"decade:{decade}s")
        except ValueError:
            pass

    iso = deep_meta.get("shot", {}).get("iso")
    if iso:
        try:
            iso_val = int(str(iso))
            if iso_val <= 200:
                tags.add("iso:low")
            elif iso_val <= 800:
                tags.add("iso:medium")
            else:
                tags.add("iso:high")
        except ValueError:
            pass

    focal = deep_meta.get("shot", {}).get("focal_length")
    if focal:
        try:
            fl = float(str(focal).replace("mm", ""))
            if fl <= 24:
                tags.add("focal:wide")
            elif fl <= 70:
                tags.add("focal:normal")
            elif fl <= 200:
                tags.add("focal:tele")
            else:
                tags.add("focal:supertele")
        except ValueError:
            pass

    lat = deep_meta.get("gps", {}).get("latitude")
    if lat:
        tags.add("has:gps")

    flash = deep_meta.get("shot", {}).get("flash")
    if flash and str(flash) != "No Flash":
        tags.add("flash:on")

    orientation = deep_meta.get("shot", {}).get("orientation")
    if orientation and "90" in str(orientation):
        tags.add("orientation:portrait")

    ext = Path(filename).suffix.lower()
    if ext in (".cr2", ".cr3", ".nef", ".arw", ".dng"):
        tags.add("type:raw")
    elif ext in (".jpg", ".jpeg"):
        tags.add("type:jpeg")
    elif ext in (".png",):
        tags.add("type:png")
    elif ext in (".mp4", ".mov", ".avi"):
        tags.add("type:video")

    score = deep_meta.get("meta_score", {}).get("score", 0)
    if score >= 80:
        tags.add("meta:excellent")
    elif score >= 60:
        tags.add("meta:good")

    return sorted(tags)
