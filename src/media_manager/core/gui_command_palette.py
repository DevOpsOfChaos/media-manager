from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_i18n import translate

COMMAND_PALETTE_SCHEMA_VERSION = "1.0"


def _command(command_id: str, *, label_key: str, page_id: str, shortcut: str = "", enabled: bool = True, language: str = "en") -> dict[str, object]:
    return {
        "id": command_id,
        "label": translate(label_key, language=language),
        "page_id": page_id,
        "shortcut": shortcut,
        "enabled": enabled,
        "executes_filesystem_changes": False,
    }


def build_command_palette(*, language: str = "en", home_state: Mapping[str, Any] | None = None) -> dict[str, object]:
    people_ready = bool(((home_state or {}).get("people_review") or {}) if isinstance((home_state or {}).get("people_review"), Mapping) else False)
    commands = [
        _command("open_people_review", label_key="command.open_people_review", page_id="people-review", shortcut="Ctrl+P", enabled=people_ready, language=language),
        _command("new_people_scan", label_key="command.new_people_scan", page_id="new-run", shortcut="Ctrl+N", language=language),
        _command("open_profiles", label_key="command.open_profiles", page_id="profiles", shortcut="Ctrl+Shift+P", language=language),
        _command("open_runs", label_key="command.open_runs", page_id="run-history", shortcut="Ctrl+R", language=language),
    ]
    return {
        "schema_version": COMMAND_PALETTE_SCHEMA_VERSION,
        "title": translate("command_palette.title", language=language),
        "commands": commands,
        "enabled_count": sum(1 for item in commands if item.get("enabled")),
    }


__all__ = ["COMMAND_PALETTE_SCHEMA_VERSION", "build_command_palette"]
