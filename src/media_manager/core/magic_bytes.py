"""Content-based file type detection using magic bytes (file signatures)."""

from pathlib import Path
from typing import Optional

# Magic byte signatures: (offset, bytes, mime_type, category, description)
SIGNATURES = {
    # JPEG
    b'\xff\xd8\xff\xe0': ("image/jpeg", "photo", "JPEG (JFIF)"),
    b'\xff\xd8\xff\xe1': ("image/jpeg", "photo", "JPEG (EXIF)"),
    b'\xff\xd8\xff\xe2': ("image/jpeg", "photo", "JPEG (Canon)"),
    b'\xff\xd8\xff\xe8': ("image/jpeg", "photo", "JPEG (SPIFF)"),
    b'\xff\xd8\xff\xdb': ("image/jpeg", "photo", "JPEG"),

    # PNG
    b'\x89PNG\r\n\x1a\n': ("image/png", "photo", "PNG"),

    # GIF
    b'GIF87a': ("image/gif", "photo", "GIF (87a)"),
    b'GIF89a': ("image/gif", "photo", "GIF (89a)"),

    # BMP
    b'BM': ("image/bmp", "photo", "BMP"),

    # WebP
    b'RIFF': ("image/webp", "photo", "WebP (needs RIFF+WEBP check)"),

    # HEIC/HEIF
    b'\x00\x00\x00\x1cftypheic': ("image/heic", "photo", "HEIC"),
    b'\x00\x00\x00\x1cftypheif': ("image/heif", "photo", "HEIF"),
    b'\x00\x00\x00\x1cftypmif1': ("image/heif", "photo", "HEIF (MIF1)"),

    # TIFF/RAW
    b'II*\x00': ("image/tiff", "raw", "TIFF (Intel)"),
    b'MM\x00*': ("image/tiff", "raw", "TIFF (Motorola)"),
    b'II*\x00\x10\x00\x00\x00CR': ("image/x-canon-cr2", "raw", "Canon CR2"),

    # NEF (Nikon)
    b'II*\x00\x10\x00\x00\x00NEF': ("image/x-nikon-nef", "raw", "Nikon NEF"),

    # Video
    b'\x00\x00\x00\x1cftypmp42': ("video/mp4", "video", "MP4"),
    b'\x00\x00\x00\x1cftypisom': ("video/mp4", "video", "MP4 (ISOM)"),
    b'\x00\x00\x00\x1cftypqt  ': ("video/quicktime", "video", "MOV"),
    b'\x00\x00\x00\x1cftypM4V': ("video/mp4", "video", "M4V"),
    b'\x1aE\xdf\xa3': ("video/webm", "video", "WebM/MKV"),

    # AVI
    b'RIFF': ("video/avi", "video", "AVI (needs RIFF+AVI check)"),

    # Audio
    b'ID3': ("audio/mpeg", "audio", "MP3 (ID3)"),
    b'\xff\xfb': ("audio/mpeg", "audio", "MP3 (MPEG)"),
    b'fLaC': ("audio/flac", "audio", "FLAC"),
    b'RIFF': ("audio/wav", "audio", "WAV (needs RIFF+WAVE check)"),
    b'OggS': ("audio/ogg", "audio", "OGG"),

    # PDF
    b'%PDF': ("application/pdf", "document", "PDF"),

    # ZIP/Archive
    b'PK\x03\x04': ("application/zip", "archive", "ZIP"),
}

# RIFF subtypes (need to check bytes 8-11)
RIFF_SUBTYPES = {
    b'WEBP': ("image/webp", "photo", "WebP"),
    b'AVI ': ("video/avi", "video", "AVI"),
    b'WAVE': ("audio/wav", "audio", "WAV"),
}


def detect_file_type(path: Path) -> Optional[dict]:
    """Detect file type by reading magic bytes (ignores file extension).

    Returns: {mime_type, category, description, confidence}
    """
    try:
        with open(path, 'rb') as f:
            header = f.read(16)  # Read first 16 bytes
    except OSError:
        return None

    if len(header) < 4:
        return None

    # Check all signatures
    for sig, (mime, cat, desc) in SIGNATURES.items():
        if header.startswith(sig):
            confidence = 1.0 if len(sig) >= 6 else 0.7
            return {
                "mime_type": mime,
                "category": cat,
                "description": desc,
                "confidence": confidence,
                "detected_by": "magic_bytes",
            }

    # Check RIFF subtypes
    if header.startswith(b'RIFF') and len(header) >= 12:
        riff_type = header[8:12]
        for subtype, (mime, cat, desc) in RIFF_SUBTYPES.items():
            if riff_type.startswith(subtype):
                return {
                    "mime_type": mime,
                    "category": cat,
                    "description": desc,
                    "confidence": 0.9,
                    "detected_by": "magic_bytes_riff",
                }

    return None


def is_media_file(path: Path) -> bool:
    """Check if file is a media file based on content (not extension)."""
    result = detect_file_type(path)
    return result is not None and result["category"] in ("photo", "video", "audio", "raw")


def is_image_file(path: Path) -> bool:
    result = detect_file_type(path)
    return result is not None and result["category"] in ("photo", "raw")
