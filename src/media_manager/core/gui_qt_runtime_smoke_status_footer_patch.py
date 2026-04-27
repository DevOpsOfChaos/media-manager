from __future__ import annotations
from collections.abc import Mapping
from typing import Any
QT_RUNTIME_SMOKE_STATUS_FOOTER_PATCH_SCHEMA_VERSION = "1.0"
def _m(v: object) -> Mapping[str, Any]: return v if isinstance(v, Mapping) else {}
def build_qt_runtime_smoke_status_footer_patch(wiring_plan: Mapping[str, Any]) -> dict[str, object]:
    slot = _m(_m(wiring_plan.get("shell_bundle")).get("status_slot"))
    state = str(slot.get("state") or ("ready" if wiring_plan.get("ready") else "blocked"))
    item = {"slot_id": "runtime-smoke-status", "page_id": "runtime-smoke", "state": state, "text": slot.get("text") or ("Runtime Smoke ready" if state == "ready" else "Runtime Smoke needs attention"), "problem_count": int(slot.get("problem_count") or _m(wiring_plan.get("summary")).get("problem_count") or 0), "local_only": True, "opens_window": False, "executes_commands": False}
    return {"schema_version": QT_RUNTIME_SMOKE_STATUS_FOOTER_PATCH_SCHEMA_VERSION, "kind": "qt_runtime_smoke_status_footer_patch", "operation": "upsert_status_slot", "item": item, "summary": {"state": state, "problem_count": item["problem_count"], "enabled": bool(wiring_plan.get("ready")), "opens_window": False, "executes_commands": False, "local_only": True}, "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True}}
__all__ = ["QT_RUNTIME_SMOKE_STATUS_FOOTER_PATCH_SCHEMA_VERSION", "build_qt_runtime_smoke_status_footer_patch"]
