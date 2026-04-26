from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_i18n import translate
from .gui_modern_components import build_action_button

PROFILE_EDITOR_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_profile_form_schema(*, command: str = "organize", language: str = "en") -> dict[str, object]:
    normalized = str(command or "organize").strip().lower()
    common_fields = [
        {"id": "title", "label": translate("profile.field.title", language=language), "type": "text", "required": True},
        {"id": "source_dirs", "label": translate("profile.field.sources", language=language), "type": "path_list", "required": normalized in {"organize", "rename", "duplicates", "cleanup", "people"}},
        {"id": "run_dir", "label": translate("profile.field.run_dir", language=language), "type": "path", "required": False},
    ]
    command_fields = {
        "organize": [{"id": "target_root", "label": translate("profile.field.target", language=language), "type": "path", "required": True}],
        "cleanup": [{"id": "target_root", "label": translate("profile.field.target", language=language), "type": "path", "required": True}],
        "people": [
            {"id": "catalog", "label": translate("profile.field.catalog", language=language), "type": "path", "required": False},
            {"id": "backend", "label": "Backend", "type": "choice", "choices": ["auto", "dlib", "opencv"], "required": False},
            {"id": "include_encodings", "label": translate("profile.field.include_encodings", language=language), "type": "boolean", "required": False, "privacy_sensitive": True},
        ],
    }
    return {
        "schema_version": PROFILE_EDITOR_SCHEMA_VERSION,
        "kind": "profile_form_schema",
        "command": normalized,
        "fields": [*common_fields, *command_fields.get(normalized, [])],
        "primary_action": build_action_button("save_profile", translate("action.save", language=language), variant="primary", icon="save"),
    }


def build_profile_list_state(home_state: Mapping[str, Any], *, language: str = "en") -> dict[str, object]:
    profiles = _mapping(home_state.get("profiles"))
    items = [dict(item) for item in _list(profiles.get("items")) if isinstance(item, Mapping)]
    return {
        "schema_version": PROFILE_EDITOR_SCHEMA_VERSION,
        "kind": "profile_list_state",
        "items": items,
        "item_count": len(items),
        "form_schemas": {command: build_profile_form_schema(command=command, language=language) for command in ("organize", "duplicates", "people", "doctor")},
    }


__all__ = ["PROFILE_EDITOR_SCHEMA_VERSION", "build_profile_form_schema", "build_profile_list_state"]
