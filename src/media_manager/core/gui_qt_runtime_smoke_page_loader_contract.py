from __future__ import annotations
from collections.abc import Mapping
from typing import Any
QT_RUNTIME_SMOKE_PAGE_LOADER_CONTRACT_SCHEMA_VERSION = "1.0"
def build_qt_runtime_smoke_page_loader_contract(wiring_plan: Mapping[str, Any]) -> dict[str, object]:
    enabled = bool(wiring_plan.get("ready"))
    pre = [{"id": "wiring-plan-ready", "passed": enabled, "required": True}, {"id": "manual-only", "passed": True, "required": True}, {"id": "local-only", "passed": True, "required": True}]
    return {"schema_version": QT_RUNTIME_SMOKE_PAGE_LOADER_CONTRACT_SCHEMA_VERSION, "kind": "qt_runtime_smoke_page_loader_contract", "loader_id": "runtime-smoke-page-loader", "page_id": "runtime-smoke", "enabled": enabled, "source_module": "media_manager.core.gui_qt_runtime_smoke_adapter_bundle", "factory_name": "build_qt_runtime_smoke_adapter_bundle", "lazy_import": True, "render_requires_pyside6": True, "contract_requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True, "preconditions": pre, "summary": {"precondition_count": len(pre), "failed_required_precondition_count": sum(1 for p in pre if p["required"] and not p["passed"]), "enabled": enabled, "opens_window": False, "executes_commands": False, "local_only": True}, "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True}}
__all__ = ["QT_RUNTIME_SMOKE_PAGE_LOADER_CONTRACT_SCHEMA_VERSION", "build_qt_runtime_smoke_page_loader_contract"]
