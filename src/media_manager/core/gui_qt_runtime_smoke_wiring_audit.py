from __future__ import annotations
from collections.abc import Mapping
from typing import Any
QT_RUNTIME_SMOKE_WIRING_AUDIT_SCHEMA_VERSION = "1.0"
def _m(v: object) -> Mapping[str, Any]: return v if isinstance(v, Mapping) else {}
def audit_qt_runtime_smoke_wiring(wiring_plan: Mapping[str, Any], dry_run: Mapping[str, Any], rollback_plan: Mapping[str, Any]) -> dict[str, object]:
    problems=[]; ds=_m(dry_run.get("summary")); rs=_m(rollback_plan.get("summary")); ws=_m(wiring_plan.get("summary"))
    if wiring_plan.get("ready") is not True: problems.append({"code": "wiring_plan_not_ready"})
    if ds.get("ready") is not True: problems.append({"code": "dry_run_not_ready"})
    if int(ds.get("immediate_execution_count") or 0) > 0: problems.append({"code": "dry_run_executes_immediately"})
    if int(rs.get("immediate_execution_count") or 0) > 0: problems.append({"code": "rollback_executes_immediately"})
    if ws.get("local_only") is not True or ds.get("local_only") is not True or rs.get("local_only") is not True: problems.append({"code": "wiring_not_local_only"})
    return {"schema_version": QT_RUNTIME_SMOKE_WIRING_AUDIT_SCHEMA_VERSION, "kind": "qt_runtime_smoke_wiring_audit", "valid": not problems, "problem_count": len(problems), "problems": problems, "summary": {"wiring_ready": bool(wiring_plan.get("ready")), "dry_run_ready": bool(ds.get("ready")), "rollback_operation_count": int(rs.get("operation_count") or 0), "local_only": True, "opens_window": False, "executes_commands": False}, "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True}}
__all__ = ["QT_RUNTIME_SMOKE_WIRING_AUDIT_SCHEMA_VERSION", "audit_qt_runtime_smoke_wiring"]
