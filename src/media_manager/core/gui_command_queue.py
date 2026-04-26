from __future__ import annotations

from typing import Any, Mapping, Sequence

from .gui_execution_guard import guard_job_for_queue
from .gui_job_model import build_gui_job, summarize_jobs, transition_gui_job

COMMAND_QUEUE_SCHEMA_VERSION = "1.0"


def build_command_queue(jobs: Sequence[Mapping[str, Any]] = ()) -> dict[str, object]:
    job_list = [dict(job) for job in jobs]
    return {
        "schema_version": COMMAND_QUEUE_SCHEMA_VERSION,
        "kind": "gui_command_queue",
        "jobs": job_list,
        "summary": summarize_jobs(job_list),
        "executes_commands": False,
    }


def enqueue_action(
    queue: Mapping[str, Any],
    *,
    action_id: str,
    command_argv: Sequence[object],
    title: str | None = None,
    risk_level: str = "safe",
    confirmed: bool = False,
    allow_destructive: bool = False,
) -> dict[str, object]:
    jobs = [dict(item) for item in queue.get("jobs", []) if isinstance(item, Mapping)]
    draft = build_gui_job(action_id=action_id, command_argv=command_argv, title=title, risk_level=risk_level)
    guard = guard_job_for_queue(draft, confirmed=confirmed, allow_destructive=allow_destructive)
    job = transition_gui_job(draft, "queued" if guard["safe_to_queue"] else "blocked")
    job["guard"] = guard
    jobs.append(job)
    payload = build_command_queue(jobs)
    payload["last_job_id"] = job["job_id"]
    payload["last_guard"] = guard
    return payload


def dequeue_next_job(queue: Mapping[str, Any]) -> dict[str, object]:
    jobs = [dict(item) for item in queue.get("jobs", []) if isinstance(item, Mapping)]
    next_job = next((job for job in jobs if job.get("status") == "queued"), None)
    return {
        "schema_version": COMMAND_QUEUE_SCHEMA_VERSION,
        "job": next_job,
        "has_job": next_job is not None,
        "remaining_queued_count": sum(1 for job in jobs if job.get("status") == "queued") - (1 if next_job else 0),
    }


__all__ = ["COMMAND_QUEUE_SCHEMA_VERSION", "build_command_queue", "dequeue_next_job", "enqueue_action"]
