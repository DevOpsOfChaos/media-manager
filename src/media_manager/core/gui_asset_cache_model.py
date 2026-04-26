from __future__ import annotations

from collections.abc import Iterable, Mapping
import hashlib
from pathlib import Path
from typing import Any

ASSET_CACHE_SCHEMA_VERSION = "1.0"


def build_asset_cache_key(path: str | Path | None, *, role: str = "asset", size: int = 256) -> str:
    token = f"{role}|{size}|{Path(path).as_posix() if path is not None else ''}"
    return hashlib.sha1(token.encode("utf-8")).hexdigest()[:20]


def build_asset_cache_manifest(
    asset_refs: Iterable[Mapping[str, Any]],
    *,
    cache_dir: str | Path,
    thumbnail_size: int = 256,
) -> dict[str, object]:
    root = Path(cache_dir)
    entries: list[dict[str, object]] = []
    for ref in asset_refs:
        source = ref.get("path") or ref.get("asset_path") or ref.get("value")
        role = str(ref.get("role") or "asset")
        key = build_asset_cache_key(source, role=role, size=thumbnail_size)
        sensitive = role in {"face", "people_face", "face_crop"} or bool(ref.get("sensitive"))
        entries.append(
            {
                "cache_key": key,
                "role": role,
                "source_path": str(source) if source is not None else "",
                "cache_path": str(root / f"{key}.jpg"),
                "thumbnail_size": thumbnail_size,
                "sensitive": sensitive,
            }
        )
    return {
        "schema_version": ASSET_CACHE_SCHEMA_VERSION,
        "kind": "asset_cache_manifest",
        "cache_dir": str(root),
        "thumbnail_size": thumbnail_size,
        "entry_count": len(entries),
        "sensitive_count": sum(1 for item in entries if item["sensitive"]),
        "entries": entries,
    }


def prune_asset_cache_manifest(manifest: Mapping[str, Any], *, keep_limit: int) -> dict[str, object]:
    entries = manifest.get("entries") if isinstance(manifest.get("entries"), list) else []
    kept = entries[: max(0, keep_limit)]
    removed = entries[max(0, keep_limit) :]
    return {
        "schema_version": ASSET_CACHE_SCHEMA_VERSION,
        "kind": "asset_cache_prune_plan",
        "keep_limit": max(0, keep_limit),
        "kept_count": len(kept),
        "removed_count": len(removed),
        "kept": kept,
        "removed": removed,
    }


__all__ = ["ASSET_CACHE_SCHEMA_VERSION", "build_asset_cache_key", "build_asset_cache_manifest", "prune_asset_cache_manifest"]
