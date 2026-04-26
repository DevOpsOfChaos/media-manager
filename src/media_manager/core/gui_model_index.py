from __future__ import annotations

from collections.abc import Mapping
from typing import Any

MODEL_INDEX_SCHEMA_VERSION = "1.0"


def build_gui_model_index(models: Mapping[str, Mapping[str, Any]]) -> dict[str, object]:
    entries = []
    for name, model in sorted(models.items()):
        entries.append({
            "name": name,
            "kind": model.get("kind"),
            "schema_version": model.get("schema_version"),
            "keys": sorted(str(key) for key in model.keys()),
        })
    return {
        "schema_version": MODEL_INDEX_SCHEMA_VERSION,
        "kind": "gui_model_index",
        "model_count": len(entries),
        "entries": entries,
    }


def summarize_gui_model_index(index: Mapping[str, Any]) -> str:
    return f"{index.get('model_count', 0)} GUI models indexed"


__all__ = ["MODEL_INDEX_SCHEMA_VERSION", "build_gui_model_index", "summarize_gui_model_index"]
