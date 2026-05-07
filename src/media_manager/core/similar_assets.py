from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image

from ..similar_images import SimilarImageGroup

ASSET_SCHEMA_VERSION = 1
ASSET_KIND = "similar_image_assets"
DEFAULT_THUMBNAIL_SIZE = 512


def build_similar_group_id(group: SimilarImageGroup) -> str:
    anchor_hash = group.members[0].hash_hex if group.members else "00000000"
    stem = group.anchor_path.stem
    return f"similar-{stem}_{anchor_hash[:12]}"


def _safe_filename(text: str) -> str:
    keep = "".join(c for c in text if c.isalnum() or c in "._-")
    return keep[:120] or "unnamed"


def _relative_asset_path(asset_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(asset_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _write_similar_thumbnail(
    *,
    source_path: Path,
    group_id: str,
    asset_dir: Path,
    thumbnail_size: int,
    quality: int,
    overwrite: bool,
    is_anchor: bool = False,
    distance: int = 0,
    hash_hex: str = "",
) -> dict[str, object]:
    filename = f"{_safe_filename(source_path.stem)}_{'anchor' if is_anchor else 'candidate'}.jpg"
    output_dir = asset_dir / "similar_images" / group_id
    output_path = output_dir / filename

    base_payload: dict[str, object] = {
        "group_id": group_id,
        "path": str(source_path),
        "is_anchor": is_anchor,
        "distance": distance,
        "hash_hex": hash_hex,
        "asset_path": output_path.as_posix(),
        "asset_relative_path": _relative_asset_path(asset_dir, output_path),
        "image_uri": {"type": "local_path", "value": output_path.as_posix()},
    }

    if output_path.exists() and not overwrite:
        base_payload.update({"status": "exists", "error": None})
        try:
            with Image.open(output_path) as img:
                base_payload["thumbnail_size"] = {"width": img.width, "height": img.height}
        except Exception:
            base_payload["thumbnail_size"] = {"width": 0, "height": 0}
        return base_payload

    if not source_path.exists():
        base_payload.update({"status": "error", "error": "source_image_missing"})
        return base_payload

    try:
        with Image.open(source_path) as image:
            rgb = image.convert("RGB")
            rgb.thumbnail((thumbnail_size, thumbnail_size))
            output_dir.mkdir(parents=True, exist_ok=True)
            rgb.save(output_path, format="JPEG", quality=max(1, min(100, int(quality))))
            base_payload.update(
                {
                    "status": "ok",
                    "error": None,
                    "source_image_size": {"width": image.width, "height": image.height},
                    "thumbnail_size": {"width": rgb.width, "height": rgb.height},
                }
            )
            return base_payload
    except Exception as exc:
        base_payload.update({"status": "error", "error": str(exc)})
        return base_payload


def build_similar_image_assets(
    *,
    similar_groups: list[SimilarImageGroup],
    asset_dir: str | Path,
    thumbnail_size: int = DEFAULT_THUMBNAIL_SIZE,
    quality: int = 90,
    overwrite: bool = True,
) -> dict[str, object]:
    """Write local thumbnail assets for a GUI similar-image comparison page.

    Generates JPEG thumbnails for every member of every similar-image group.
    The manifest references local paths only and never uploads data anywhere.
    """

    resolved_asset_dir = Path(asset_dir)
    assets: list[dict[str, object]] = []

    for group_index, group in enumerate(similar_groups, start=1):
        group_id = build_similar_group_id(group)
        anchor_hash = group.members[0].hash_hex if group.members else ""
        for member in group.members:
            is_anchor = member.path == group.anchor_path
            distance_to_anchor = member.distance if not is_anchor else 0
            asset = _write_similar_thumbnail(
                source_path=member.path,
                group_id=group_id,
                asset_dir=resolved_asset_dir,
                thumbnail_size=thumbnail_size,
                quality=quality,
                overwrite=overwrite,
                is_anchor=is_anchor,
                distance=distance_to_anchor,
                hash_hex=member.hash_hex,
            )
            asset.update(
                {
                    "group_index": group_index,
                    "anchor_path": str(group.anchor_path),
                    "anchor_hash_hex": anchor_hash,
                }
            )
            assets.append(asset)

    generated_count = sum(1 for item in assets if item.get("status") == "ok")
    existing_count = sum(1 for item in assets if item.get("status") == "exists")
    error_count = sum(1 for item in assets if item.get("status") == "error")
    return {
        "schema_version": ASSET_SCHEMA_VERSION,
        "kind": ASSET_KIND,
        "asset_dir": resolved_asset_dir.as_posix(),
        "thumbnail_size": thumbnail_size,
        "quality": quality,
        "summary": {
            "asset_count": len(assets),
            "generated_count": generated_count,
            "existing_count": existing_count,
            "error_count": error_count,
            "group_count": len(similar_groups),
        },
        "assets": assets,
        "privacy_notice": "Similar-image thumbnails reference local files. Keep this directory local/private.",
    }


def write_similar_image_asset_manifest(path: str | Path, payload: Mapping[str, object]) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(dict(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


__all__ = [
    "ASSET_KIND",
    "ASSET_SCHEMA_VERSION",
    "DEFAULT_THUMBNAIL_SIZE",
    "build_similar_group_id",
    "build_similar_image_assets",
    "write_similar_image_asset_manifest",
]
