from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

GRID_SCHEMA_VERSION = "1.0"
DEFAULT_GRID_LIMIT = 200


def _text(value: object) -> str:
    return value if isinstance(value, str) else ""


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _asset_path(asset: Mapping[str, Any]) -> str:
    for key in ("asset_relative_path", "asset_path", "path"):
        text = _text(asset.get(key))
        if text:
            return text
    image_uri = _mapping(asset.get("image_uri"))
    return _text(image_uri.get("value"))


def _matches_query(card: Mapping[str, Any], query: str) -> bool:
    needle = query.strip().casefold()
    if not needle:
        return True
    haystack = " ".join(
        _text(value)
        for value in (
            card.get("face_id"),
            card.get("title"),
            card.get("subtitle"),
            card.get("source_path"),
            card.get("group_id"),
            card.get("status"),
        )
    ).casefold()
    return needle in haystack


def _normalize_card(asset: Mapping[str, Any], *, selected_ids: set[str]) -> dict[str, object]:
    face_id = _text(asset.get("face_id")) or _text(asset.get("id"))
    status = _text(asset.get("status")) or "unknown"
    group_id = _text(asset.get("review_group_id")) or _text(asset.get("group_id"))
    title = _text(asset.get("selected_name")) or _text(asset.get("matched_name")) or _text(asset.get("suggested_name")) or face_id or "Preview"
    source_path = _text(asset.get("path")) or _text(asset.get("source_path"))
    return {
        "id": face_id or _asset_path(asset),
        "face_id": face_id,
        "group_id": group_id,
        "title": title,
        "subtitle": source_path,
        "status": status,
        "selected": bool((face_id and face_id in selected_ids) or (_asset_path(asset) in selected_ids)),
        "include": bool(asset.get("include", True)) if isinstance(asset.get("include", True), bool) else True,
        "source_path": source_path,
        "asset_path": _asset_path(asset),
        "image_uri": asset.get("image_uri") if isinstance(asset.get("image_uri"), Mapping) else {"type": "local_path", "value": _asset_path(asset)},
        "error": asset.get("error"),
    }


def build_media_preview_grid(
    assets: Iterable[Mapping[str, Any]] | Mapping[str, Any] | None,
    *,
    query: str = "",
    status_filter: str = "all",
    selected_ids: Iterable[str] = (),
    limit: int = DEFAULT_GRID_LIMIT,
    columns: int = 5,
) -> dict[str, object]:
    """Build a GUI-friendly preview grid from face/media asset refs."""
    if isinstance(assets, Mapping):
        raw_assets = [item for item in _list(assets.get("assets")) if isinstance(item, Mapping)]
    else:
        raw_assets = [item for item in list(assets or []) if isinstance(item, Mapping)]
    selected = {str(item) for item in selected_ids if str(item)}
    cards = [_normalize_card(asset, selected_ids=selected) for asset in raw_assets]
    if status_filter and status_filter != "all":
        cards = [card for card in cards if card.get("status") == status_filter]
    cards = [card for card in cards if _matches_query(card, query)]
    max_items = max(0, int(limit))
    displayed = cards[:max_items]
    selected_count = sum(1 for card in displayed if card.get("selected"))
    error_count = sum(1 for card in displayed if card.get("status") == "error" or card.get("error"))
    return {
        "schema_version": GRID_SCHEMA_VERSION,
        "kind": "media_preview_grid",
        "query": query,
        "status_filter": status_filter or "all",
        "columns": max(1, int(columns)),
        "card_count": len(cards),
        "returned_card_count": len(displayed),
        "selected_count": selected_count,
        "error_count": error_count,
        "truncated": len(cards) > len(displayed),
        "cards": displayed,
        "empty_state": "No preview assets match the current filters." if not displayed else None,
    }


__all__ = ["DEFAULT_GRID_LIMIT", "GRID_SCHEMA_VERSION", "build_media_preview_grid"]
