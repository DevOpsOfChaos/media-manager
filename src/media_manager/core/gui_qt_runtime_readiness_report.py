from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_runtime_node_trace import build_qt_runtime_sensitive_node_traces
from .gui_qt_runtime_safety_audit import audit_qt_runtime_build_safety
from .gui_qt_runtime_step_index import build_qt_runtime_step_index

QT_RUNTIME_READINESS_REPORT_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _build_plan_from_payload(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    if payload.get("kind") == "qt_runtime_build_plan":
        return payload
    return _mapping(payload.get("build_plan"))


def build_qt_runtime_readiness_report(bootstrap_or_build_plan: Mapping[str, Any]) -> dict[str, object]:
    """Build a headless readiness report for the future PySide6 runtime path."""

    build_plan = _build_plan_from_payload(bootstrap_or_build_plan)
    validation = _mapping(bootstrap_or_build_plan.get("validation"))
    validation_problem_count = int(validation.get("problem_count") or 0)
    step_index = build_qt_runtime_step_index(build_plan)
    safety_audit = audit_qt_runtime_build_safety(build_plan)
    sensitive_traces = build_qt_runtime_sensitive_node_traces(build_plan)
    index_summary = _mapping(step_index.get("summary"))
    safety_summary = _mapping(safety_audit.get("summary"))
    source_ready = bool(bootstrap_or_build_plan.get("ready", True))
    ready = (
        source_ready
        and bool(safety_audit.get("valid"))
        and validation_problem_count == 0
        and bool(index_summary.get("order_is_monotonic"))
        and int(index_summary.get("duplicate_step_id_count") or 0) == 0
    )
    return {
        "schema_version": QT_RUNTIME_READINESS_REPORT_SCHEMA_VERSION,
        "kind": "qt_runtime_readiness_report",
        "active_page_id": bootstrap_or_build_plan.get("active_page_id") or _mapping(bootstrap_or_build_plan.get("summary")).get("active_page_id"),
        "step_index": step_index,
        "safety_audit": safety_audit,
        "sensitive_node_traces": sensitive_traces,
        "validation": dict(validation),
        "summary": {
            "step_count": index_summary.get("step_count", 0),
            "node_count": index_summary.get("node_count", 0),
            "operation_count": index_summary.get("operation_count", 0),
            "sensitive_node_count": safety_summary.get("sensitive_node_count", 0),
            "local_only_node_count": safety_summary.get("local_only_node_count", 0),
            "deferred_execution_count": safety_summary.get("deferred_execution_count", 0),
            "safety_problem_count": safety_audit.get("problem_count", 0),
            "validation_problem_count": validation_problem_count,
            "ready": ready,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
        "ready": ready,
    }


def summarize_qt_runtime_readiness_report(report: Mapping[str, Any]) -> str:
    summary = _mapping(report.get("summary"))
    return "\n".join(
        [
            "Qt runtime readiness report",
            f"  Active page: {report.get('active_page_id')}",
            f"  Ready: {report.get('ready')}",
            f"  Steps: {summary.get('step_count', 0)}",
            f"  Nodes: {summary.get('node_count', 0)}",
            f"  Sensitive nodes: {summary.get('sensitive_node_count', 0)}",
            f"  Safety problems: {summary.get('safety_problem_count', 0)}",
            f"  Validation problems: {summary.get('validation_problem_count', 0)}",
        ]
    )


__all__ = [
    "QT_RUNTIME_READINESS_REPORT_SCHEMA_VERSION",
    "build_qt_runtime_readiness_report",
    "summarize_qt_runtime_readiness_report",
]
