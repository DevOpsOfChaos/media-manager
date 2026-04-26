from __future__ import annotations

from typing import Any, Mapping

RESULT_MODEL_SCHEMA_VERSION = "1.0"


def build_job_result(
    *,
    job_id: str | None,
    exit_code: int | None = None,
    stdout: str = "",
    stderr: str = "",
    cancelled: bool = False,
    timed_out: bool = False,
) -> dict[str, object]:
    success = exit_code == 0 and not cancelled and not timed_out
    status = "cancelled" if cancelled else "timed_out" if timed_out else "completed" if success else "failed"
    return {
        "schema_version": RESULT_MODEL_SCHEMA_VERSION,
        "kind": "gui_job_result",
        "job_id": job_id,
        "exit_code": exit_code,
        "status": status,
        "success": success,
        "cancelled": bool(cancelled),
        "timed_out": bool(timed_out),
        "stdout_preview": stdout[:2000],
        "stderr_preview": stderr[:2000],
        "has_stdout": bool(stdout),
        "has_stderr": bool(stderr),
    }


def summarize_job_result(result: Mapping[str, Any]) -> dict[str, object]:
    return {
        "schema_version": RESULT_MODEL_SCHEMA_VERSION,
        "job_id": result.get("job_id"),
        "status": result.get("status"),
        "success": bool(result.get("success")),
        "has_output": bool(result.get("has_stdout") or result.get("has_stderr")),
        "needs_attention": result.get("status") in {"failed", "timed_out", "cancelled"} or bool(result.get("has_stderr")),
    }


__all__ = ["RESULT_MODEL_SCHEMA_VERSION", "build_job_result", "summarize_job_result"]
