from __future__ import annotations

from collections.abc import Mapping
from typing import Any

PANEL_STATE_SCHEMA_VERSION = "1.0"

DEFAULT_PANELS = {
    "sidebar": {"visible": True, "width": 280, "minimum": 220, "maximum": 420},
    "detail": {"visible": True, "width": 420, "minimum": 320, "maximum": 720},
    "activity": {"visible": True, "height": 220, "minimum": 160, "maximum": 420},
}


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_bool(value: Any, *, default: bool) -> bool:
    return value if isinstance(value, bool) else default


def _as_int(value: Any, *, default: int) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


def _clamp(value: int, *, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))


def normalize_panel_state(panel_state: Mapping[str, Any] | None = None) -> dict[str, object]:
    source = _as_mapping(panel_state)
    panels: dict[str, object] = {}
    for panel_id, defaults in DEFAULT_PANELS.items():
        raw = _as_mapping(source.get(panel_id))
        visible = _as_bool(raw.get("visible"), default=bool(defaults["visible"]))
        payload: dict[str, object] = {
            "id": panel_id,
            "visible": visible,
            "minimum": defaults["minimum"],
            "maximum": defaults["maximum"],
        }
        if "width" in defaults:
            payload["width"] = _clamp(
                _as_int(raw.get("width"), default=int(defaults["width"])),
                minimum=int(defaults["minimum"]),
                maximum=int(defaults["maximum"]),
            )
        if "height" in defaults:
            payload["height"] = _clamp(
                _as_int(raw.get("height"), default=int(defaults["height"])),
                minimum=int(defaults["minimum"]),
                maximum=int(defaults["maximum"]),
            )
        panels[panel_id] = payload
    return {
        "schema_version": PANEL_STATE_SCHEMA_VERSION,
        "kind": "gui_panel_state",
        "panels": panels,
        "visible_panel_count": sum(1 for item in panels.values() if isinstance(item, Mapping) and item.get("visible")),
    }


def update_panel_visibility(
    panel_state: Mapping[str, Any] | None,
    *,
    panel_id: str,
    visible: bool,
) -> dict[str, object]:
    state = normalize_panel_state(panel_state)
    panels = dict(_as_mapping(state.get("panels")))
    if panel_id in panels and isinstance(panels[panel_id], Mapping):
        panels[panel_id] = {**dict(panels[panel_id]), "visible": bool(visible)}
    return normalize_panel_state(panels)


def update_panel_size(
    panel_state: Mapping[str, Any] | None,
    *,
    panel_id: str,
    size: int,
) -> dict[str, object]:
    state = normalize_panel_state(panel_state)
    panels = dict(_as_mapping(state.get("panels")))
    panel = _as_mapping(panels.get(panel_id))
    if not panel:
        return state
    if "width" in panel:
        panels[panel_id] = {**dict(panel), "width": int(size)}
    elif "height" in panel:
        panels[panel_id] = {**dict(panel), "height": int(size)}
    return normalize_panel_state(panels)


__all__ = [
    "DEFAULT_PANELS",
    "PANEL_STATE_SCHEMA_VERSION",
    "normalize_panel_state",
    "update_panel_size",
    "update_panel_visibility",
]
