from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SIGNAL_MAP_SCHEMA_VERSION = "1.0"

def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}

def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []

def _text(value: object, fallback: str = "") -> str:
    return str(value) if value is not None else fallback

def build_signal_binding(widget_id: str, signal: str, intent: Mapping[str, Any], *, requires_confirmation: bool = False) -> dict[str, object]:
    return {
        "widget_id": str(widget_id),
        "signal": str(signal),
        "intent": dict(intent),
        "requires_confirmation": bool(requires_confirmation),
        "executes_immediately": False,
    }

def build_qt_signal_map(blueprint: Mapping[str, Any]) -> dict[str, object]:
    bindings: list[dict[str, object]] = []
    root = _mapping(blueprint.get("root"))

    def walk(node: Mapping[str, Any]) -> None:
        props = _mapping(node.get("props"))
        widget_id = _text(node.get("widget_id"))
        target_page = props.get("target_page_id")
        if target_page:
            bindings.append(
                build_signal_binding(
                    widget_id,
                    "clicked",
                    {"intent_type": "navigate", "page_id": str(target_page)},
                )
            )
        if props.get("component") == "metric_card" and props.get("title"):
            bindings.append(
                build_signal_binding(
                    widget_id,
                    "activated",
                    {"intent_type": "open_detail", "title": str(props.get("title"))},
                )
            )
        for raw_child in _list(node.get("children")):
            if isinstance(raw_child, Mapping):
                walk(raw_child)

    walk(root)
    summary = {
        "binding_count": len(bindings),
        "confirmation_count": sum(1 for item in bindings if item.get("requires_confirmation")),
    }
    return {
        "schema_version": SIGNAL_MAP_SCHEMA_VERSION,
        "kind": "qt_signal_map",
        "bindings": bindings,
        "summary": summary,
    }

def validate_signal_map(signal_map: Mapping[str, Any]) -> dict[str, object]:
    problems: list[str] = []
    for index, raw in enumerate(_list(signal_map.get("bindings"))):
        item = _mapping(raw)
        if not item.get("widget_id"):
            problems.append(f"binding[{index}] missing widget_id")
        if item.get("executes_immediately") is not False:
            problems.append(f"binding[{index}] must not execute immediately")
    return {"valid": not problems, "problems": problems, "problem_count": len(problems)}

__all__ = ["SIGNAL_MAP_SCHEMA_VERSION", "build_qt_signal_map", "build_signal_binding", "validate_signal_map"]
