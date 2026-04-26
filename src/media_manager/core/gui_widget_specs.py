from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

WIDGET_SPEC_SCHEMA_VERSION = "1.0"

_ALLOWED_WIDGETS = {
    "action_bar",
    "badge",
    "button",
    "card",
    "card_grid",
    "empty_state",
    "face_card",
    "footer",
    "hero",
    "image",
    "list",
    "metric",
    "navigation",
    "panel",
    "search",
    "section",
    "table",
    "text",
    "timeline",
}


def _text(value: object, default: str = "") -> str:
    return value if isinstance(value, str) and value else default


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def normalize_widget_type(widget_type: str | None) -> str:
    value = str(widget_type or "section").strip().lower().replace("-", "_")
    return value if value in _ALLOWED_WIDGETS else "section"


def build_widget_spec(
    widget_id: str,
    widget_type: str,
    *,
    title: str = "",
    props: Mapping[str, Any] | None = None,
    children: Iterable[Mapping[str, Any]] = (),
    slots: Mapping[str, Any] | None = None,
    visible: bool = True,
    enabled: bool = True,
) -> dict[str, object]:
    return {
        "schema_version": WIDGET_SPEC_SCHEMA_VERSION,
        "widget_id": _text(widget_id, "widget"),
        "widget_type": normalize_widget_type(widget_type),
        "title": title,
        "props": dict(props or {}),
        "children": [dict(item) for item in children if isinstance(item, Mapping)],
        "slots": dict(slots or {}),
        "visible": bool(visible),
        "enabled": bool(enabled),
    }


def build_text_spec(widget_id: str, text: str, *, role: str = "body") -> dict[str, object]:
    return build_widget_spec(widget_id, "text", props={"text": text, "role": role})


def build_button_spec(
    button_id: str,
    label: str,
    *,
    variant: str = "secondary",
    action_id: str | None = None,
    enabled: bool = True,
    requires_confirmation: bool = False,
) -> dict[str, object]:
    return build_widget_spec(
        button_id,
        "button",
        title=label,
        props={
            "label": label,
            "variant": variant,
            "action_id": action_id or button_id,
            "requires_confirmation": bool(requires_confirmation),
        },
        enabled=enabled,
    )


def build_card_spec(
    card_id: str,
    title: str,
    *,
    subtitle: str = "",
    metrics: Mapping[str, Any] | None = None,
    actions: Iterable[Mapping[str, Any]] = (),
) -> dict[str, object]:
    return build_widget_spec(
        card_id,
        "card",
        title=title,
        props={"subtitle": subtitle, "metrics": dict(metrics or {})},
        children=[dict(action) for action in actions if isinstance(action, Mapping)],
    )


def build_table_spec(
    table_id: str,
    *,
    columns: Iterable[str],
    rows: Iterable[Mapping[str, Any]],
    empty_state: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    column_list = [str(item) for item in columns]
    row_list = [dict(item) for item in rows if isinstance(item, Mapping)]
    return build_widget_spec(
        table_id,
        "table",
        title=table_id.replace("-", " ").title(),
        props={
            "columns": column_list,
            "rows": row_list,
            "row_count": len(row_list),
            "empty_state": dict(empty_state or {}),
        },
    )


def build_face_card_spec(face: Mapping[str, Any], *, selected: bool = False) -> dict[str, object]:
    face_id = _text(face.get("face_id"), "face")
    return build_widget_spec(
        face_id,
        "face_card",
        title=_text(face.get("display_label") or face.get("path"), face_id),
        props={
            "face_id": face_id,
            "asset_ref": dict(_mapping(face.get("asset_ref"))),
            "status": face.get("status") or face.get("decision_status"),
            "selected": bool(selected),
            "include": face.get("include"),
            "path": face.get("path"),
        },
    )


def summarize_widget_tree(root: Mapping[str, Any]) -> dict[str, object]:
    stack = [root]
    counts: dict[str, int] = {}
    visible_count = 0
    disabled_count = 0
    while stack:
        item = stack.pop()
        if not isinstance(item, Mapping):
            continue
        widget_type = _text(item.get("widget_type"), "unknown")
        counts[widget_type] = counts.get(widget_type, 0) + 1
        visible_count += 1 if item.get("visible", True) else 0
        disabled_count += 1 if item.get("enabled", True) is False else 0
        stack.extend(reversed(_list(item.get("children"))))
        for slot_value in _mapping(item.get("slots")).values():
            if isinstance(slot_value, Mapping):
                stack.append(slot_value)
            elif isinstance(slot_value, list):
                stack.extend(item for item in reversed(slot_value) if isinstance(item, Mapping))
    return {
        "schema_version": WIDGET_SPEC_SCHEMA_VERSION,
        "widget_count": sum(counts.values()),
        "visible_count": visible_count,
        "disabled_count": disabled_count,
        "type_summary": dict(sorted(counts.items())),
    }


__all__ = [
    "WIDGET_SPEC_SCHEMA_VERSION",
    "build_button_spec",
    "build_card_spec",
    "build_face_card_spec",
    "build_table_spec",
    "build_text_spec",
    "build_widget_spec",
    "normalize_widget_type",
    "summarize_widget_tree",
]
