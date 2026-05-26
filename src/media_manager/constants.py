from __future__ import annotations

from .media_formats import list_supported_media_extensions

MEDIA_EXTENSIONS = set(list_supported_media_extensions())

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
