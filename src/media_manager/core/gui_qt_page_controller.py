from __future__ import annotations

from collections.abc import Mapping
from typing import Any

PAGE_CONTROLLER_SCHEMA_VERSION = "1.0"


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _text(value: Any, default: str = "") -> str:
    return str(value) if value is not None else default


def normalize_page_id(page_id: str | None) -> str:
    value = _text(page_id, "dashboard").strip().lower().replace("_", "-")
    aliases = {
        "home": "dashboard",
        "people": "people-review",
        "runs": "run-history",
        "history": "run-history",
        "doctor": "settings",
        "settings-doctor": "settings",
    }
    return aliases.get(value, value or "dashboard")


def build_page_controller_state(shell_model: Mapping[str, Any], *, target_page_id: str | None = None) -> dict[str, Any]:
    navigation = [item for item in _as_list(shell_model.get("navigation")) if isinstance(item, Mapping)]
    page_ids = [normalize_page_id(_text(item.get("id"))) for item in navigation]
    active = normalize_page_id(target_page_id or _text(shell_model.get("active_page_id"), "dashboard"))
    if active not in page_ids and page_ids:
        active = page_ids[0]
    return {
        "schema_version": PAGE_CONTROLLER_SCHEMA_VERSION,
        "kind": "qt_page_controller_state",
        "active_page_id": active,
        "known_page_ids": page_ids,
        "can_go_back": False,
        "can_go_forward": False,
        "navigation": [
            {
                "page_id": normalize_page_id(_text(item.get("id"))),
                "label": item.get("label"),
                "enabled": bool(item.get("enabled", True)),
                "active": normalize_page_id(_text(item.get("id"))) == active,
            }
            for item in navigation
        ],
    }


def plan_page_switch(controller_state: Mapping[str, Any], target_page_id: str) -> dict[str, Any]:
    target = normalize_page_id(target_page_id)
    known = [normalize_page_id(_text(item)) for item in _as_list(controller_state.get("known_page_ids"))]
    allowed = target in known
    active = normalize_page_id(_text(controller_state.get("active_page_id"), "dashboard"))
    return {
        "schema_version": PAGE_CONTROLLER_SCHEMA_VERSION,
        "kind": "qt_page_switch_plan",
        "from_page_id": active,
        "to_page_id": target,
        "allowed": allowed,
        "no_op": active == target,
        "blocked_reason": None if allowed else "unknown_page",
        "updates_navigation": allowed,
        "rebuilds_page": allowed and active != target,
    }


def apply_page_switch(controller_state: Mapping[str, Any], switch_plan: Mapping[str, Any]) -> dict[str, Any]:
    if not switch_plan.get("allowed"):
        return dict(controller_state)
    target = normalize_page_id(_text(switch_plan.get("to_page_id")))
    updated = dict(controller_state)
    updated["active_page_id"] = target
    updated["navigation"] = [
        {**dict(_as_mapping(item)), "active": normalize_page_id(_text(_as_mapping(item).get("page_id"))) == target}
        for item in _as_list(controller_state.get("navigation"))
        if isinstance(item, Mapping)
    ]
    return updated


__all__ = [
    "PAGE_CONTROLLER_SCHEMA_VERSION",
    "apply_page_switch",
    "build_page_controller_state",
    "normalize_page_id",
    "plan_page_switch",
]
