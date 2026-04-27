from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_RESULT_SUMMARY_SCHEMA_VERSION = "1.0"


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def summarize_qt_runtime_smoke_desktop_results(validation: Mapping[str, Any]) -> dict[str, object]:
    results = [result for result in _list(validation.get("results")) if isinstance(result, Mapping)]
    required = [result for result in results if result.get("required")]
    completed = [result for result in results if result.get("passed") is not None]
    failed = [result for result in required if result.get("passed") is False]
    missing = [result for result in required if result.get("passed") is None]
    passed = [result for result in required if result.get("passed") is True]
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_RESULT_SUMMARY_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_result_summary",
        "result_count": len(results),
        "required_result_count": len(required),
        "completed_result_count": len(completed),
        "passed_required_count": len(passed),
        "failed_required_count": len(failed),
        "missing_required_count": len(missing),
        "evidence_count": sum(1 for result in results if result.get("has_evidence_path")),
        "sensitive_media_count": sum(1 for result in results if result.get("contains_sensitive_media")),
        "complete": len(missing) == 0,
        "passed": len(failed) == 0 and len(missing) == 0 and bool(required),
        "local_only": True,
        "opens_window": False,
        "executes_commands": False,
    }


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_RESULT_SUMMARY_SCHEMA_VERSION", "summarize_qt_runtime_smoke_desktop_results"]
