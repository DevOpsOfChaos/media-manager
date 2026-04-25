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


# Keep this catalog deliberately explicit. Exact duplicate scanning is byte-based and
# therefore safe for every listed media format, including videos and RAW files. Similar
# image scanning remains opt-in only for formats Pillow can commonly decode reliably.
_MEDIA_FORMAT_CAPABILITIES: tuple[MediaFormatCapability, ...] = (
    # Common raster images
    MediaFormatCapability(".jpg", "image", True, True, True, "JPEG image"),
    MediaFormatCapability(".jpeg", "image", True, True, True, "JPEG image"),
    MediaFormatCapability(".jpe", "image", True, True, True, "JPEG image"),
    MediaFormatCapability(".jfif", "image", True, True, True, "JPEG/JFIF image"),
    MediaFormatCapability(".png", "image", True, True, True, "PNG image"),
    MediaFormatCapability(".gif", "image", True, True, True, "GIF image"),
    MediaFormatCapability(".bmp", "image", True, True, True, "Bitmap image"),
    MediaFormatCapability(".dib", "image", True, True, True, "Bitmap image"),
    MediaFormatCapability(".tif", "image", True, True, True, "TIFF image"),
    MediaFormatCapability(".tiff", "image", True, True, True, "TIFF image"),
    MediaFormatCapability(".webp", "image", True, True, True, "WebP image"),
    MediaFormatCapability(".avif", "image", True, False, True, "AVIF image; exact duplicates are supported, similar-image support is decoder-dependent."),
    MediaFormatCapability(".heic", "image", True, False, True, "HEIC image; exact duplicates are supported, similar-image support is decoder-dependent."),
    MediaFormatCapability(".heif", "image", True, False, True, "HEIF image; exact duplicates are supported, similar-image support is decoder-dependent."),

    # RAW still image formats
    MediaFormatCapability(".dng", "raw-image", True, False, True, "Digital Negative RAW image"),
    MediaFormatCapability(".raw", "raw-image", True, False, True, "Generic RAW image"),
    MediaFormatCapability(".arw", "raw-image", True, False, True, "Sony RAW image"),
    MediaFormatCapability(".srf", "raw-image", True, False, True, "Sony RAW image"),
    MediaFormatCapability(".sr2", "raw-image", True, False, True, "Sony RAW image"),
    MediaFormatCapability(".cr2", "raw-image", True, False, True, "Canon RAW image"),
    MediaFormatCapability(".cr3", "raw-image", True, False, True, "Canon RAW image"),
    MediaFormatCapability(".crw", "raw-image", True, False, True, "Canon RAW image"),
    MediaFormatCapability(".nef", "raw-image", True, False, True, "Nikon RAW image"),
    MediaFormatCapability(".nrw", "raw-image", True, False, True, "Nikon RAW image"),
    MediaFormatCapability(".orf", "raw-image", True, False, True, "Olympus RAW image"),
    MediaFormatCapability(".rw2", "raw-image", True, False, True, "Panasonic RAW image"),
    MediaFormatCapability(".rwl", "raw-image", True, False, True, "Leica RAW image"),
    MediaFormatCapability(".raf", "raw-image", True, False, True, "Fujifilm RAW image"),
    MediaFormatCapability(".pef", "raw-image", True, False, True, "Pentax RAW image"),
    MediaFormatCapability(".srw", "raw-image", True, False, True, "Samsung RAW image"),
    MediaFormatCapability(".x3f", "raw-image", True, False, True, "Sigma RAW image"),
    MediaFormatCapability(".3fr", "raw-image", True, False, True, "Hasselblad RAW image"),
    MediaFormatCapability(".fff", "raw-image", True, False, True, "Hasselblad RAW image"),
    MediaFormatCapability(".erf", "raw-image", True, False, True, "Epson RAW image"),
    MediaFormatCapability(".kdc", "raw-image", True, False, True, "Kodak RAW image"),
    MediaFormatCapability(".dcr", "raw-image", True, False, True, "Kodak RAW image"),
    MediaFormatCapability(".mrw", "raw-image", True, False, True, "Minolta RAW image"),
    MediaFormatCapability(".mos", "raw-image", True, False, True, "Leaf RAW image"),
    MediaFormatCapability(".mef", "raw-image", True, False, True, "Mamiya RAW image"),

    # Video containers and camera/video formats
    MediaFormatCapability(".mp4", "video", True, False, True, "MPEG-4 video"),
    MediaFormatCapability(".m4v", "video", True, False, True, "M4V video"),
    MediaFormatCapability(".mov", "video", True, False, True, "QuickTime video"),
    MediaFormatCapability(".qt", "video", True, False, True, "QuickTime video"),
    MediaFormatCapability(".avi", "video", True, False, True, "AVI video"),
    MediaFormatCapability(".mkv", "video", True, False, True, "Matroska video"),
    MediaFormatCapability(".webm", "video", True, False, True, "WebM video"),
    MediaFormatCapability(".wmv", "video", True, False, True, "Windows Media video"),
    MediaFormatCapability(".asf", "video", True, False, True, "Advanced Systems Format video"),
    MediaFormatCapability(".flv", "video", True, False, True, "Flash video"),
    MediaFormatCapability(".f4v", "video", True, False, True, "Flash/MPEG-4 video"),
    MediaFormatCapability(".3gp", "video", True, False, True, "3GPP video"),
    MediaFormatCapability(".3g2", "video", True, False, True, "3GPP2 video"),
    MediaFormatCapability(".mpg", "video", True, False, True, "MPEG video"),
    MediaFormatCapability(".mpeg", "video", True, False, True, "MPEG video"),
    MediaFormatCapability(".mpe", "video", True, False, True, "MPEG video"),
    MediaFormatCapability(".m2v", "video", True, False, True, "MPEG-2 video"),
    MediaFormatCapability(".mp2", "video", True, False, True, "MPEG transport/program video"),
    MediaFormatCapability(".vob", "video", True, False, True, "DVD video object"),
    MediaFormatCapability(".ogv", "video", True, False, True, "Ogg video"),
    MediaFormatCapability(".ogm", "video", True, False, True, "Ogg media video"),
    MediaFormatCapability(".divx", "video", True, False, True, "DivX video"),
    MediaFormatCapability(".xvid", "video", True, False, True, "Xvid video"),
    MediaFormatCapability(".mts", "video", True, False, True, "AVCHD transport stream"),
    MediaFormatCapability(".m2ts", "video", True, False, True, "Blu-ray transport stream"),
    MediaFormatCapability(".ts", "video", True, False, True, "MPEG transport stream"),
    MediaFormatCapability(".mxf", "video", True, False, True, "Material Exchange Format video"),
    MediaFormatCapability(".mod", "video", True, False, True, "Camcorder MOD video"),
    MediaFormatCapability(".tod", "video", True, False, True, "Camcorder TOD video"),
    MediaFormatCapability(".rm", "video", True, False, True, "RealMedia video"),
    MediaFormatCapability(".rmvb", "video", True, False, True, "RealMedia variable bitrate video"),

    # Audio formats (exact duplicate scanning is byte-based and safe; similar-image scanning is not applicable)
    MediaFormatCapability(".mp3", "audio", True, False, True, "MP3 audio"),
    MediaFormatCapability(".m4a", "audio", True, False, True, "MPEG-4 audio"),
    MediaFormatCapability(".aac", "audio", True, False, True, "AAC audio"),
    MediaFormatCapability(".wav", "audio", True, False, True, "Waveform audio"),
    MediaFormatCapability(".wave", "audio", True, False, True, "Waveform audio"),
    MediaFormatCapability(".flac", "audio", True, False, True, "FLAC audio"),
    MediaFormatCapability(".alac", "audio", True, False, True, "Apple Lossless audio"),
    MediaFormatCapability(".ogg", "audio", True, False, True, "Ogg audio"),
    MediaFormatCapability(".oga", "audio", True, False, True, "Ogg audio"),
    MediaFormatCapability(".opus", "audio", True, False, True, "Opus audio"),
    MediaFormatCapability(".wma", "audio", True, False, True, "Windows Media Audio"),
    MediaFormatCapability(".aif", "audio", True, False, True, "AIFF audio"),
    MediaFormatCapability(".aiff", "audio", True, False, True, "AIFF audio"),
    MediaFormatCapability(".ape", "audio", True, False, True, "Monkey's Audio"),
    MediaFormatCapability(".amr", "audio", True, False, True, "AMR audio"),
    MediaFormatCapability(".mid", "audio", True, False, True, "MIDI audio"),
    MediaFormatCapability(".midi", "audio", True, False, True, "MIDI audio"),
    MediaFormatCapability(".caf", "audio", True, False, True, "Core Audio Format"),
    MediaFormatCapability(".dsf", "audio", True, False, True, "DSD Stream File audio"),
    MediaFormatCapability(".dff", "audio", True, False, True, "DSDIFF audio"),
)

