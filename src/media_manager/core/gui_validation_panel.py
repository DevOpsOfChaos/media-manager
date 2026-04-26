from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

VALIDATION_PANEL_SCHEMA_VERSION = "1.0"


def build_validation_message(code: str, message: str, *, severity: str = "info", target: str | None = None) -> dict[str, object]:
    return {
        "schema_version": VALIDATION_PANEL_SCHEMA_VERSION,
        "code": code,
        "message": message,
        "severity": severity,
        "target": target,
    }


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _messages_from_page_model(*, page_id: str | None, page_model: Mapping[str, Any] | None) -> list[dict[str, object]]:
    payload = _as_mapping(page_model)
    target = page_id or str(payload.get("page_id") or "") or None
    messages: list[dict[str, object]] = []

    empty_state = payload.get("empty_state")
    if empty_state:
        messages.append(
            build_validation_message(
                "empty_state",
                str(empty_state),
                severity="info",
                target=target,
            )
        )

    overview = _as_mapping(payload.get("overview"))
    needs_name_count = overview.get("needs_name_group_count")
    if isinstance(needs_name_count, int) and needs_name_count > 0:
        messages.append(
            build_validation_message(
                "people_needs_name",
                f"{needs_name_count} groups need a name.",
                severity="warning",
                target=target,
            )
        )

    needs_review_count = overview.get("needs_review_group_count")
    if isinstance(needs_review_count, int) and needs_review_count > 0:
        messages.append(
            build_validation_message(
                "people_needs_review",
                f"{needs_review_count} groups still need review.",
                severity="info",
                target=target,
            )
        )

    if overview.get("groups_truncated") or payload.get("truncated"):
        messages.append(
            build_validation_message(
                "truncated",
                "Only a subset of entries is shown.",
                severity="warning",
                target=target,
            )
        )

    return messages


def build_validation_panel(
    messages: Iterable[Mapping[str, Any]] | None = None,
    *,
    page_id: str | None = None,
    page_model: Mapping[str, Any] | None = None,
    language: str | None = None,
) -> dict[str, object]:
    """Build a validation panel from explicit messages or a GUI page model.

    The original v1 API accepted only ``messages``. Newer page models call this
    helper with keyword arguments (``page_id`` and ``page_model``). Supporting
    both shapes keeps old tests/callers compatible while letting GUI pages attach
    validation metadata directly.
    """

    items = [dict(item) for item in messages] if messages is not None else []
    items.extend(_messages_from_page_model(page_id=page_id, page_model=page_model))
    return {
        "schema_version": VALIDATION_PANEL_SCHEMA_VERSION,
        "kind": "validation_panel",
        "page_id": page_id or (_as_mapping(page_model).get("page_id") if page_model is not None else None),
        "language": language,
        "messages": items,
        "message_count": len(items),
        "error_count": sum(1 for item in items if item.get("severity") == "error"),
        "warning_count": sum(1 for item in items if item.get("severity") == "warning"),
    }


def validation_panel_from_status(payload: Mapping[str, Any]) -> dict[str, object]:
    messages = []
    if payload.get("empty_state"):
        messages.append(build_validation_message("empty_state", str(payload.get("empty_state")), severity="info"))
    overview = payload.get("overview") if isinstance(payload.get("overview"), Mapping) else {}
    if overview.get("needs_name_group_count"):
        messages.append(build_validation_message("people_needs_name", f"{overview.get('needs_name_group_count')} groups need a name.", severity="warning"))
    if overview.get("groups_truncated"):
        messages.append(build_validation_message("truncated", "Only a subset of groups is shown.", severity="warning"))
    return build_validation_panel(messages)


__all__ = ["VALIDATION_PANEL_SCHEMA_VERSION", "build_validation_message", "build_validation_panel", "validation_panel_from_status"]
