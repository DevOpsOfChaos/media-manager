from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_action_result import build_qt_action_result
from .gui_qt_navigation_intents import navigation_intent_from_action, normalize_qt_page_id
from .gui_qt_page_state_summary import build_qt_shell_state_summary
from .gui_qt_reload_coordinator import build_qt_reload_plan
from .gui_qt_toolbar_actions import build_qt_toolbar_actions
from .gui_qt_ui_contract_validator import validate_qt_shell_contract

VIEW_ORCHESTRATOR_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_qt_view_orchestration_state(shell_model: Mapping[str, Any]) -> dict[str, object]:
    page = _mapping(shell_model.get("page"))
    active_page_id = normalize_qt_page_id(shell_model.get("active_page_id") or page.get("page_id") or "dashboard")
    toolbar = build_qt_toolbar_actions(page, language=str(shell_model.get("language") or "en"))
    validation = validate_qt_shell_contract(shell_model)
    return {
        "schema_version": VIEW_ORCHESTRATOR_SCHEMA_VERSION,
        "kind": "qt_view_orchestration_state",
        "active_page_id": active_page_id,
        "summary": build_qt_shell_state_summary(shell_model),
        "toolbar": toolbar,
        "validation": validation,
        "ready": bool(validation.get("valid")),
        "executes_commands": False,
    }


def plan_qt_view_action(shell_model: Mapping[str, Any], action: Mapping[str, Any]) -> dict[str, object]:
    active_page_id = normalize_qt_page_id(shell_model.get("active_page_id") or "dashboard")
    intent = navigation_intent_from_action(action, current_page_id=active_page_id)
    status = "blocked" if intent.get("kind") == "qt_unknown_intent" else "accepted"
    changes = []
    if intent.get("action") == "navigate":
        changes.append("page")
    elif intent.get("action") == "reload_page":
        changes.append("page")
    elif intent.get("action") in {"back", "forward"}:
        changes.append("page")
    reload_plan = build_qt_reload_plan(changes, active_page_id=str(intent.get("target_page_id") or active_page_id))
    result = build_qt_action_result(str(action.get("id") or intent.get("intent_id") or "action"), status=status, intent=intent, page_id=active_page_id)
    return {
        "schema_version": VIEW_ORCHESTRATOR_SCHEMA_VERSION,
        "kind": "qt_view_action_plan",
        "active_page_id": active_page_id,
        "intent": intent,
        "reload_plan": reload_plan,
        "result": result,
        "executes_immediately": False,
        "requires_confirmation": bool(action.get("requires_confirmation")),
    }


def apply_qt_view_action_to_model(shell_model: Mapping[str, Any], action: Mapping[str, Any]) -> dict[str, object]:
    """Return an updated shell-model-like payload without mutating the input.

    This function updates only cheap visible state fields. It intentionally does not
    rebuild page models or execute commands; the real GUI can use the returned reload
    plan to decide what to rebuild.
    """
    plan = plan_qt_view_action(shell_model, action)
    intent = _mapping(plan.get("intent"))
    payload = dict(shell_model)
    if intent.get("action") == "navigate" and intent.get("target_page_id"):
        target = normalize_qt_page_id(intent.get("target_page_id"))
        payload["active_page_id"] = target
        nav = []
        for raw in _list(shell_model.get("navigation")):
            item = dict(_mapping(raw))
            item["active"] = item.get("id") == target
            nav.append(item)
        payload["navigation"] = nav
    payload["last_action_plan"] = plan
    payload["executes_commands"] = False
    return payload


__all__ = [
    "VIEW_ORCHESTRATOR_SCHEMA_VERSION",
    "apply_qt_view_action_to_model",
    "build_qt_view_orchestration_state",
    "plan_qt_view_action",
]
