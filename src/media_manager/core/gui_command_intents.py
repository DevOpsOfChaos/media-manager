from __future__ import annotations

from collections.abc import Mapping
from typing import Any

COMMAND_INTENT_SCHEMA_VERSION = "1.0"

_SAFE_INTENTS = {
    "open_page",
    "open_file_ref",
    "show_dialog",
    "build_preview",
    "validate_bundle",
    "save_workflow",
}
_RISKY_INTENTS = {
    "apply_people_review",
    "apply_filesystem_plan",
}


def normalize_intent_id(value: str | None) -> str:
    return str(value or "").strip().lower().replace("_", "-")


def build_command_intent(
    intent_id: str,
    *,
    label: str,
    payload: Mapping[str, Any] | None = None,
    risk_level: str = "safe",
    requires_confirmation: bool | None = None,
) -> dict[str, object]:
    normalized = normalize_intent_id(intent_id)
    risky = risk_level in {"medium", "high", "destructive"} or normalized in _RISKY_INTENTS
    return {
        "schema_version": COMMAND_INTENT_SCHEMA_VERSION,
        "kind": "command_intent",
        "intent_id": normalized,
        "label": label,
        "payload": dict(payload or {}),
        "risk_level": risk_level,
        "requires_confirmation": bool(risky if requires_confirmation is None else requires_confirmation),
        "executes_immediately": False,
    }


def intent_from_action(action: Mapping[str, Any]) -> dict[str, object]:
    action_id = normalize_intent_id(str(action.get("id") or action.get("action_id") or ""))
    risk = str(action.get("risk_level") or "safe")
    label = str(action.get("label") or action_id.replace("-", " ").title())
    if action_id.startswith("open-") or action_id.startswith("select-"):
        intent_id = "open_page" if "page_id" in action else "open_file_ref"
    elif action_id.startswith("apply"):
        intent_id = "apply_people_review" if ("people" in action_id or "ready-groups" in action_id) else "apply_filesystem_plan"
    elif "validate" in action_id:
        intent_id = "validate_bundle"
    else:
        intent_id = "show_dialog" if risk in {"medium", "high", "destructive"} else "build_preview"
    return build_command_intent(
        intent_id,
        label=label,
        payload={"source_action": dict(action)},
        risk_level=risk,
        requires_confirmation=action.get("requires_confirmation") if isinstance(action.get("requires_confirmation"), bool) else None,
    )


def build_intent_queue(actions: list[Mapping[str, Any]]) -> dict[str, object]:
    intents = [intent_from_action(action) for action in actions if isinstance(action, Mapping)]
    return {
        "schema_version": COMMAND_INTENT_SCHEMA_VERSION,
        "kind": "command_intent_queue",
        "intent_count": len(intents),
        "confirmation_required_count": sum(1 for item in intents if item.get("requires_confirmation")),
        "intents": intents,
    }


__all__ = [
    "COMMAND_INTENT_SCHEMA_VERSION",
    "build_command_intent",
    "build_intent_queue",
    "intent_from_action",
    "normalize_intent_id",
]
