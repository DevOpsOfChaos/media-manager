from __future__ import annotations

from collections.abc import Mapping
from typing import Any

ASSET_REVIEW_GALLERY_SCHEMA_VERSION = "1.0"


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_asset_review_gallery(asset_refs: list[Mapping[str, Any]] | None = None, *, selected_id: str | None = None, limit: int = 100) -> dict[str, object]:
    cards = []
    for index, asset in enumerate((asset_refs or [])[: max(0, limit)]):
        asset_id = str(asset.get("id") or asset.get("face_id") or asset.get("path") or f"asset-{index + 1}")
        cards.append({
            "id": asset_id,
            "title": str(asset.get("title") or asset.get("face_id") or f"Asset {index + 1}"),
            "path": asset.get("path"),
            "exists": bool(asset.get("exists", True)),
            "sensitive": bool(asset.get("sensitive", asset.get("kind") == "face_crop")),
            "selected": asset_id == selected_id,
            "status": str(asset.get("status") or "pending"),
        })
    return {
        "schema_version": ASSET_REVIEW_GALLERY_SCHEMA_VERSION,
        "kind": "asset_review_gallery",
        "card_count": len(cards),
        "selected_id": selected_id,
        "sensitive_count": sum(1 for card in cards if card["sensitive"]),
        "missing_count": sum(1 for card in cards if not card["exists"]),
        "truncated": bool(asset_refs and len(asset_refs) > len(cards)),
        "cards": cards,
    }


def build_asset_review_gallery_from_page(page_model: Mapping[str, Any], *, selected_id: str | None = None) -> dict[str, object]:
    refs = [_mapping(item) for item in _list(page_model.get("asset_refs")) if isinstance(item, Mapping)]
    detail_faces = _list(_mapping(page_model.get("detail")).get("faces"))
    for face in detail_faces:
        if isinstance(face, Mapping):
            refs.append(face)
    return build_asset_review_gallery(refs, selected_id=selected_id)


__all__ = ["ASSET_REVIEW_GALLERY_SCHEMA_VERSION", "build_asset_review_gallery", "build_asset_review_gallery_from_page"]
