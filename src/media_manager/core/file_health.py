"""Detect corrupted or problematic media files."""

from __future__ import annotations

from pathlib import Path


def detect_file_type(path: Path) -> dict | None:
    """Detect file type from magic bytes. Returns dict with mime_type, description or None."""
    try:
        with open(path, 'rb') as f:
            header = f.read(12)
    except OSError:
        return None

    if len(header) < 2:
        return None

    if header[:2] == b'\xff\xd8':
        return {"mime_type": "image/jpeg", "description": "JPEG image"}
    if header[:8] == b'\x89PNG\r\n\x1a\n':
        return {"mime_type": "image/png", "description": "PNG image"}
    if header[:6] in (b'GIF87a', b'GIF89a'):
        return {"mime_type": "image/gif", "description": "GIF image"}
    if header[:4] == b'RIFF' and header[8:12] == b'WEBP':
        return {"mime_type": "image/webp", "description": "WebP image"}
    if header[:2] in (b'BM',):
        return {"mime_type": "image/bmp", "description": "BMP image"}
    if header[:4] in (b'II*\x00', b'MM\x00*'):
        return {"mime_type": "image/tiff", "description": "TIFF image"}
    suffix = path.suffix.lower()
    if suffix in ('.mp4', '.m4v', '.mov', '.qt', '.avi', '.mkv', '.webm',
                  '.wmv', '.asf', '.flv', '.f4v', '.3gp', '.3g2', '.mpg',
                  '.mpeg', '.mpe', '.m2v', '.mp2', '.vob', '.ogv', '.ogm',
                  '.divx', '.xvid', '.mts', '.m2ts', '.ts', '.mxf', '.mod',
                  '.tod', '.rm', '.rmvb'):
        return {"mime_type": "video/" + suffix.lstrip('.'), "description": f"{suffix.upper()} video"}
    if suffix in ('.mp3', '.m4a', '.aac', '.wav', '.wave', '.flac', '.alac',
                  '.ogg', '.oga', '.opus', '.wma', '.aif', '.aiff', '.ape',
                  '.amr', '.mid', '.midi', '.caf', '.dsf', '.dff'):
        return {"mime_type": "audio/" + suffix.lstrip('.'), "description": f"{suffix.upper()} audio"}
    return None


def check_file_health(path: Path) -> dict:
    """Check if a media file is healthy."""
    result: dict = {
        "path": str(path),
        "healthy": True,
        "issues": [],
        "warnings": [],
    }

    try:
        size = path.stat().st_size
        if size == 0:
            result["healthy"] = False
            result["issues"].append("File is empty (0 bytes)")
            return result
    except OSError:
        result["healthy"] = False
        result["issues"].append("Cannot access file")
        return result

    magic = detect_file_type(path)
    if magic is None:
        result["healthy"] = False
        result["issues"].append("Unknown or corrupted file format")
        return result

    result["detected_type"] = magic["description"]

    if magic["mime_type"] == "image/jpeg":
        try:
            with open(path, 'rb') as f:
                if f.read(2) != b'\xff\xd8':
                    result["healthy"] = False
                    result["issues"].append("Missing JPEG start marker (SOI)")
                f.seek(-2, 2)
                if f.read(2) != b'\xff\xd9':
                    result["warnings"].append("Missing JPEG end marker (EOI) — file may be truncated")
        except OSError:
            result["issues"].append("Cannot read file for JPEG validation")

    if magic["mime_type"] == "image/png":
        try:
            with open(path, 'rb') as f:
                f.read(8)
                f.seek(-12, 2)
                iend = f.read(12)
                if iend[4:8] != b'IEND':
                    result["warnings"].append("Missing PNG end chunk (IEND)")
        except OSError:
            result["issues"].append("Cannot read file for PNG validation")

    min_sizes = {"image/jpeg": 100, "image/png": 67, "image/gif": 35, "image/webp": 20}
    min_size = min_sizes.get(magic["mime_type"])
    if min_size and size < min_size:
        result["warnings"].append(
            f"File size ({size} bytes) below minimum for {magic['description']} ({min_size} bytes)"
        )

    return result


def scan_directory_health(source_dir: Path, max_files: int = 1000) -> dict:
    """Scan a directory for file health issues."""
    healthy: list[dict] = []
    unhealthy: list[dict] = []
    count = 0

    for f in source_dir.rglob("*"):
        if not f.is_file():
            continue
        if count >= max_files:
            break

        result = check_file_health(f)
        if result["healthy"]:
            healthy.append({"path": result["path"], "type": result.get("detected_type", "unknown")})
        else:
            unhealthy.append(result)
        count += 1

    return {
        "total_scanned": count,
        "healthy_count": len(healthy),
        "unhealthy_count": len(unhealthy),
        "health_score": len(healthy) * 100 // max(count, 1),
        "issues": unhealthy,
    }
