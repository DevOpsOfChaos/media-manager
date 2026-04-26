from __future__ import annotations

from collections.abc import Mapping
from typing import Any

RUNTIME_STATE_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_gui_runtime_state(
    shell_model: Mapping[str, Any],
    *,
    diagnostics: Mapping[str, Any] | None = None,
    notifications: Mapping[str, Any] | None = None,
    footer: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    caps = _mapping(shell_model.get("capabilities"))
    diag = dict(diagnostics or {})
    note = dict(notifications or {})
    foot = dict(footer or {})
    return {
        "schema_version": RUNTIME_STATE_SCHEMA_VERSION,
        "kind": "gui_runtime_state",
        "active_page_id": shell_model.get("active_page_id"),
        "language": shell_model.get("language"),
        "theme": _mapping(shell_model.get("theme")).get("theme"),
        "navigation_count": len(_list(shell_model.get("navigation"))),
        "capabilities": dict(caps),
        "safe_mode": not bool(caps.get("executes_commands")),
        "diagnostics": diag,
        "notifications": note,
        "footer": foot,
        "ready": not bool(diag.get("blocking_count", 0)),
    }


def summarize_runtime_state(runtime_state: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "GUI runtime state",
            f"  Page: {runtime_state.get('active_page_id')}",
            f"  Language: {runtime_state.get('language')}",
            f"  Theme: {runtime_state.get('theme')}",
            f"  Safe mode: {runtime_state.get('safe_mode')}",
            f"  Ready: {runtime_state.get('ready')}",
        ]
    )


__all__ = ["RUNTIME_STATE_SCHEMA_VERSION", "build_gui_runtime_state", "summarize_runtime_state"]