_MEDIA_FORMAT_BY_EXTENSION = {item.extension: item for item in _MEDIA_FORMAT_CAPABILITIES}


def _normalize_extension(extension: str) -> str:
    normalized = str(extension).strip().lower()
    if normalized and not normalized.startswith("."):
        normalized = "." + normalized
    return normalized


def list_media_format_capabilities() -> list[MediaFormatCapability]:
    return list(_MEDIA_FORMAT_CAPABILITIES)


def get_media_format_capability(extension: str) -> MediaFormatCapability | None:
    return _MEDIA_FORMAT_BY_EXTENSION.get(_normalize_extension(extension))


def media_kind_for_extension(extension: str) -> str:
    capability = get_media_format_capability(extension)
    return "unknown" if capability is None else capability.media_kind


def list_supported_media_kinds() -> set[str]:
    return {item.media_kind for item in _MEDIA_FORMAT_CAPABILITIES}


def extensions_for_media_kinds(media_kinds: tuple[str, ...] | list[str] | set[str]) -> set[str]:
    normalized_kinds = {str(item).strip().lower() for item in media_kinds if str(item).strip()}
    if not normalized_kinds or "all" in normalized_kinds:
        return list_supported_media_extensions()
    return {item.extension for item in _MEDIA_FORMAT_CAPABILITIES if item.media_kind in normalized_kinds}


