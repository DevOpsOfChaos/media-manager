from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

IMAGE_PIPELINE_SCHEMA_VERSION = "1.0"

def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}

def _text(value: object, fallback: str = "") -> str:
    return str(value) if value is not None else fallback

def build_qt_image_request(asset: Mapping[str, Any], *, size: int = 192) -> dict[str, object]:
    path = _text(asset.get("asset_path") or asset.get("path"))
    sensitive = bool(asset.get("sensitive") or asset.get("role") == "face_crop" or asset.get("kind") == "face")
    return {
        "schema_version": IMAGE_PIPELINE_SCHEMA_VERSION,
        "kind": "qt_image_request",
        "asset_id": asset.get("asset_id") or asset.get("face_id") or Path(path).stem,
        "path": path,
        "exists": Path(path).exists() if path else False,
        "target_size": max(32, min(1024, int(size))),
        "sensitive": sensitive,
        "cache_allowed": not sensitive,
        "redaction_allowed": sensitive,
    }

def build_qt_image_pipeline(assets: Sequence[Mapping[str, Any]], *, size: int = 192, limit: int = 200) -> dict[str, object]:
    selected = list(assets)[: max(0, limit)]
    requests = [build_qt_image_request(asset, size=size) for asset in selected]
    return {
        "schema_version": IMAGE_PIPELINE_SCHEMA_VERSION,
        "kind": "qt_image_pipeline",
        "request_count": len(requests),
        "sensitive_count": sum(1 for item in requests if item["sensitive"]),
        "truncated": len(assets) > len(selected),
        "requests": requests,
    }

__all__ = ["IMAGE_PIPELINE_SCHEMA_VERSION", "build_qt_image_pipeline", "build_qt_image_request"]
