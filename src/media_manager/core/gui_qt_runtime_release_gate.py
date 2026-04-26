from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_RELEASE_GATE_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def evaluate_qt_runtime_release_gate(
    handoff_manifest: Mapping[str, Any],
    launch_contract: Mapping[str, Any],
    smoke_plan: Mapping[str, Any],
    *,
    smoke_results: Mapping[str, bool] | None = None,
) -> dict[str, object]:
    """Evaluate whether the runtime handoff is safe for a manual smoke attempt."""

    readiness = _mapping(handoff_manifest.get("readiness"))
    privacy = _mapping(handoff_manifest.get("privacy"))
    execution = _mapping(launch_contract.get("execution_policy"))
    results = dict(smoke_results or {})
    required_checks = [check for check in _list(smoke_plan.get("checks")) if isinstance(check, Mapping) and check.get("required")]
    missing_smoke_checks = [
        _text(check.get("id"))
        for check in required_checks
        if _text(check.get("id")) and results.get(_text(check.get("id"))) is not True
    ]

    gates = [
        {
            "id": "handoff-ready",
            "passed": bool(handoff_manifest.get("ready_for_manual_smoke")),
            "required": True,
        },
        {
            "id": "launch-contract-ready",
            "passed": bool(launch_contract.get("ready_for_launch_attempt")),
            "required": True,
        },
        {
            "id": "no-safety-problems",
            "passed": int(readiness.get("safety_problem_count") or 0) == 0,
            "required": True,
        },
        {
            "id": "no-validation-problems",
            "passed": int(readiness.get("validation_problem_count") or 0) == 0,
            "required": True,
        },
        {
            "id": "manual-only",
            "passed": execution.get("mode") == "manual_only" and execution.get("executes_immediately") is False,
            "required": True,
        },
        {
            "id": "local-only",
            "passed": bool(privacy.get("local_only")) and privacy.get("network_required") is False,
            "required": True,
        },
    ]
    ready_for_manual_smoke = all(gate["passed"] for gate in gates if gate.get("required"))
    manual_smoke_complete = ready_for_manual_smoke and not missing_smoke_checks and bool(results)
    return {
        "schema_version": QT_RUNTIME_RELEASE_GATE_SCHEMA_VERSION,
        "kind": "qt_runtime_release_gate",
        "active_page_id": handoff_manifest.get("active_page_id") or launch_contract.get("active_page_id"),
        "gates": gates,
        "missing_smoke_checks": missing_smoke_checks,
        "summary": {
            "gate_count": len(gates),
            "passed_gate_count": sum(1 for gate in gates if gate.get("passed")),
            "missing_smoke_check_count": len(missing_smoke_checks),
            "ready_for_manual_smoke": ready_for_manual_smoke,
            "manual_smoke_complete": manual_smoke_complete,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
        "ready_for_manual_smoke": ready_for_manual_smoke,
        "manual_smoke_complete": manual_smoke_complete,
    }


__all__ = ["QT_RUNTIME_RELEASE_GATE_SCHEMA_VERSION", "evaluate_qt_runtime_release_gate"]
