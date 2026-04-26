from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_i18n import translate

RUN_WIZARD_SCHEMA_VERSION = "1.0"
RUN_COMMANDS = ("organize", "rename", "duplicates", "cleanup", "people")


def build_run_wizard_model(*, language: str = "en", selected_command: str = "people", profile: Mapping[str, Any] | None = None) -> dict[str, object]:
    command = selected_command if selected_command in RUN_COMMANDS else "people"
    values = profile.get("values", {}) if isinstance(profile, Mapping) and isinstance(profile.get("values"), Mapping) else {}
    steps = [
        {"id": "choose_command", "title": "Choose workflow", "complete": bool(command)},
        {"id": "select_inputs", "title": "Select inputs", "complete": bool(values.get("source_dirs") or values.get("report_json"))},
        {"id": "preview", "title": translate("action.preview", language=language), "complete": False},
        {"id": "review", "title": translate("action.review", language=language), "complete": False},
        {"id": "apply", "title": translate("action.apply", language=language), "complete": False},
    ]
    return {
        "schema_version": RUN_WIZARD_SCHEMA_VERSION,
        "kind": "run_wizard",
        "selected_command": command,
        "available_commands": list(RUN_COMMANDS),
        "steps": steps,
        "current_step_id": next((step["id"] for step in steps if not step["complete"]), "choose_command"),
        "values": dict(values),
        "safe_defaults": {"preview_first": True, "requires_confirmation_for_apply": True},
    }


__all__ = ["RUN_COMMANDS", "RUN_WIZARD_SCHEMA_VERSION", "build_run_wizard_model"]
