from __future__ import annotations

from typing import Any, Mapping, Sequence

EXECUTION_GUARD_SCHEMA_VERSION = "1.0"
DANGEROUS_FLAGS = {"--apply", "--yes", "--delete", "--move", "--apply-organize", "--apply-rename", "--include-encodings"}
DESTRUCTIVE_FLAGS = {"--delete", "--yes"}


def _argv_tokens(command_argv: Sequence[object]) -> list[str]:
    return [str(item) for item in command_argv if item is not None]


def inspect_command_safety(command_argv: Sequence[object], *, confirmed: bool = False, allow_destructive: bool = False) -> dict[str, object]:
    argv = _argv_tokens(command_argv)
    flags = {item for item in argv if item.startswith("--")}
    risky = sorted(flags & DANGEROUS_FLAGS)
    destructive = sorted(flags & DESTRUCTIVE_FLAGS)
    needs_confirmation = bool(risky)
    blocked_reasons: list[str] = []
    if needs_confirmation and not confirmed:
        blocked_reasons.append("confirmation_required")
    if destructive and not allow_destructive:
        blocked_reasons.append("destructive_flags_blocked")
    return {
        "schema_version": EXECUTION_GUARD_SCHEMA_VERSION,
        "command_argv": argv,
        "risky_flags": risky,
        "destructive_flags": destructive,
        "requires_confirmation": needs_confirmation,
        "confirmed": bool(confirmed),
        "allow_destructive": bool(allow_destructive),
        "blocked": bool(blocked_reasons),
        "blocked_reasons": blocked_reasons,
        "safe_to_queue": not blocked_reasons,
    }


def guard_job_for_queue(job: Mapping[str, Any], *, confirmed: bool = False, allow_destructive: bool = False) -> dict[str, object]:
    safety = inspect_command_safety(job.get("command_argv", ()), confirmed=confirmed, allow_destructive=allow_destructive)
    return {
        "schema_version": EXECUTION_GUARD_SCHEMA_VERSION,
        "job_id": job.get("job_id"),
        "action_id": job.get("action_id"),
        "status": "allowed" if safety["safe_to_queue"] else "blocked",
        "safe_to_queue": safety["safe_to_queue"],
        "safety": safety,
        "next_action": "queue_job" if safety["safe_to_queue"] else "review_confirmation_and_risk_flags",
    }


__all__ = ["DANGEROUS_FLAGS", "DESTRUCTIVE_FLAGS", "EXECUTION_GUARD_SCHEMA_VERSION", "guard_job_for_queue", "inspect_command_safety"]