def normalize_extensions(extensions: tuple[str, ...] | list[str] | set[str]) -> set[str]:
    return {normalized for item in extensions if (normalized := _normalize_extension(str(item)))}


def unsupported_media_kinds(media_kinds: tuple[str, ...] | list[str] | set[str]) -> set[str]:
    normalized_kinds = {str(item).strip().lower() for item in media_kinds if str(item).strip()}
    return normalized_kinds - {"all"} - list_supported_media_kinds()


def unsupported_media_extensions(extensions: tuple[str, ...] | list[str] | set[str]) -> set[str]:
    return normalize_extensions(extensions) - list_supported_media_extensions()


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


def summarize_supported_media_formats() -> dict[str, object]:
    by_kind: dict[str, int] = {}
    for item in _MEDIA_FORMAT_CAPABILITIES:
        by_kind[item.media_kind] = by_kind.get(item.media_kind, 0) + 1
    return {
        "total_extensions": len(_MEDIA_FORMAT_CAPABILITIES),
        "media_kind_summary": dict(sorted(by_kind.items())),
        "exact_duplicate_extensions": sorted(list_supported_exact_duplicate_extensions()),
        "similar_image_extensions": sorted(list_supported_similar_image_extensions()),
        "formats": [item.to_dict() for item in _MEDIA_FORMAT_CAPABILITIES],
    }
