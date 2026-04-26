from __future__ import annotations

from collections.abc import Mapping
from typing import Any

DEVTOOLS_SCHEMA_VERSION = "1.0"


def _type_name(value: object) -> str:
    if isinstance(value, Mapping):
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if value is None:
        return "null"
    return "string"


def build_model_schema_summary(model: Mapping[str, Any], *, model_name: str = "model") -> dict[str, object]:
    fields = []
    for key, value in sorted(model.items(), key=lambda item: str(item[0])):
        fields.append(
            {
                "name": str(key),
                "type": _type_name(value),
                "present": True,
                "nested_count": len(value) if isinstance(value, (Mapping, list)) else 0,
            }
        )
    return {
        "schema_version": DEVTOOLS_SCHEMA_VERSION,
        "kind": "model_schema_summary",
        "model_name": model_name,
        "field_count": len(fields),
        "fields": fields,
    }


def build_devtools_panel(models: Mapping[str, Mapping[str, Any]]) -> dict[str, object]:
    summaries = [build_model_schema_summary(model, model_name=name) for name, model in sorted(models.items())]
    return {
        "schema_version": DEVTOOLS_SCHEMA_VERSION,
        "kind": "devtools_panel",
        "model_count": len(summaries),
        "summaries": summaries,
        "exportable": True,
    }


__all__ = ["DEVTOOLS_SCHEMA_VERSION", "build_devtools_panel", "build_model_schema_summary"]
