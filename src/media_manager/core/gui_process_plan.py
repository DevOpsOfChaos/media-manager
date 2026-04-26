from __future__ import annotations

from typing import Any, Mapping, Sequence

PROCESS_PLAN_SCHEMA_VERSION = "1.0"


def build_process_plan(
    *,
    command_argv: Sequence[object],
    cwd: str | None = None,
    env_overrides: Mapping[str, object] | None = None,
    capture_output: bool = True,
    timeout_seconds: int | None = None,
) -> dict[str, object]:
    argv = [str(item) for item in command_argv if item is not None]
    return {
        "schema_version": PROCESS_PLAN_SCHEMA_VERSION,
        "kind": "gui_process_plan",
        "command_argv": argv,
        "program": argv[0] if argv else None,
        "args": argv[1:],
        "cwd": cwd,
        "env_overrides": {str(key): str(value) for key, value in dict(env_overrides or {}).items()},
        "capture_output": bool(capture_output),
        "timeout_seconds": timeout_seconds,
        "shell": False,
        "executes_immediately": False,
    }


def process_plan_from_job(job: Mapping[str, Any], *, cwd: str | None = None) -> dict[str, object]:
    plan = build_process_plan(command_argv=job.get("command_argv", ()), cwd=cwd)
    plan["job_id"] = job.get("job_id")
    plan["action_id"] = job.get("action_id")
    plan["risk_level"] = job.get("risk_level")
    return plan


def validate_process_plan(plan: Mapping[str, Any]) -> dict[str, object]:
    problems: list[str] = []
    argv = plan.get("command_argv")
    if not isinstance(argv, list) or not argv:
        problems.append("missing_command_argv")
    if plan.get("shell") is True:
        problems.append("shell_execution_not_allowed")
    return {
        "schema_version": PROCESS_PLAN_SCHEMA_VERSION,
        "valid": not problems,
        "problems": problems,
        "safe_to_prepare": not problems,
    }


__all__ = ["PROCESS_PLAN_SCHEMA_VERSION", "build_process_plan", "process_plan_from_job", "validate_process_plan"]
