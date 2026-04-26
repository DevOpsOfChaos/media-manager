from __future__ import annotations

from collections.abc import Mapping
from typing import Any

MODEL_HEALTH_SCHEMA_VERSION = "1.0"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _message(code: str, message: str, *, severity: str = "info", target: str | None = None) -> dict[str, object]:
    payload: dict[str, object] = {"code": code, "message": message, "severity": severity}
    if target:
        payload["target"] = target
    return payload


def validate_page_model_contract(page_model: Mapping[str, Any]) -> dict[str, object]:
    messages: list[dict[str, object]] = []
    page_id = page_model.get("page_id")
    if not page_id:
        messages.append(_message("missing_page_id", "Page model has no page_id.", severity="error"))
    if not page_model.get("kind"):
        messages.append(_message("missing_kind", "Page model has no kind.", severity="error"))
    if not page_model.get("layout"):
        messages.append(_message("missing_layout", "Page model has no layout.", severity="warning"))
    if page_id == "people-review":
        if "editor" not in page_model:
            messages.append(_message("missing_people_editor", "People review page has no legacy editor model.", severity="error"))
        if "queue" not in page_model:
            messages.append(_message("missing_people_queue", "People review page has no queue model.", severity="error"))
    return _build_health_result("page_model_health", messages)


def validate_shell_model_contract(shell_model: Mapping[str, Any]) -> dict[str, object]:
    messages: list[dict[str, object]] = []
    if not shell_model.get("active_page_id"):
        messages.append(_message("missing_active_page", "Shell model has no active page.", severity="error"))
    if not _as_list(shell_model.get("navigation")):
        messages.append(_message("missing_navigation", "Shell model has no navigation items.", severity="error"))
    page = _as_mapping(shell_model.get("page"))
    page_health = validate_page_model_contract(page)
    for raw in _as_list(page_health.get("messages")):
        if isinstance(raw, Mapping):
            messages.append({**dict(raw), "target": "page"})
    return _build_health_result("shell_model_health", messages)


def _build_health_result(kind: str, messages: list[dict[str, object]]) -> dict[str, object]:
    return {
        "schema_version": MODEL_HEALTH_SCHEMA_VERSION,
        "kind": kind,
        "healthy": not any(item.get("severity") == "error" for item in messages),
        "message_count": len(messages),
        "error_count": sum(1 for item in messages if item.get("severity") == "error"),
        "warning_count": sum(1 for item in messages if item.get("severity") == "warning"),
        "messages": messages,
    }


__all__ = [
    "MODEL_HEALTH_SCHEMA_VERSION",
    "validate_page_model_contract",
    "validate_shell_model_contract",
]
