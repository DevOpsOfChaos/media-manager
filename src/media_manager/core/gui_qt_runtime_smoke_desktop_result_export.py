from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_RESULT_EXPORT_SCHEMA_VERSION = "1.0"


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_qt_runtime_smoke_desktop_result_export(report: Mapping[str, Any]) -> dict[str, object]:
    validation = report.get("validation") if isinstance(report.get("validation"), Mapping) else {}
    redacted_results = []
    for result in _list(validation.get("results")):
        if not isinstance(result, Mapping):
            continue
        redacted_results.append(
            {
                "check_id": result.get("check_id"),
                "label": result.get("label"),
                "required": result.get("required"),
                "passed": result.get("passed"),
                "note": result.get("note"),
                "has_evidence_path": bool(result.get("has_evidence_path")),
                "contains_sensitive_media": bool(result.get("contains_sensitive_media")),
            }
        )
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_RESULT_EXPORT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_result_export",
        "accepted": report.get("accepted"),
        "summary": dict(report.get("summary")) if isinstance(report.get("summary"), Mapping) else {},
        "results": redacted_results,
        "privacy": {
            "metadata_only": True,
            "evidence_paths_redacted": True,
            "contains_face_crops": False,
            "contains_embeddings": False,
            "contains_media_file_contents": False,
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


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_RESULT_EXPORT_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_result_export"]
