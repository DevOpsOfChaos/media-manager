from __future__ import annotations

from collections.abc import Mapping
from typing import Any

FORM_PLAN_SCHEMA_VERSION = "1.0"


def build_qt_form_field(field_id: str, label: str, *, value: Any = None, field_type: str = "text", required: bool = False, sensitive: bool = False) -> dict[str, object]:
    return {"id": field_id, "label": label, "type": field_type, "value": value, "required": required, "sensitive": sensitive, "valid": (value not in (None, "") if required else True)}


def build_qt_form_plan(form_id: str, fields: list[Mapping[str, Any]] | None = None, *, title: str = "Form") -> dict[str, object]:
    normalized = []
    for item in fields or []:
        normalized.append(build_qt_form_field(
            str(item.get("id") or item.get("name") or "field"),
            str(item.get("label") or item.get("id") or "Field"),
            value=item.get("value"),
            field_type=str(item.get("type") or "text"),
            required=bool(item.get("required", False)),
            sensitive=bool(item.get("sensitive", False)),
        ))
    return {
        "schema_version": FORM_PLAN_SCHEMA_VERSION,
        "form_id": form_id,
        "title": title,
        "field_count": len(normalized),
        "required_count": sum(1 for field in normalized if field["required"]),
        "valid": all(bool(field["valid"]) for field in normalized),
        "fields": normalized,
    }


__all__ = ["FORM_PLAN_SCHEMA_VERSION", "build_qt_form_field", "build_qt_form_plan"]
