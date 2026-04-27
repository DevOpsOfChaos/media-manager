from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_runtime_smoke_status import build_qt_runtime_smoke_status_badge, build_qt_runtime_smoke_status_strip
from .gui_qt_runtime_smoke_trend import build_qt_runtime_smoke_trend

QT_RUNTIME_SMOKE_DASHBOARD_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _int(value: object, fallback: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def build_qt_runtime_smoke_dashboard(*, current_report: Mapping[str, Any] | None = None, history: Mapping[str, Any] | list[Mapping[str, Any]] | None = None, artifact_manifest: Mapping[str, Any] | None = None) -> dict[str, object]:
    report = _mapping(current_report)
    artifact = _mapping(artifact_manifest)
    report_summary = _mapping(report.get("summary"))
    artifact_summary = _mapping(artifact.get("summary"))
    trend = build_qt_runtime_smoke_trend(history if history is not None else [])
    trend_summary = _mapping(trend.get("summary"))
    current_badge = build_qt_runtime_smoke_status_badge(report, label="Current smoke")
    trend_badge = build_qt_runtime_smoke_status_badge({"summary": {"ready_for_release_gate": trend_summary.get("latest_ready"), "problem_count": trend_summary.get("latest_problem_count")}}, label="History trend")
    artifact_badge = build_qt_runtime_smoke_status_badge({"summary": {"ready_for_release_gate": True, "problem_count": artifact_summary.get("sensitive_media_count", 0)}}, label="Artifacts")
    status_strip = build_qt_runtime_smoke_status_strip([current_badge, trend_badge, artifact_badge])
    strip_summary = _mapping(status_strip.get("summary"))
    cards = [
        {"id": "current-report", "title": "Current runtime smoke", "metric": "ready" if current_badge["ready"] else current_badge["state"], "details": {"check_count": _int(report_summary.get("check_count")), "result_count": _int(report_summary.get("result_count")), "problem_count": _int(report_summary.get("problem_count")), "privacy_check_count": _int(report_summary.get("privacy_check_count"))}},
        {"id": "history", "title": "Smoke history", "metric": trend_summary.get("direction"), "details": dict(trend_summary)},
        {"id": "artifacts", "title": "Local artifacts", "metric": artifact_summary.get("artifact_count", 0), "details": {"artifact_count": _int(artifact_summary.get("artifact_count")), "metadata_only_count": _int(artifact_summary.get("metadata_only_count")), "sensitive_media_count": _int(artifact_summary.get("sensitive_media_count")), "all_local_only": bool(artifact_summary.get("all_local_only", True))}},
    ]
    blocked = int(strip_summary.get("blocked_count") or 0)
    ready = bool(current_badge["ready"]) and blocked == 0
    return {
        "schema_version": QT_RUNTIME_SMOKE_DASHBOARD_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_dashboard",
        "active_page_id": report.get("active_page_id") or trend_summary.get("latest_active_page_id"),
        "status_strip": status_strip,
        "trend": trend,
        "cards": cards,
        "summary": {"card_count": len(cards), "current_ready": bool(current_badge["ready"]), "blocked_badge_count": blocked, "incomplete_badge_count": strip_summary.get("incomplete_count", 0), "history_entry_count": trend_summary.get("entry_count", 0), "artifact_count": artifact_summary.get("artifact_count", 0), "ready_for_runtime_review": ready},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
        "ready_for_runtime_review": ready,
    }


__all__ = ["QT_RUNTIME_SMOKE_DASHBOARD_SCHEMA_VERSION", "build_qt_runtime_smoke_dashboard"]
