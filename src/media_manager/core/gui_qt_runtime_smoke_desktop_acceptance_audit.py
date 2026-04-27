from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_AUDIT_SCHEMA_VERSION = "1.0"


def _summary(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    return payload.get("summary") if isinstance(payload.get("summary"), Mapping) else {}


def audit_qt_runtime_smoke_desktop_acceptance(
    gate: Mapping[str, Any],
    checklist: Mapping[str, Any],
    policy: Mapping[str, Any],
    redaction: Mapping[str, Any],
) -> dict[str, object]:
    problems = []
    if gate.get("ready") is not True:
        problems.append({"code": "acceptance_gate_not_ready"})
    if int(_summary(checklist).get("failed_required_count") or 0) > 0:
        problems.append({"code": "acceptance_checklist_failed"})
    if int(_summary(policy).get("failed_required_count") or 0) > 0:
        problems.append({"code": "evidence_policy_failed"})
    if int(_summary(redaction).get("sensitive_media_count") or 0) > 0:
        problems.append({"code": "sensitive_media_in_redacted_export"})
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_AUDIT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_acceptance_audit",
        "valid": not problems,
        "problem_count": len(problems),
        "problems": problems,
        "summary": {
            "valid": not problems,
            "problem_count": len(problems),
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


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_AUDIT_SCHEMA_VERSION", "audit_qt_runtime_smoke_desktop_acceptance"]
