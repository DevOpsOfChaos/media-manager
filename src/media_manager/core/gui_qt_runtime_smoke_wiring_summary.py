from __future__ import annotations
from collections.abc import Mapping
from typing import Any
QT_RUNTIME_SMOKE_WIRING_SUMMARY_SCHEMA_VERSION = "1.0"
def _m(v: object) -> Mapping[str, Any]: return v if isinstance(v, Mapping) else {}
def summarize_qt_runtime_smoke_wiring_bundle(bundle: Mapping[str, Any]) -> str:
    s=_m(bundle.get("summary"))
    return "\n".join(["Qt runtime smoke guarded shell wiring", f"  Ready: {bundle.get('ready_for_guarded_shell_wiring')}", f"  Problems: {s.get('problem_count', 0)}", f"  Routes: {s.get('route_count', 0)}", f"  Dispatch entries: {s.get('dispatch_count', 0)}", f"  Rollback operations: {s.get('rollback_operation_count', 0)}", f"  Opens window: {s.get('opens_window')}", f"  Executes commands: {s.get('executes_commands')}"])
__all__ = ["QT_RUNTIME_SMOKE_WIRING_SUMMARY_SCHEMA_VERSION", "summarize_qt_runtime_smoke_wiring_bundle"]
