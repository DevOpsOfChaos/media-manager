from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

IMAGE_CARD_ADAPTER_SCHEMA_VERSION = "1.0"


def _text(value: object) -> str:
    return str(value) if value is not None else ""


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _path_exists(value: object) -> bool:
    text = _text(value)
    return bool(text) and Path(text).exists()


def build_qt_image_card(asset: Mapping[str, Any], *, selected: bool = False) -> dict[str, object]:
    image_uri = _as_mapping(asset.get("image_uri"))
    path = asset.get("asset_path") or image_uri.get("value") or asset.get("path")
    face_id = asset.get("face_id") or asset.get("id") or _text(path)
    return {
        "schema_version": IMAGE_CARD_ADAPTER_SCHEMA_VERSION,
        "kind": "qt_image_card",
        "id": str(face_id),
        "title": str(asset.get("display_label") or asset.get("matched_name") or asset.get("face_id") or "Face"),
        "subtitle": str(asset.get("path") or ""),
        "path": _text(path),
        "exists": _path_exists(path),
        "selected": bool(selected),
        "sensitive": True,
        "status": asset.get("status") or asset.get("decision_status") or "unknown",
        "badges": [item for item in [asset.get("status"), asset.get("matched_name"), asset.get("unknown_cluster_id")] if item],
    }


def build_qt_image_card_grid(
    assets: Sequence[Mapping[str, Any]],
    *,
    selected_ids: Sequence[str] = (),
    max_cards: int = 120,
) -> dict[str, object]:
    selected = {str(item) for item in selected_ids}
    visible = list(assets)[: max(0, int(max_cards))]
    cards = [build_qt_image_card(asset, selected=str(asset.get("face_id") or asset.get("id")) in selected) for asset in visible]
    return {
        "schema_version": IMAGE_CARD_ADAPTER_SCHEMA_VERSION,
        "kind": "qt_image_card_grid",
        "card_count": len(cards),
        "asset_count": len(assets),
        "truncated": len(assets) > len(cards),
        "sensitive_asset_count": sum(1 for card in cards if card.get("sensitive")),
        "cards": cards,
        "privacy_notice": "Face cards can reveal sensitive people data and should stay local/private.",
    }


__all__ = ["IMAGE_CARD_ADAPTER_SCHEMA_VERSION", "build_qt_image_card", "build_qt_image_card_grid"]
