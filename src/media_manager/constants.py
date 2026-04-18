from __future__ import annotations

from .media_formats import list_supported_media_extensions

MEDIA_EXTENSIONS = list_supported_media_extensions()

DATE_TAG_PRIORITY = [
    "DateTimeOriginal",
    "CreateDate",
    "MediaCreateDate",
    "TrackCreateDate",
    "ModifyDate",
    "FileModifyDate",
]
