from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
from typing import Any

ACTION_RESULT_SCHEMA_VERSION = "1.0"


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_qt_action_result(
    action_id: str,
    *,
    status: str = "accepted",
    message: str = "",
    intent: Mapping[str, Any] | None = None,
    page_id: str | None = None,
    problems: Iterable[str] = (),
    warnings: Iterable[str] = (),
) -> dict[str, object]:
    normalized_status = str(status or "accepted").strip().lower()
    if normalized_status not in {"accepted", "blocked", "queued", "ignored", "failed"}:
        normalized_status = "accepted"
    problem_list = [str(item) for item in problems if str(item).strip()]
    warning_list = [str(item) for item in warnings if str(item).strip()]
    notification_level = "error" if normalized_status in {"blocked", "failed"} else "warning" if warning_list else "success" if normalized_status == "accepted" else "info"
    return {
        "schema_version": ACTION_RESULT_SCHEMA_VERSION,
        "kind": "qt_action_result",
        "generated_at_utc": _now_utc(),
        "action_id": str(action_id or "action"),
        "status": normalized_status,
        "message": message or _default_message(normalized_status),
        "page_id": page_id,
        "intent": dict(intent or {}),
        "problem_count": len(problem_list),
        "warning_count": len(warning_list),
        "problems": problem_list,
        "warnings": warning_list,
        "notification": {
            "level": notification_level,
            "title": str(action_id or "Action"),
            "message": message or _default_message(normalized_status),
        },
    }


def _default_message(status: str) -> str:
    return {
        "accepted": "Action accepted for the GUI state model.",
        "blocked": "Action is blocked and was not executed.",
        "queued": "Action was queued for review.",
        "ignored": "Action was ignored.",
        "failed": "Action failed while building the GUI state model.",
    }.get(status, "Action processed.")


def summarize_qt_action_results(results: Iterable[Mapping[str, Any]]) -> dict[str, object]:
    items = [dict(item) for item in results]
    by_status: dict[str, int] = {}
    for item in items:
        status = str(item.get("status") or "unknown")
        by_status[status] = by_status.get(status, 0) + 1
    return {
        "schema_version": ACTION_RESULT_SCHEMA_VERSION,
        "kind": "qt_action_result_summary",
        "result_count": len(items),
        "status_summary": dict(sorted(by_status.items())),
        "blocked_count": by_status.get("blocked", 0) + by_status.get("failed", 0),
        "warning_count": sum(int(item.get("warning_count") or 0) for item in items),
    }


__all__ = ["ACTION_RESULT_SCHEMA_VERSION", "build_qt_action_result", "summarize_qt_action_results"]
