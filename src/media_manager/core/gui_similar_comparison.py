from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..similar_review import build_similar_review_report
from .gui_empty_states import build_empty_state

PAGE_MODEL_SCHEMA_VERSION = "3.0"


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


def _text(value: object, fallback: str = "") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text or fallback


def _match_kind(distance: int) -> str:
    if distance <= 0:
        return "exact-hash"
    if distance <= 2:
        return "very-close"
    if distance <= 5:
        return "close"
    return "broad"


def _review_priority(distance: int) -> str:
    if distance <= 2:
        return "high"
    if distance <= 5:
        return "medium"
    return "low"


def build_similar_comparison_page_model(
    home_state: Mapping[str, Any],
    *,
    language: str = "en",
) -> dict[str, object]:
    """Build the side-by-side similar-image comparison page model.

    Left panel = keep candidate. Right panel = review candidate.
    Headless, no PySide6, non-executing.

    home_state may contain keys: similar_groups, asset_manifest, decisions, selected_group_index.
    """

    home = _as_mapping(home_state)
    groups = list(home.get("similar_groups", []) or [])
    if not groups:
        return {
            "schema_version": PAGE_MODEL_SCHEMA_VERSION,
            "page_id": "similar-comparison",
            "title": "Similar Image Comparison",
            "description": "Run a similar-images scan to populate comparison pairs.",
            "kind": "similar_comparison_page",
            "layout": "side_by_side_comparison",
            "total_groups": 0,
            "total_candidates": 0,
            "reviewed_count": 0,
            "remaining_count": 0,
            "current_group_index": 0,
            "current_pair_index": 0,
            "navigation": {"has_previous_group": False, "has_next_group": False, "has_previous_candidate": False, "has_next_candidate": False},
            "current_pair": None,
            "actions": [],
            "asset_refs": [],
            "empty_state": build_empty_state("similar-comparison", language=language),
            "capabilities": {"headless_testable": True, "requires_pyside6": False, "opens_window": False, "executes_commands": False, "apply_enabled": False},
        }

    decisions = dict(home.get("decisions") or {})
    asset_manifest = _as_mapping(home.get("asset_manifest") or {})
    selected_group_index = _as_int(home.get("selected_group_index"), 0)
    assets_by_path: dict[str, dict[str, object]] = {}
    for asset in _as_list(asset_manifest.get("assets")):
        if isinstance(asset, Mapping):
            assets_by_path[str(asset.get("path", ""))] = dict(asset)

    total_groups = len(groups)
    group_index = max(0, min(selected_group_index, total_groups - 1)) if total_groups else 0
    current_group = groups[group_index] if groups else None

    pairs: list[dict[str, object]] = []
    total_candidates = 0
    current_pair_index = 0
    review_report = build_similar_review_report(groups, keep_policy="first") if groups else None

    for g_idx, group in enumerate(groups):
        group_decisions = decisions.get(f"similar-{group.anchor_path.stem}_{group.members[0].hash_hex[:12]}", {})
        keep_path = group.anchor_path
        for member in group.members:
            if member.path == keep_path:
                continue
            total_candidates += 1
            member_path_str = str(member.path)
            keep_asset = assets_by_path.get(str(keep_path), {})
            candidate_asset = assets_by_path.get(member_path_str, {})
            decision = group_decisions.get(member_path_str)

            pair = {
                "group_index": g_idx,
                "group_size": len(group.members),
                "candidate_index": total_candidates - 1,
                "keep": {
                    "path": str(keep_path),
                    "asset_path": keep_asset.get("asset_path", str(keep_path)),
                    "image_uri": keep_asset.get("image_uri") or {"type": "local_path", "value": str(keep_path)},
                    "hash_hex": next((m.hash_hex for m in group.members if m.path == keep_path), ""),
                    "distance": 0,
                    "width": keep_asset.get("source_image_size", {}).get("width") or next((m.width for m in group.members if m.path == keep_path), None),
                    "height": keep_asset.get("source_image_size", {}).get("height") or next((m.height for m in group.members if m.path == keep_path), None),
                },
                "candidate": {
                    "path": member_path_str,
                    "asset_path": candidate_asset.get("asset_path", member_path_str),
                    "image_uri": candidate_asset.get("image_uri") or {"type": "local_path", "value": member_path_str},
                    "hash_hex": member.hash_hex,
                    "distance": member.distance,
                    "match_kind": _match_kind(member.distance),
                    "review_priority": _review_priority(member.distance),
                    "width": member.width,
                    "height": member.height,
                },
                "decision": decision,
            }
            pairs.append(pair)

    current_pair: dict[str, object] | None = None
    if pairs:
        current_pair_index = 0
        current_pair = pairs[0]

    nav_has_next = current_pair_index < len(pairs) - 1 if pairs else False
    nav_has_prev = current_pair_index > 0

    reviewed_count = sum(
        1 for gid, gdec in decisions.items()
        for d in gdec.values()
        if d in {"keep", "remove"}
    )
    remaining_count = max(0, total_candidates - reviewed_count)

    return {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": "similar-comparison",
        "title": "Similar Image Comparison",
        "description": f"Side-by-side visual review of similar image groups ({total_groups} groups, {total_candidates} candidates).",
        "kind": "similar_comparison_page",
        "layout": "side_by_side_comparison",
        "total_groups": total_groups,
        "total_candidates": total_candidates,
        "reviewed_count": reviewed_count,
        "remaining_count": remaining_count,
        "current_group_index": group_index,
        "current_pair_index": current_pair_index,
        "navigation": {
            "has_previous_group": group_index > 0,
            "has_next_group": group_index < total_groups - 1,
            "has_previous_candidate": nav_has_prev,
            "has_next_candidate": nav_has_next,
        },
        "current_pair": current_pair,
        "all_pairs": pairs,
        "actions": [
            {"id": "keep-left", "label": "Keep Left", "description": "Keep the left image, remove the right.", "enabled": current_pair is not None, "executes_immediately": True},
            {"id": "keep-right", "label": "Keep Right", "description": "Keep the right image instead of the left.", "enabled": current_pair is not None, "executes_immediately": True},
            {"id": "keep-both", "label": "Keep Both", "description": "Keep both images.", "enabled": current_pair is not None, "executes_immediately": True},
            {"id": "skip", "label": "Skip", "description": "Skip this pair for now.", "enabled": current_pair is not None, "executes_immediately": True},
            {"id": "next-candidate", "label": "Next", "description": "Go to next comparison pair.", "enabled": nav_has_next, "executes_immediately": True},
            {"id": "prev-candidate", "label": "Previous", "description": "Go to previous comparison pair.", "enabled": nav_has_prev, "executes_immediately": True},
        ],
        "asset_refs": [
            {
                "path": pair["keep"]["path"],
                "image_uri": pair["keep"]["image_uri"],
                "pair_index": pair["candidate_index"],
            }
            for pair in pairs
        ]
        + [
            {
                "path": pair["candidate"]["path"],
                "image_uri": pair["candidate"]["image_uri"],
                "pair_index": pair["candidate_index"],
            }
            for pair in pairs
        ],
        "empty_state": build_empty_state("similar-comparison", language=language) if not current_pair else None,
        "capabilities": {
            "headless_testable": True,
            "requires_pyside6": False,
            "opens_window": False,
            "executes_commands": False,
            "apply_enabled": False,
        },
    }
