from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
from typing import Any

PENDING_CHANGES_SCHEMA_VERSION = "1.0"
_MUTATING_ACTIONS = {"rename_group", "accept_group", "reject_face", "include_face", "exclude_face", "split_group", "merge_group"}
_RISKY_ACTIONS = {"apply_ready_groups", "apply_review", "delete", "split_group", "merge_group"}


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _text(value: Any, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_pending_change(
    action_id: str,
    *,
    target_id: str | None = None,
    target_type: str = "group",
    payload: Mapping[str, Any] | None = None,
    status: str = "pending",
    source: str = "gui",
) -> dict[str, Any]:
    action = _text(action_id, "unknown")
    target = _text(target_id, "") or None
    change_id = f"{action}:{target_type}:{target or 'none'}"
    risk_level = "high" if action in _RISKY_ACTIONS else "medium" if action in _MUTATING_ACTIONS else "safe"
    return {
        "schema_version": PENDING_CHANGES_SCHEMA_VERSION,
        "change_id": change_id,
        "action_id": action,
        "target_id": target,
        "target_type": target_type,
        "payload": dict(payload or {}),
        "status": status,
        "source": source,
        "risk_level": risk_level,
        "requires_confirmation": risk_level == "high",
        "created_at_utc": _now_utc(),
        "executes_immediately": False,
    }


def normalize_pending_changes(changes: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in changes:
        change = _as_mapping(raw)
        action = _text(change.get("action_id"), "unknown")
        target_type = _text(change.get("target_type"), "group")
        target_id = change.get("target_id")
        payload = _as_mapping(change.get("payload"))
        item = build_pending_change(
            action,
            target_id=str(target_id) if target_id is not None else None,
            target_type=target_type,
            payload=payload,
            status=_text(change.get("status"), "pending"),
            source=_text(change.get("source"), "gui"),
        )
        if change.get("change_id"):
            item["change_id"] = str(change["change_id"])
        if item["change_id"] in seen:
            continue
        seen.add(str(item["change_id"]))
        normalized.append(item)
    return normalized


def summarize_pending_changes(changes: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    items = normalize_pending_changes(changes)
    by_action: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for item in items:
        by_action[str(item["action_id"])] = by_action.get(str(item["action_id"]), 0) + 1
        by_status[str(item["status"])] = by_status.get(str(item["status"]), 0) + 1
    return {
        "schema_version": PENDING_CHANGES_SCHEMA_VERSION,
        "change_count": len(items),
        "pending_count": sum(1 for item in items if item.get("status") == "pending"),
        "high_risk_count": sum(1 for item in items if item.get("risk_level") == "high"),
        "requires_confirmation_count": sum(1 for item in items if item.get("requires_confirmation")),
        "by_action": dict(sorted(by_action.items())),
        "by_status": dict(sorted(by_status.items())),
        "has_unsaved_changes": bool(items),
        "executes_immediately": False,
    }


__all__ = ["PENDING_CHANGES_SCHEMA_VERSION", "build_pending_change", "normalize_pending_changes", "summarize_pending_changes"]
