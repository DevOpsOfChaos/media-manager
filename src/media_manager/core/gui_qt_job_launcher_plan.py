from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

JOB_LAUNCHER_PLAN_SCHEMA_VERSION = "1.0"
_RISK_FLAGS = {"--apply", "--yes", "--delete", "--include-encodings", "--move"}


def build_job_launcher_plan(
    command_preview: Iterable[object],
    *,
    title: str = "Run command",
    confirmed: bool = False,
) -> dict[str, object]:
    argv = [str(item) for item in command_preview if str(item)]
    risk_flags = [item for item in argv if item in _RISK_FLAGS]
    risk_level = "high" if {"--apply", "--yes", "--delete"}.intersection(risk_flags) else "medium" if risk_flags else "safe"
    can_launch = bool(argv) and (not risk_flags or confirmed)
    return {
        "schema_version": JOB_LAUNCHER_PLAN_SCHEMA_VERSION,
        "kind": "qt_job_launcher_plan",
        "title": title,
        "argv": argv,
        "command_preview": " ".join(_quote(item) for item in argv),
        "risk_level": risk_level,
        "risk_flags": risk_flags,
        "requires_confirmation": bool(risk_flags),
        "confirmed": bool(confirmed),
        "can_launch": can_launch,
        "executes_immediately": False,
        "blocked_reason": None if can_launch else "Command preview is empty." if not argv else "Confirmation is required.",
    }


def _quote(value: str) -> str:
    return f'"{value}"' if any(ch.isspace() for ch in value) else value


def launcher_plan_summary(plan: Mapping[str, Any]) -> dict[str, object]:
    return {
        "risk_level": plan.get("risk_level"),
        "can_launch": bool(plan.get("can_launch")),
        "requires_confirmation": bool(plan.get("requires_confirmation")),
        "arg_count": len(plan.get("argv", [])) if isinstance(plan.get("argv"), list) else 0,
    }


__all__ = ["JOB_LAUNCHER_PLAN_SCHEMA_VERSION", "build_job_launcher_plan", "launcher_plan_summary"]
