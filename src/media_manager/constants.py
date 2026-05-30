from __future__ import annotations

from .media_formats import list_supported_media_extensions

MEDIA_EXTENSIONS = set(list_supported_media_extensions())

# ── Scanner ──────────────────────────────────────────────────────────
MAX_SCAN_DEPTH = 3
DEFAULT_BATCH_SIZE = 1000
LARGE_LIBRARY_THRESHOLD = 100_000
LARGE_BATCH_SIZE = 5000

# ── Duplicates ───────────────────────────────────────────────────────
SAMPLE_SIZE = 64 * 1024
HASH_CHUNK_SIZE = 1024 * 1024
MAX_SIMILAR_IMAGES = 500
MAX_SIMILAR_PAIRS = 150_000

# ── Face Recognition ─────────────────────────────────────────────────
DEFAULT_TOLERANCE = 0.6
FACE_QUALITY_THRESHOLD = 0.3

# ── Bridge ───────────────────────────────────────────────────────────
MAX_PAGE_SIZE = 1000
LIBRARY_CACHE_TTL = 300
BRIDGE_ENTRY_LIMIT = 200

# ── UI ───────────────────────────────────────────────────────────────
TOAST_DURATION = 4000
DEBOUNCE_DELAY = 300

DATE_TAG_PRIORITY = [
    # Primary EXIF date tags (camera capture date)
    "DateTimeOriginal",
    "CreateDate",
    "DateCreated",
    "DigitalCreationDate",
    # Media-specific
    "MediaCreateDate",
    "TrackCreateDate",
    "ContentCreateDate",
    # Video date tags
    "CreationDate",
    "MediaDate",
    "EncodedDate",
    # Fallbacks (modification date)
    "ModifyDate",
    "FileModifyDate",
    # XMP
    "XMP:DateTimeOriginal",
    "XMP:CreateDate",
    "XMP:DateCreated",
    # IPTC
    "IPTC:DateCreated",
    "IPTC:DigitalCreationDate",
    # QuickTime/MP4
    "QuickTime:CreateDate",
    "QuickTime:MediaCreateDate",
    # RIFF/AVI
    "RIFF:DateTimeOriginal",
    # Windows
    "FileCreateDate",
]
