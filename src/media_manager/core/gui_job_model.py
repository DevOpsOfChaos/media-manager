from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

JOB_MODEL_SCHEMA_VERSION = "1.0"
JOB_STATUSES = ("draft", "queued", "running", "completed", "failed", "cancelled", "blocked")
RISK_LEVELS = ("safe", "low", "medium", "high", "destructive")


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _slug(value: str) -> str:
    text = "".join(ch.lower() if ch.isalnum() else "-" for ch in str(value).strip())
    while "--" in text:
        text = text.replace("--", "-")
    return text.strip("-") or "job"


def normalize_job_status(status: object) -> str:
    value = str(status or "draft").strip().lower().replace("_", "-")
    return value if value in JOB_STATUSES else "draft"


def normalize_risk_level(risk_level: object) -> str:
    value = str(risk_level or "safe").strip().lower().replace("_", "-")
    return value if value in RISK_LEVELS else "safe"


def build_gui_job(
    *,
    action_id: str,
    command_argv: Sequence[object] = (),
    title: str | None = None,
    risk_level: str = "safe",
    requires_confirmation: bool = False,
    status: str = "draft",
    source: str = "gui",
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    action = str(action_id or "job").strip() or "job"
    normalized_risk = normalize_risk_level(risk_level)
    argv = [str(item) for item in command_argv if item is not None]
    job_id = f"job-{_slug(action)}-{abs(hash(tuple(argv))) % 100000:05d}"
    return {
        "schema_version": JOB_MODEL_SCHEMA_VERSION,
        "job_id": job_id,
        "action_id": action,
        "title": title or action.replace("_", " ").replace("-", " ").title(),
        "source": source,
        "status": normalize_job_status(status),
        "risk_level": normalized_risk,
        "requires_confirmation": bool(requires_confirmation or normalized_risk in {"high", "destructive"}),
        "command_argv": argv,
        "created_at_utc": _now_utc(),
        "updated_at_utc": _now_utc(),
        "metadata": dict(metadata or {}),
        "executes_immediately": False,
    }


def transition_gui_job(job: Mapping[str, Any], status: str, *, message: str | None = None) -> dict[str, object]:
    payload = dict(job)
    payload["status"] = normalize_job_status(status)
    payload["updated_at_utc"] = _now_utc()
    if message:
        payload["message"] = message
    return payload


def summarize_jobs(jobs: Sequence[Mapping[str, Any]]) -> dict[str, object]:
    status_summary: dict[str, int] = {}
    risk_summary: dict[str, int] = {}
    for job in jobs:
        status = normalize_job_status(job.get("status"))
        risk = normalize_risk_level(job.get("risk_level"))
        status_summary[status] = status_summary.get(status, 0) + 1
        risk_summary[risk] = risk_summary.get(risk, 0) + 1
    return {
        "schema_version": JOB_MODEL_SCHEMA_VERSION,
        "job_count": len(jobs),
        "status_summary": dict(sorted(status_summary.items())),
        "risk_summary": dict(sorted(risk_summary.items())),
        "blocked_count": status_summary.get("blocked", 0),
        "running_count": status_summary.get("running", 0),
        "requires_confirmation_count": sum(1 for item in jobs if bool(item.get("requires_confirmation"))),
    }


__all__ = [
    "JOB_MODEL_SCHEMA_VERSION",
    "JOB_STATUSES",
    "RISK_LEVELS",
    "build_gui_job",
    "normalize_job_status",
    "normalize_risk_level",
    "summarize_jobs",
    "transition_gui_job",
]
