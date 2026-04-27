from __future__ import annotations
import hashlib, json
from collections.abc import Mapping
from typing import Any
QT_RUNTIME_SMOKE_SHELL_SNAPSHOT_SCHEMA_VERSION = "1.0"
def _mapping(value: object) -> Mapping[str, Any]: return value if isinstance(value, Mapping) else {}
def _hash(payload: Mapping[str, Any]) -> str: return hashlib.sha256(json.dumps(dict(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
def build_qt_runtime_smoke_shell_snapshot(shell_bundle: Mapping[str, Any]) -> dict[str, object]:
    readiness = _mapping(shell_bundle.get("readiness")); registration = _mapping(shell_bundle.get("shell_registration")); payload = {"kind": shell_bundle.get("kind"), "page_id": registration.get("page_id"), "registration_summary": _mapping(registration.get("summary")), "readiness_summary": _mapping(readiness.get("summary")), "ready": readiness.get("ready")}
    return {"schema_version": QT_RUNTIME_SMOKE_SHELL_SNAPSHOT_SCHEMA_VERSION, "kind": "qt_runtime_smoke_shell_snapshot", "payload_hash": _hash(payload), "payload": payload, "summary": {"ready": bool(readiness.get("ready")), "problem_count": int(readiness.get("problem_count") or 0), "local_only": _mapping(readiness.get("summary")).get("local_only", True)}, "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True}}
__all__ = ["QT_RUNTIME_SMOKE_SHELL_SNAPSHOT_SCHEMA_VERSION", "build_qt_runtime_smoke_shell_snapshot"]
