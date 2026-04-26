from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

IMAGE_LOADING_SCHEMA_VERSION = "1.0"


def build_image_load_request(asset_ref: Mapping[str, Any], *, thumbnail_size: int = 256, prefer_cache: bool = True) -> dict[str, object]:
    path = asset_ref.get("path") or asset_ref.get("asset_path") or asset_ref.get("source_path") or asset_ref.get("value")
    source = Path(str(path)) if path else None
    exists = source.exists() if source is not None else False
    return {
        "schema_version": IMAGE_LOADING_SCHEMA_VERSION,
        "kind": "image_load_request",
        "source_path": str(source) if source is not None else "",
        "exists": exists,
        "thumbnail_size": thumbnail_size,
        "prefer_cache": bool(prefer_cache),
        "role": asset_ref.get("role") or "image",
        "face_id": asset_ref.get("face_id"),
        "priority": 0 if exists else 50,
        "status": "ready" if exists else "missing",
    }


def build_image_loading_queue(asset_refs: Iterable[Mapping[str, Any]], *, thumbnail_size: int = 256, max_items: int = 200) -> dict[str, object]:
    requests = [build_image_load_request(ref, thumbnail_size=thumbnail_size) for ref in asset_refs]
    requests.sort(key=lambda item: (int(item["priority"]), str(item["source_path"]).casefold()))
    returned = requests[: max(0, max_items)]
    return {
        "schema_version": IMAGE_LOADING_SCHEMA_VERSION,
        "kind": "image_loading_queue",
        "thumbnail_size": thumbnail_size,
        "request_count": len(requests),
        "returned_count": len(returned),
        "missing_count": sum(1 for item in requests if item["status"] == "missing"),
        "truncated": len(returned) < len(requests),
        "requests": returned,
    }


__all__ = ["IMAGE_LOADING_SCHEMA_VERSION", "build_image_load_request", "build_image_loading_queue"]
