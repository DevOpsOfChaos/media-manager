from __future__ import annotations

from collections.abc import Mapping
from typing import Any

EMPTY_STATE_RENDERER_SCHEMA_VERSION = "1.0"


def build_qt_empty_state_render_plan(empty_state: Mapping[str, Any] | str | None, *, page_id: str = "unknown") -> dict[str, object]:
    if isinstance(empty_state, Mapping):
        title = str(empty_state.get("title") or "Nothing here yet")
        description = str(empty_state.get("description") or "")
        action = empty_state.get("action")
    elif isinstance(empty_state, str) and empty_state:
        title = empty_state
        description = ""
        action = None
    else:
        title = "Nothing here yet"
        description = "Open or create data for this page."
        action = None
    return {"schema_version": EMPTY_STATE_RENDERER_SCHEMA_VERSION, "page_id": page_id, "widget": "empty_state", "title": title, "description": description, "action": action, "visible": True}


__all__ = ["EMPTY_STATE_RENDERER_SCHEMA_VERSION", "build_qt_empty_state_render_plan"]
