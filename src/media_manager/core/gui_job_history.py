from __future__ import annotations

from typing import Any, Mapping, Sequence

from .gui_job_model import summarize_jobs

JOB_HISTORY_SCHEMA_VERSION = "1.0"
TERMINAL_STATUSES = {"completed", "failed", "cancelled", "blocked"}


def build_job_history(jobs: Sequence[Mapping[str, Any]] = (), *, limit: int | None = None) -> dict[str, object]:
    values = [dict(item) for item in jobs]
    values.sort(key=lambda item: str(item.get("updated_at_utc") or item.get("created_at_utc") or ""), reverse=True)
    truncated = False
    if limit is not None and limit >= 0 and len(values) > limit:
        values = values[:limit]
        truncated = True
    terminal_count = sum(1 for item in values if item.get("status") in TERMINAL_STATUSES)
    return {
        "schema_version": JOB_HISTORY_SCHEMA_VERSION,
        "kind": "gui_job_history",
        "jobs": values,
        "job_count": len(values),
        "terminal_count": terminal_count,
        "truncated": truncated,
        "summary": summarize_jobs(values),
    }


def record_job_result(history: Mapping[str, Any], job: Mapping[str, Any]) -> dict[str, object]:
    jobs = [dict(item) for item in history.get("jobs", []) if isinstance(item, Mapping)]
    jobs.insert(0, dict(job))
    return build_job_history(jobs)


__all__ = ["JOB_HISTORY_SCHEMA_VERSION", "TERMINAL_STATUSES", "build_job_history", "record_job_result"]
