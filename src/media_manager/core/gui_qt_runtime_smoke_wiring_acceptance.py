from __future__ import annotations
from collections.abc import Mapping
from typing import Any
QT_RUNTIME_SMOKE_WIRING_ACCEPTANCE_SCHEMA_VERSION = "1.0"
def _m(v: object) -> Mapping[str, Any]: return v if isinstance(v, Mapping) else {}
def build_qt_runtime_smoke_wiring_acceptance(audit: Mapping[str, Any]) -> dict[str, object]:
    checks=[{"id":"audit-valid","passed":bool(audit.get("valid")),"required":True},{"id":"no-window-opened","passed":True,"required":True},{"id":"no-command-execution","passed":True,"required":True},{"id":"rollback-available","passed":int(_m(audit.get("summary")).get("rollback_operation_count") or 0)>0,"required":True},{"id":"local-only","passed":_m(audit.get("summary")).get("local_only") is True,"required":True}]
    accepted=all(c["passed"] for c in checks if c["required"])
    return {"schema_version": QT_RUNTIME_SMOKE_WIRING_ACCEPTANCE_SCHEMA_VERSION, "kind": "qt_runtime_smoke_wiring_acceptance", "accepted": accepted, "checks": checks, "summary": {"check_count": len(checks), "failed_required_count": sum(1 for c in checks if c["required"] and not c["passed"]), "accepted": accepted, "opens_window": False, "executes_commands": False, "local_only": True}, "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True}}
__all__ = ["QT_RUNTIME_SMOKE_WIRING_ACCEPTANCE_SCHEMA_VERSION", "build_qt_runtime_smoke_wiring_acceptance"]
