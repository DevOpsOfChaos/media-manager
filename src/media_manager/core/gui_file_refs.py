from __future__ import annotations

from pathlib import Path
from typing import Any

FILE_REF_SCHEMA_VERSION = "1.0"


def _as_text(value: object) -> str:
    return value if isinstance(value, str) else ""


def normalize_local_path(path: str | Path | None) -> str | None:
    if path is None:
        return None
    text = str(path).strip()
    if not text:
        return None
    return str(Path(text))


def build_local_file_ref(path: str | Path | None, *, role: str = "file", base_dir: str | Path | None = None) -> dict[str, object]:
    """Build a stable GUI-facing local file reference without opening the file."""
    normalized = normalize_local_path(path)
    payload: dict[str, object] = {
        "schema_version": FILE_REF_SCHEMA_VERSION,
        "type": "local_path",
        "role": role,
        "path": normalized,
        "exists": False,
        "is_file": False,
        "is_dir": False,
        "relative_path": None,
        "uri": None,
    }
    if normalized is None:
        return payload

    resolved = Path(normalized)
    payload["exists"] = resolved.exists()
    payload["is_file"] = resolved.is_file()
    payload["is_dir"] = resolved.is_dir()
    payload["uri"] = resolved.resolve().as_uri() if resolved.exists() else None
    if base_dir is not None:
        try:
            payload["relative_path"] = resolved.relative_to(Path(base_dir)).as_posix()
        except ValueError:
            payload["relative_path"] = None
    return payload


def build_asset_ref(asset: dict[str, Any], *, bundle_dir: str | Path | None = None) -> dict[str, object]:
    """Normalize one people-review asset entry for GUI rendering."""
    asset_path = asset.get("asset_path") or asset.get("path")
    face_id = _as_text(asset.get("face_id"))
    ref = build_local_file_ref(asset_path, role="face_crop", base_dir=bundle_dir)
    ref.update(
        {
            "face_id": face_id,
            "status": asset.get("status"),
            "error": asset.get("error"),
            "source_path": asset.get("path"),
            "review_group_id": asset.get("review_group_id"),
            "selected_name": asset.get("selected_name"),
            "include": asset.get("include"),
        }
    )
    return ref


def collect_asset_refs(asset_manifest: dict[str, Any] | None, *, bundle_dir: str | Path | None = None, limit: int = 200) -> list[dict[str, object]]:
    if not isinstance(asset_manifest, dict):
        return []
    assets = asset_manifest.get("assets")
    if not isinstance(assets, list):
        return []
    result: list[dict[str, object]] = []
    for item in assets[: max(0, int(limit))]:
        if isinstance(item, dict):
            result.append(build_asset_ref(item, bundle_dir=bundle_dir))
    return result


__all__ = [
    "FILE_REF_SCHEMA_VERSION",
    "build_asset_ref",
    "build_local_file_ref",
    "collect_asset_refs",
    "normalize_local_path",
]
