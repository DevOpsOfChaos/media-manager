from __future__ import annotations

from collections.abc import Mapping
from typing import Any

WINDOW_STATE_SCHEMA_VERSION = "1.0"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def clamp_window_size(width: int, height: int, *, min_width: int = 1000, min_height: int = 700, max_width: int = 3840, max_height: int = 2160) -> dict[str, int]:
    return {
        "width": min(max(int(width), min_width), max_width),
        "height": min(max(int(height), min_height), max_height),
    }


def build_qt_window_state(shell_model: Mapping[str, Any]) -> dict[str, Any]:
    window = _as_mapping(shell_model.get("window"))
    size = clamp_window_size(int(window.get("width", 1440) or 1440), int(window.get("height", 940) or 940))
    return {
        "schema_version": WINDOW_STATE_SCHEMA_VERSION,
        "kind": "qt_window_state",
        "title": window.get("title") or "Media Manager",
        **size,
        "minimum_width": int(window.get("minimum_width", 1100) or 1100),
        "minimum_height": int(window.get("minimum_height", 740) or 740),
        "maximized": bool(window.get("maximized", False)),
        "remember_geometry": True,
    }


def update_window_state(window_state: Mapping[str, Any], *, width: int | None = None, height: int | None = None, maximized: bool | None = None) -> dict[str, Any]:
    current = dict(window_state)
    size = clamp_window_size(width if width is not None else int(current.get("width", 1440)), height if height is not None else int(current.get("height", 940)))
    current.update(size)
    if maximized is not None:
        current["maximized"] = bool(maximized)
    return current


__all__ = ["WINDOW_STATE_SCHEMA_VERSION", "build_qt_window_state", "clamp_window_size", "update_window_state"]
