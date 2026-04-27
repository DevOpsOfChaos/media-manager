from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_REDACTION_SCHEMA_VERSION = "1.0"


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_qt_runtime_smoke_desktop_acceptance_redaction(export_payload: Mapping[str, Any]) -> dict[str, object]:
    redacted_results = []
    for row in _list(export_payload.get("results")):
        if not isinstance(row, Mapping):
            continue
        redacted_results.append(
            {
                "check_id": row.get("check_id"),
                "passed": row.get("passed"),
                "required": row.get("required"),
                "has_evidence_path": bool(row.get("has_evidence_path")),
                "evidence_path": None,
                "contains_sensitive_media": bool(row.get("contains_sensitive_media")),
            }
        )
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_REDACTION_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_acceptance_redaction",
        "results": redacted_results,
        "summary": {
            "result_count": len(redacted_results),
            "evidence_path_redacted_count": sum(1 for row in redacted_results if row["has_evidence_path"]),
            "sensitive_media_count": sum(1 for row in redacted_results if row["contains_sensitive_media"]),
            "metadata_only": True,
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


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_REDACTION_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_acceptance_redaction"]
