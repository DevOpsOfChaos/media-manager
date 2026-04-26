from __future__ import annotations

from collections.abc import Mapping
from typing import Any

ACCESSIBILITY_SCHEMA_VERSION = "1.0"

_DEFAULT_SHORTCUTS = [
    {"id": "command_palette", "keys": ["Ctrl", "K"], "action": "open_command_palette"},
    {"id": "dashboard", "keys": ["Ctrl", "1"], "action": "navigate_dashboard"},
    {"id": "people_review", "keys": ["Ctrl", "2"], "action": "navigate_people_review"},
    {"id": "run_history", "keys": ["Ctrl", "3"], "action": "navigate_run_history"},
    {"id": "profiles", "keys": ["Ctrl", "4"], "action": "navigate_profiles"},
    {"id": "settings", "keys": ["Ctrl", ","], "action": "navigate_settings"},
]


def build_accessibility_contract(*, language: str = "en", high_contrast: bool = False) -> dict[str, object]:
    return {
        "schema_version": ACCESSIBILITY_SCHEMA_VERSION,
        "language": language,
        "high_contrast": bool(high_contrast),
        "keyboard_first": True,
        "screen_reader_labels": True,
        "shortcuts": [dict(item) for item in _DEFAULT_SHORTCUTS],
        "focus_order": ["sidebar", "command_palette", "page_header", "primary_content", "details_panel", "status_bar"],
    }


def annotate_for_accessibility(component: Mapping[str, Any], *, role: str, label: str | None = None) -> dict[str, object]:
    payload = dict(component)
    payload["accessibility"] = {
        "role": role,
        "label": label or str(component.get("title") or component.get("label") or component.get("id") or role),
    }
    return payload


__all__ = ["ACCESSIBILITY_SCHEMA_VERSION", "annotate_for_accessibility", "build_accessibility_contract"]
