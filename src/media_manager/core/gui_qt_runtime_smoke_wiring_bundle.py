from __future__ import annotations
from collections.abc import Mapping
from .gui_qt_runtime_smoke_command_dispatch_plan import build_qt_runtime_smoke_command_dispatch_plan
from .gui_qt_runtime_smoke_page_loader_contract import build_qt_runtime_smoke_page_loader_contract
from .gui_qt_runtime_smoke_router_patch import build_qt_runtime_smoke_router_patch
from .gui_qt_runtime_smoke_shell_wiring_plan import build_qt_runtime_smoke_shell_wiring_plan
from .gui_qt_runtime_smoke_status_footer_patch import build_qt_runtime_smoke_status_footer_patch
from .gui_qt_runtime_smoke_wiring_acceptance import build_qt_runtime_smoke_wiring_acceptance
from .gui_qt_runtime_smoke_wiring_audit import audit_qt_runtime_smoke_wiring
from .gui_qt_runtime_smoke_wiring_dry_run import build_qt_runtime_smoke_wiring_dry_run
from .gui_qt_runtime_smoke_wiring_rollback_plan import build_qt_runtime_smoke_wiring_rollback_plan
from .gui_qt_runtime_smoke_wiring_snapshot import build_qt_runtime_smoke_wiring_snapshot
QT_RUNTIME_SMOKE_WIRING_BUNDLE_SCHEMA_VERSION = "1.0"
def build_qt_runtime_smoke_wiring_bundle(integration_bundle: Mapping[str, object], shell_bundle: Mapping[str, object], *, existing_routes: list[Mapping[str, object]] | None = None) -> dict[str, object]:
    wiring_plan=build_qt_runtime_smoke_shell_wiring_plan(integration_bundle, shell_bundle)
    router_patch=build_qt_runtime_smoke_router_patch(wiring_plan, existing_routes=existing_routes)
    loader=build_qt_runtime_smoke_page_loader_contract(wiring_plan); dispatch=build_qt_runtime_smoke_command_dispatch_plan(wiring_plan); footer=build_qt_runtime_smoke_status_footer_patch(wiring_plan)
    dry_run=build_qt_runtime_smoke_wiring_dry_run(router_patch, loader, dispatch, footer); rollback=build_qt_runtime_smoke_wiring_rollback_plan(wiring_plan, router_patch)
    audit=audit_qt_runtime_smoke_wiring(wiring_plan, dry_run, rollback); acceptance=build_qt_runtime_smoke_wiring_acceptance(audit)
    ready=bool(audit.get("valid")) and bool(acceptance.get("accepted"))
    bundle={"schema_version": QT_RUNTIME_SMOKE_WIRING_BUNDLE_SCHEMA_VERSION, "kind": "qt_runtime_smoke_wiring_bundle", "wiring_plan": wiring_plan, "router_patch": router_patch, "page_loader_contract": loader, "command_dispatch_plan": dispatch, "status_footer_patch": footer, "dry_run": dry_run, "rollback_plan": rollback, "audit": audit, "acceptance": acceptance, "ready_for_guarded_shell_wiring": ready, "summary": {"ready_for_guarded_shell_wiring": ready, "problem_count": int(audit.get("problem_count") or 0) + int(acceptance["summary"]["failed_required_count"]), "route_count": router_patch["summary"]["runtime_smoke_route_count"], "dispatch_count": dispatch["summary"]["dispatch_count"], "rollback_operation_count": rollback["summary"]["operation_count"], "local_only": True, "opens_window": False, "executes_commands": False}, "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True}}
    bundle["snapshot"]=build_qt_runtime_smoke_wiring_snapshot(bundle)
    return bundle
__all__ = ["QT_RUNTIME_SMOKE_WIRING_BUNDLE_SCHEMA_VERSION", "build_qt_runtime_smoke_wiring_bundle"]
