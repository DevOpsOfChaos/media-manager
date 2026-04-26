from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

SHORTCUT_SCHEMA_VERSION = "1.0"

_DEFAULT_SHORTCUTS = [
    ("open_command_palette", "Ctrl+K", "global", "Open command palette"),
    ("go_dashboard", "Ctrl+1", "navigation", "Open dashboard"),
    ("go_people_review", "Ctrl+2", "navigation", "Open people review"),
    ("go_run_history", "Ctrl+3", "navigation", "Open run history"),
    ("go_profiles", "Ctrl+4", "navigation", "Open profiles"),
    ("save_review_state", "Ctrl+S", "review", "Save current review state"),
    ("reject_face", "Del", "review", "Reject selected face"),
    ("accept_group", "Ctrl+Enter", "review", "Accept selected group"),
    ("toggle_help", "F1", "global", "Show help"),
]


def _shortcut(action_id: str, keys: str, scope: str, label: str) -> dict[str, object]:
    return {"action_id": action_id, "keys": keys, "scope": scope, "label": label, "enabled": True}


def build_keyboard_shortcuts(extra_shortcuts: Iterable[Mapping[str, Any]] = ()) -> dict[str, object]:
    shortcuts = [_shortcut(*item) for item in _DEFAULT_SHORTCUTS]
    for raw in extra_shortcuts:
        if isinstance(raw, Mapping):
            action_id = str(raw.get("action_id") or "").strip()
            keys = str(raw.get("keys") or "").strip()
            if action_id and keys:
                shortcuts.append({
                    "action_id": action_id,
                    "keys": keys,
                    "scope": str(raw.get("scope") or "custom"),
                    "label": str(raw.get("label") or action_id),
                    "enabled": bool(raw.get("enabled", True)),
                })
    conflicts = detect_shortcut_conflicts(shortcuts)
    return {
        "schema_version": SHORTCUT_SCHEMA_VERSION,
        "kind": "keyboard_shortcuts",
        "shortcut_count": len(shortcuts),
        "conflict_count": len(conflicts),
        "shortcuts": shortcuts,
        "conflicts": conflicts,
    }


def detect_shortcut_conflicts(shortcuts: Iterable[Mapping[str, Any]]) -> list[dict[str, object]]:
    by_key_scope: dict[tuple[str, str], list[str]] = {}
    for shortcut in shortcuts:
        keys = str(shortcut.get("keys") or "").casefold()
        scope = str(shortcut.get("scope") or "global").casefold()
        action_id = str(shortcut.get("action_id") or "")
        if keys and action_id:
            by_key_scope.setdefault((keys, scope), []).append(action_id)
    return [
        {"keys": keys, "scope": scope, "action_ids": action_ids}
        for (keys, scope), action_ids in sorted(by_key_scope.items())
        if len(action_ids) > 1
    ]


__all__ = ["SHORTCUT_SCHEMA_VERSION", "build_keyboard_shortcuts", "detect_shortcut_conflicts"]
