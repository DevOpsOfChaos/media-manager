from __future__ import annotations
from collections.abc import Mapping
from typing import Any
QT_RUNTIME_SMOKE_SHELL_REGISTRATION_SCHEMA_VERSION = "1.0"
def _mapping(value: object) -> Mapping[str, Any]: return value if isinstance(value, Mapping) else {}
def build_qt_runtime_smoke_shell_registration(page_handoff: Mapping[str, Any], *, section_id: str = "runtime") -> dict[str, object]:
    route = _mapping(page_handoff.get("route")); nav = _mapping(page_handoff.get("navigation_item")); diag = _mapping(page_handoff.get("diagnostics")); summary = _mapping(page_handoff.get("summary"))
    ready = bool(page_handoff.get("ready_for_shell_registration")) and bool(diag.get("ready"))
    return {"schema_version": QT_RUNTIME_SMOKE_SHELL_REGISTRATION_SCHEMA_VERSION, "kind": "qt_runtime_smoke_shell_registration", "section_id": section_id, "page_id": route.get("page_id") or "runtime-smoke", "route_id": route.get("route_id") or "runtime-smoke", "label": nav.get("label") or "Runtime Smoke", "navigation_item": dict(nav), "route": dict(route), "diagnostics": dict(diag), "enabled": ready, "visible": bool(nav.get("visible", True)), "summary": {"ready_for_shell_registration": ready, "problem_count": int(summary.get("problem_count") or 0), "local_only": bool(summary.get("local_only", True)), "opens_window": False, "executes_commands": False}, "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True}}
__all__ = ["QT_RUNTIME_SMOKE_SHELL_REGISTRATION_SCHEMA_VERSION", "build_qt_runtime_smoke_shell_registration"]
