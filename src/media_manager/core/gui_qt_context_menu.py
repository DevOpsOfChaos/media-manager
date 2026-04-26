from __future__ import annotations

from collections.abc import Mapping
from typing import Any

CONTEXT_MENU_SCHEMA_VERSION = "1.0"


def _text(value: Any, fallback: str = "") -> str:
    return str(value).strip() if value is not None and str(value).strip() else fallback


def _item(item_id: str, label: str, *, intent: Mapping[str, Any], enabled: bool = True, risk_level: str = "safe", requires_confirmation: bool = False) -> dict[str, object]:
    return {
        "id": item_id,
        "label": label,
        "enabled": enabled,
        "risk_level": risk_level,
        "requires_confirmation": requires_confirmation or risk_level in {"high", "danger", "destructive"},
        "intent": dict(intent),
        "executes_immediately": False,
    }


def build_qt_context_menu(target_kind: str, target: Mapping[str, Any] | None = None, *, language: str = "en") -> dict[str, object]:
    target = target or {}
    label_prefix = "Öffnen" if language == "de" else "Open"
    items: list[dict[str, object]]
    if target_kind == "people_group":
        group_id = _text(target.get("group_id"), "<group>")
        items = [
            _item("select_group", "Gruppe auswählen" if language == "de" else "Select group", intent={"type": "select_group", "group_id": group_id}),
            _item("rename_group", "Umbenennen" if language == "de" else "Rename", intent={"type": "rename_group", "group_id": group_id}),
            _item("mark_ready", "Als bereit markieren" if language == "de" else "Mark ready", intent={"type": "mark_group_ready", "group_id": group_id}, requires_confirmation=True),
        ]
    elif target_kind == "face_card":
        face_id = _text(target.get("face_id"), "<face>")
        items = [
            _item("select_face", "Gesicht auswählen" if language == "de" else "Select face", intent={"type": "select_face", "face_id": face_id}),
            _item("reject_face", "Nicht diese Person" if language == "de" else "Not this person", intent={"type": "reject_face", "face_id": face_id}, risk_level="medium", requires_confirmation=True),
        ]
    elif target_kind == "run_card":
        run_id = _text(target.get("run_id"), "<run>")
        items = [
            _item("open_run", f"{label_prefix} run", intent={"type": "navigate", "page_id": "run-history", "run_id": run_id}),
            _item("validate_run", "Validate run", intent={"type": "validate_run", "run_id": run_id}),
        ]
    else:
        items = [_item("inspect", "Inspect", intent={"type": "inspect", "target_kind": target_kind})]
    return {
        "schema_version": CONTEXT_MENU_SCHEMA_VERSION,
        "kind": "qt_context_menu",
        "target_kind": target_kind,
        "target_id": target.get("id") or target.get("group_id") or target.get("face_id") or target.get("run_id"),
        "items": items,
        "item_count": len(items),
        "confirmation_count": sum(1 for item in items if item["requires_confirmation"]),
        "executes_immediately": False,
    }


__all__ = ["CONTEXT_MENU_SCHEMA_VERSION", "build_qt_context_menu"]
