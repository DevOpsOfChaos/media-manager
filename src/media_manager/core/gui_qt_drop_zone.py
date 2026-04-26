from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

DROP_ZONE_SCHEMA_VERSION = "1.0"


_ZONE_EXTENSIONS = {
    "people_bundle": {"json"},
    "profile_file": {"json"},
    "catalog_file": {"json"},
    "media_source": {"jpg", "jpeg", "png", "heic", "mp4", "mov", "mkv", "raw", "dng"},
}


def _norm_ext(path: Path) -> str:
    return path.suffix.lower().lstrip(".")


def build_drop_zone(zone_id: str, *, accepts_directories: bool = True, accepts_files: bool = True) -> dict[str, object]:
    return {
        "schema_version": DROP_ZONE_SCHEMA_VERSION,
        "kind": "qt_drop_zone",
        "zone_id": zone_id,
        "accepts_directories": accepts_directories,
        "accepts_files": accepts_files,
        "accepted_extensions": sorted(_ZONE_EXTENSIONS.get(zone_id, set())),
        "executes_immediately": False,
    }


def classify_dropped_paths(paths: Iterable[str | Path], zone: dict[str, Any]) -> dict[str, object]:
    accepted: list[dict[str, object]] = []
    rejected: list[dict[str, object]] = []
    extensions = set(zone.get("accepted_extensions") or [])
    for raw in paths:
        path = Path(raw)
        is_dir_like = not path.suffix
        if is_dir_like and zone.get("accepts_directories"):
            accepted.append({"path": str(path), "kind": "directory"})
            continue
        ext = _norm_ext(path)
        if path.suffix and zone.get("accepts_files") and (not extensions or ext in extensions):
            accepted.append({"path": str(path), "kind": "file", "extension": ext})
        else:
            rejected.append({"path": str(path), "reason": "unsupported_path_or_extension", "extension": ext})
    return {
        "schema_version": DROP_ZONE_SCHEMA_VERSION,
        "zone_id": zone.get("zone_id"),
        "accepted": accepted,
        "rejected": rejected,
        "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "executes_immediately": False,
    }


__all__ = ["DROP_ZONE_SCHEMA_VERSION", "build_drop_zone", "classify_dropped_paths"]
