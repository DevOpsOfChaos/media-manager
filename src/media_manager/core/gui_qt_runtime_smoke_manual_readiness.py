from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_MANUAL_READINESS_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_qt_runtime_smoke_manual_readiness(
    *,
    dry_run: Mapping[str, Any],
    start_bundle: Mapping[str, Any],
    acceptance_bundle: Mapping[str, Any],
) -> dict[str, object]:
    """Summarize whether the user can proceed to manual Qt runtime smoke."""

    dry_summary = _mapping(dry_run.get("summary"))
    start_summary = _mapping(start_bundle.get("summary"))
    acceptance_summary = _mapping(acceptance_bundle.get("summary"))
    ready_to_start = bool(dry_run.get("ready")) and bool(start_bundle.get("ready_for_manual_desktop_start"))
    accepted = bool(acceptance_bundle.get("accepted"))
    return {
        "schema_version": QT_RUNTIME_SMOKE_MANUAL_READINESS_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_manual_readiness",
        "ready_to_start_manual_smoke": ready_to_start,
        "accepted_after_results": accepted,
        "recommended_next_step": (
            "Start the manual Qt smoke run from the generated operator sheet."
            if ready_to_start and not accepted
            else "Review or fix the guarded Runtime Smoke dry-run before opening Qt."
        ),
        "summary": {
            "ready_to_start_manual_smoke": ready_to_start,
            "accepted_after_results": accepted,
            "dry_run_failed_required_count": dry_summary.get("failed_required_count", 0),
            "operator_check_count": start_summary.get("operator_check_count", 0),
            "acceptance_problem_count": acceptance_summary.get("problem_count", 0),
            "opens_window": False,
            "executes_commands": False,
            "local_only": True,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


def summarize_qt_runtime_smoke_manual_readiness(readiness: Mapping[str, Any]) -> str:
    summary = _mapping(readiness.get("summary"))
    return "\n".join(
        [
            "Qt Runtime Smoke manual readiness",
            f"  Ready to start manual smoke: {readiness.get('ready_to_start_manual_smoke')}",
            f"  Accepted after results: {readiness.get('accepted_after_results')}",
            f"  Dry-run failed required checks: {summary.get('dry_run_failed_required_count', 0)}",
            f"  Opens window now: {summary.get('opens_window')}",
            f"  Executes commands now: {summary.get('executes_commands')}",
        ]
    )


__all__ = [
    "QT_RUNTIME_SMOKE_MANUAL_READINESS_SCHEMA_VERSION",
    "build_qt_runtime_smoke_manual_readiness",
    "summarize_qt_runtime_smoke_manual_readiness",
]
