from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_EXPORT_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _redact_result(result: Mapping[str, Any]) -> dict[str, object]:
    return {
        "check_id": result.get("check_id"),
        "passed": bool(result.get("passed")),
        "required": bool(result.get("required", True)),
        "category": result.get("category"),
        "note": result.get("note"),
        "has_evidence_path": bool(result.get("evidence_path")),
    }


def _redact_session(session: Mapping[str, Any], *, include_results: bool) -> dict[str, object]:
    payload: dict[str, object] = {
        "active_page_id": session.get("active_page_id"),
        "complete": bool(session.get("complete")),
        "summary": dict(_mapping(session.get("summary"))),
        "missing_required_checks": list(_list(session.get("missing_required_checks"))),
        "failed_required_checks": list(_list(session.get("failed_required_checks"))),
    }
    if include_results:
        payload["results"] = [
            _redact_result(result)
            for result in _list(session.get("results"))
            if isinstance(result, Mapping)
        ]
    return payload


def build_qt_runtime_smoke_export_bundle(
    smoke_report: Mapping[str, Any],
    *,
    include_results: bool = True,
) -> dict[str, object]:
    """Build a shareable metadata-only smoke export.

    Evidence paths are reduced to booleans. The export contains no face crops,
    no media file contents, no embeddings, and no telemetry payload.
    """

    session = _mapping(smoke_report.get("session"))
    audit = _mapping(smoke_report.get("audit"))
    return {
        "schema_version": QT_RUNTIME_SMOKE_EXPORT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_export_bundle",
        "active_page_id": smoke_report.get("active_page_id"),
        "ready_for_release_gate": bool(smoke_report.get("ready_for_release_gate")),
        "handoff_ready": bool(smoke_report.get("handoff_ready")),
        "launch_ready": bool(smoke_report.get("launch_ready")),
        "summary": dict(_mapping(smoke_report.get("summary"))),
        "session": _redact_session(session, include_results=include_results),
        "audit": {
            "valid": bool(audit.get("valid")),
            "problem_count": int(audit.get("problem_count") or 0),
            "problems": [dict(problem) for problem in _list(audit.get("problems")) if isinstance(problem, Mapping)],
            "summary": dict(_mapping(audit.get("summary"))),
        },
        "privacy": {
            "metadata_only": True,
            "contains_face_crops": False,
            "contains_embeddings": False,
            "contains_media_file_contents": False,
            "evidence_paths_redacted": True,
            "local_only_source": True,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_EXPORT_SCHEMA_VERSION", "build_qt_runtime_smoke_export_bundle"]
