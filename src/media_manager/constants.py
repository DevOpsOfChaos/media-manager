from __future__ import annotations

GERMAN_MONTHS = {
    1: "Januar",
    2: "Februar",
    3: "März",
    4: "April",
    5: "Mai",
    6: "Juni",
    7: "Juli",
    8: "August",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Dezember",
}

DATE_TAG_PRIORITY = [
    "SubSecDateTimeOriginal",
    "DateTimeOriginal",
    "CreationDate",
    "CreateDate",
    "MediaCreateDate",
    "TrackCreateDate",
    "ContentCreateDate",
    "Com.apple.quicktime.creationdate",
]

MEDIA_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".tif", ".tiff",
    ".bmp", ".gif", ".avif", ".raw", ".cr2", ".cr3", ".nef", ".arw", ".dng",
    ".mp4", ".mov", ".m4v", ".avi", ".mkv", ".3gp", ".mts", ".m2ts", ".wmv",
    ".mpg", ".mpeg", ".webm",
}

DEFAULT_TEMPLATE = "{year}/{month_num}-{month_name}/{day}"
DEFAULT_NO_DATE_DIR = "no_date"
