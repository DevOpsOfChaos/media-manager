from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

TELEMETRY_SNAPSHOT_SCHEMA_VERSION = "1.0"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def build_local_telemetry_snapshot(
    *,
    shell_model: Mapping[str, Any] | None = None,
    diagnostics: Mapping[str, Any] | None = None,
    performance: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    shell = _mapping(shell_model)
    page = _mapping(shell.get("page"))
    diagnostics = _mapping(diagnostics)
    performance = _mapping(performance)
    problems = _list(diagnostics.get("problems"))
    warnings = _list(diagnostics.get("warnings"))
    budget = _mapping(performance.get("summary"))
    return {
        "schema_version": TELEMETRY_SNAPSHOT_SCHEMA_VERSION,
        "kind": "qt_local_telemetry_snapshot",
        "generated_at_utc": _now(),
        "privacy": {
            "local_only": True,
            "network_transmission": False,
            "contains_file_paths": False,
            "contains_biometric_data": False,
        },
        "shell": {
            "active_page_id": shell.get("active_page_id"),
            "language": shell.get("language"),
            "theme": _mapping(shell.get("theme")).get("theme"),
            "page_kind": page.get("kind"),
        },
        "diagnostics": {
            "problem_count": len(problems),
            "warning_count": len(warnings),
        },
        "performance": {
            "budget_ok": budget.get("budget_ok", True),
            "violation_count": budget.get("violation_count", 0),
        },
        "attention_required": bool(problems) or bool(budget.get("violation_count", 0)),
    }


__all__ = ["TELEMETRY_SNAPSHOT_SCHEMA_VERSION", "build_local_telemetry_snapshot"]
