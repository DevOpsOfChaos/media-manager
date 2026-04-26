from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_HANDOFF_MANIFEST_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _int(value: object, fallback: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def build_qt_runtime_handoff_manifest(readiness_report: Mapping[str, Any]) -> dict[str, object]:
    """Create the handoff manifest between headless readiness and future Qt runtime.

    This manifest is still pure data. It does not import PySide6, does not open
    a window, and does not execute commands. It makes the readiness state easy
    for a future desktop launcher to consume.
    """

    summary = _mapping(readiness_report.get("summary"))
    safety_audit = _mapping(readiness_report.get("safety_audit"))
    safety_summary = _mapping(safety_audit.get("summary"))
    validation = _mapping(readiness_report.get("validation"))
    active_page_id = _text(readiness_report.get("active_page_id") or summary.get("active_page_id"), "dashboard")
    safety_problem_count = _int(readiness_report.get("summary", {}).get("safety_problem_count") if isinstance(readiness_report.get("summary"), Mapping) else 0)
    validation_problem_count = _int(summary.get("validation_problem_count") or validation.get("problem_count"))
    sensitive_node_count = _int(summary.get("sensitive_node_count") or safety_summary.get("sensitive_node_count"))
    ready = bool(readiness_report.get("ready")) and safety_problem_count == 0 and validation_problem_count == 0

    return {
        "schema_version": QT_RUNTIME_HANDOFF_MANIFEST_SCHEMA_VERSION,
        "kind": "qt_runtime_handoff_manifest",
        "active_page_id": active_page_id,
        "source_kind": readiness_report.get("kind"),
        "readiness": {
            "ready": ready,
            "step_count": _int(summary.get("step_count")),
            "node_count": _int(summary.get("node_count")),
            "operation_count": _int(summary.get("operation_count")),
            "sensitive_node_count": sensitive_node_count,
            "local_only_node_count": _int(summary.get("local_only_node_count") or safety_summary.get("local_only_node_count")),
            "deferred_execution_count": _int(summary.get("deferred_execution_count") or safety_summary.get("deferred_execution_count")),
            "safety_problem_count": safety_problem_count,
            "validation_problem_count": validation_problem_count,
        },
        "privacy": {
            "local_only": True,
            "contains_sensitive_people_data": sensitive_node_count > 0,
            "network_required": False,
            "telemetry_allowed": False,
            "privacy_notice": "People Review face assets and identities must stay local.",
        },
        "runtime_requirements": {
            "python_package": "media-manager",
            "optional_extra": "gui",
            "qt_binding": "PySide6",
            "requires_pyside6_to_build_manifest": False,
            "requires_pyside6_to_open_window": True,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
        "ready_for_manual_smoke": ready,
    }


def summarize_qt_runtime_handoff_manifest(manifest: Mapping[str, Any]) -> str:
    readiness = _mapping(manifest.get("readiness"))
    privacy = _mapping(manifest.get("privacy"))
    return "\n".join(
        [
            "Qt runtime handoff manifest",
            f"  Active page: {manifest.get('active_page_id')}",
            f"  Ready for manual smoke: {manifest.get('ready_for_manual_smoke')}",
            f"  Steps: {readiness.get('step_count', 0)}",
            f"  Nodes: {readiness.get('node_count', 0)}",
            f"  Sensitive people data: {privacy.get('contains_sensitive_people_data')}",
            f"  Local only: {privacy.get('local_only')}",
        ]
    )


__all__ = [
    "QT_RUNTIME_HANDOFF_MANIFEST_SCHEMA_VERSION",
    "build_qt_runtime_handoff_manifest",
    "summarize_qt_runtime_handoff_manifest",
]
