from __future__ import annotations

from typing import Any, Mapping

CANCELLATION_SCHEMA_VERSION = "1.0"
CANCELLABLE_STATUSES = {"queued", "running"}


def build_cancellation_request(job: Mapping[str, Any], *, reason: str = "user_requested") -> dict[str, object]:
    status = str(job.get("status") or "")
    can_cancel = status in CANCELLABLE_STATUSES
    return {
        "schema_version": CANCELLATION_SCHEMA_VERSION,
        "kind": "gui_cancellation_request",
        "job_id": job.get("job_id"),
        "current_status": status,
        "reason": reason,
        "can_cancel": can_cancel,
        "requires_confirmation": status == "running",
        "executes_immediately": False,
        "blocked_reason": None if can_cancel else "job_is_not_cancellable",
    }


def apply_cancellation_marker(job: Mapping[str, Any], *, reason: str = "user_requested") -> dict[str, object]:
    request = build_cancellation_request(job, reason=reason)
    payload = dict(job)
    if request["can_cancel"]:
        payload["status"] = "cancelled"
        payload["cancel_reason"] = reason
    return payload


__all__ = ["CANCELLABLE_STATUSES", "CANCELLATION_SCHEMA_VERSION", "apply_cancellation_marker", "build_cancellation_request"]
