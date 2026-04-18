from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class MediaFormatCapability:
    extension: str
    media_kind: str
    exact_duplicates: bool
    similar_images: bool
    date_resolution: bool
    notes: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "extension": self.extension,
            "media_kind": self.media_kind,
            "exact_duplicates": self.exact_duplicates,
            "similar_images": self.similar_images,
            "date_resolution": self.date_resolution,
            "notes": self.notes,
        }


_MEDIA_FORMAT_CAPABILITIES: tuple[MediaFormatCapability, ...] = (
    MediaFormatCapability(".jpg", "image", True, True, True, "JPEG image"),
    MediaFormatCapability(".jpeg", "image", True, True, True, "JPEG image"),
    MediaFormatCapability(".jpe", "image", True, True, True, "JPEG image"),
    MediaFormatCapability(".jfif", "image", True, True, True, "JPEG/JFIF image"),
    MediaFormatCapability(".png", "image", True, True, True, "PNG image"),
    MediaFormatCapability(".gif", "image", True, True, True, "GIF image"),
    MediaFormatCapability(".bmp", "image", True, True, True, "Bitmap image"),
    MediaFormatCapability(".tif", "image", True, True, True, "TIFF image"),
    MediaFormatCapability(".tiff", "image", True, True, True, "TIFF image"),
    MediaFormatCapability(".webp", "image", True, True, True, "WebP image"),
    MediaFormatCapability(
        ".heic",
        "image",
        True,
        False,
        True,
        "HEIC is scanned for media/exact duplicates, but similar-image hashing is decoder-dependent and therefore disabled by default.",
    ),
    MediaFormatCapability(
        ".heif",
        "image",
        True,
        False,
        True,
        "HEIF is scanned for media/exact duplicates, but similar-image hashing is decoder-dependent and therefore disabled by default.",
    ),
    MediaFormatCapability(
        ".dng",
        "raw-image",
        True,
        False,
        True,
        "RAW/DNG files are included for media scans and exact duplicates, but not for perceptual similarity scanning.",
    ),
    MediaFormatCapability(".raw", "raw-image", True, False, True, "Generic RAW image"),
    MediaFormatCapability(".arw", "raw-image", True, False, True, "Sony RAW image"),
    MediaFormatCapability(".cr2", "raw-image", True, False, True, "Canon RAW image"),
    MediaFormatCapability(".cr3", "raw-image", True, False, True, "Canon RAW image"),
    MediaFormatCapability(".nef", "raw-image", True, False, True, "Nikon RAW image"),
    MediaFormatCapability(".orf", "raw-image", True, False, True, "Olympus RAW image"),
    MediaFormatCapability(".rw2", "raw-image", True, False, True, "Panasonic RAW image"),
    MediaFormatCapability(".mp4", "video", True, False, True, "MPEG-4 video"),
    MediaFormatCapability(".mov", "video", True, False, True, "QuickTime video"),
    MediaFormatCapability(".avi", "video", True, False, True, "AVI video"),
    MediaFormatCapability(".mkv", "video", True, False, True, "Matroska video"),
    MediaFormatCapability(".mts", "video", True, False, True, "AVCHD transport stream"),
    MediaFormatCapability(".m2ts", "video", True, False, True, "Blu-ray transport stream"),
    MediaFormatCapability(".wmv", "video", True, False, True, "Windows Media video"),
    MediaFormatCapability(".flv", "video", True, False, True, "Flash video"),
    MediaFormatCapability(".webm", "video", True, False, True, "WebM video"),
    MediaFormatCapability(".3gp", "video", True, False, True, "3GPP video"),
    MediaFormatCapability(".m4v", "video", True, False, True, "M4V video"),
    MediaFormatCapability(".mpg", "video", True, False, True, "MPEG video"),
    MediaFormatCapability(".mpeg", "video", True, False, True, "MPEG video"),
)

_MEDIA_FORMAT_BY_EXTENSION = {item.extension: item for item in _MEDIA_FORMAT_CAPABILITIES}


def list_media_format_capabilities() -> list[MediaFormatCapability]:
    return list(_MEDIA_FORMAT_CAPABILITIES)


def get_media_format_capability(extension: str) -> MediaFormatCapability | None:
    normalized = extension.strip().lower()
    if not normalized.startswith("."):
        normalized = "." + normalized
    return _MEDIA_FORMAT_BY_EXTENSION.get(normalized)


def is_supported_media_extension(extension: str) -> bool:
    capability = get_media_format_capability(extension)
    return capability is not None


def is_supported_media_path(path) -> bool:
    return is_supported_media_extension(getattr(path, "suffix", ""))


def is_supported_exact_duplicate_extension(extension: str) -> bool:
    capability = get_media_format_capability(extension)
    return capability is not None and capability.exact_duplicates


def is_supported_similar_image_extension(extension: str) -> bool:
    capability = get_media_format_capability(extension)
    return capability is not None and capability.similar_images


def list_supported_media_extensions() -> set[str]:
    return {item.extension for item in _MEDIA_FORMAT_CAPABILITIES}


def list_supported_exact_duplicate_extensions() -> set[str]:
    return {item.extension for item in _MEDIA_FORMAT_CAPABILITIES if item.exact_duplicates}


def list_supported_similar_image_extensions() -> set[str]:
    return {item.extension for item in _MEDIA_FORMAT_CAPABILITIES if item.similar_images}
