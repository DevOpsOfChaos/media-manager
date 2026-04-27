from __future__ import annotations
from collections.abc import Mapping
from .gui_qt_runtime_smoke_shell_commands import build_qt_runtime_smoke_shell_commands
from .gui_qt_runtime_smoke_shell_guard import build_qt_runtime_smoke_shell_guard
from .gui_qt_runtime_smoke_shell_navigation_patch import build_qt_runtime_smoke_shell_navigation_patch
from .gui_qt_runtime_smoke_shell_readiness import evaluate_qt_runtime_smoke_shell_readiness
from .gui_qt_runtime_smoke_shell_registration import build_qt_runtime_smoke_shell_registration
from .gui_qt_runtime_smoke_shell_report import build_qt_runtime_smoke_shell_report
from .gui_qt_runtime_smoke_shell_snapshot import build_qt_runtime_smoke_shell_snapshot
from .gui_qt_runtime_smoke_shell_status_slot import build_qt_runtime_smoke_shell_status_slot
from .gui_qt_runtime_smoke_shell_toolbar import build_qt_runtime_smoke_shell_toolbar
QT_RUNTIME_SMOKE_SHELL_BUNDLE_SCHEMA_VERSION = "1.0"
def build_qt_runtime_smoke_shell_bundle(page_handoff: Mapping[str, object], *, existing_navigation_items: list[Mapping[str, object]] | None = None) -> dict[str, object]:
    registration = build_qt_runtime_smoke_shell_registration(page_handoff); navigation_patch = build_qt_runtime_smoke_shell_navigation_patch(registration, existing_items=existing_navigation_items); commands = build_qt_runtime_smoke_shell_commands(registration); toolbar = build_qt_runtime_smoke_shell_toolbar(commands); status_slot = build_qt_runtime_smoke_shell_status_slot(registration); guard = build_qt_runtime_smoke_shell_guard(registration); readiness = evaluate_qt_runtime_smoke_shell_readiness(registration, navigation_patch, commands, toolbar, guard)
    bundle: dict[str, object] = {"schema_version": QT_RUNTIME_SMOKE_SHELL_BUNDLE_SCHEMA_VERSION, "kind": "qt_runtime_smoke_shell_bundle", "shell_registration": registration, "navigation_patch": navigation_patch, "commands": commands, "toolbar": toolbar, "status_slot": status_slot, "guard": guard, "readiness": readiness, "ready_for_shell": bool(readiness.get("ready")), "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True}}
    bundle["report"] = build_qt_runtime_smoke_shell_report(bundle); bundle["snapshot"] = build_qt_runtime_smoke_shell_snapshot(bundle); bundle["summary"] = {"ready_for_shell": bool(bundle["ready_for_shell"]), "problem_count": readiness["problem_count"], "navigation_item_count": readiness["summary"]["navigation_item_count"], "command_count": readiness["summary"]["command_count"], "toolbar_button_count": readiness["summary"]["toolbar_button_count"], "local_only": readiness["summary"]["local_only"], "opens_window": False, "executes_commands": False}
    return bundle
__all__ = ["QT_RUNTIME_SMOKE_SHELL_BUNDLE_SCHEMA_VERSION", "build_qt_runtime_smoke_shell_bundle"]
