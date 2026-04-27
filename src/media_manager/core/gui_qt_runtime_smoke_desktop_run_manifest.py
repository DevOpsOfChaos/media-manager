from __future__ import annotations
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_RUN_MANIFEST_SCHEMA_VERSION = "1.0"

def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def _m(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}

def build_qt_runtime_smoke_desktop_run_manifest(start_plan: Mapping[str, Any], operator_sheet: Mapping[str, Any], *, run_id: str = "runtime-smoke-manual", recorded_at_utc: str | None = None) -> dict[str, object]:
    command = _m(start_plan.get("command_line"))
    check_count = _m(operator_sheet.get("summary")).get("check_count", 0)
    ready = bool(start_plan.get("ready_for_manual_start"))
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_RUN_MANIFEST_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_run_manifest",
        "run_id": run_id,
        "recorded_at_utc": recorded_at_utc or _now(),
        "page_id": "runtime-smoke",
        "command": command.get("display_command"),
        "operator_check_count": check_count,
        "ready_for_manual_start": ready,
        "privacy": {"local_only": True, "contains_face_crops": False, "contains_embeddings": False, "contains_media_file_contents": False, "telemetry_allowed": False},
        "summary": {"ready_for_manual_start": ready, "operator_check_count": check_count, "opens_window": False, "executes_commands": False, "local_only": True},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }

__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_RUN_MANIFEST_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_run_manifest"]
