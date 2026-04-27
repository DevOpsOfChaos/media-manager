from __future__ import annotations
import hashlib, json
from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_START_SNAPSHOT_SCHEMA_VERSION = "1.0"

def _m(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}

def _hash(payload: Mapping[str, Any]) -> str:
    data = json.dumps(dict(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()

def build_qt_runtime_smoke_desktop_start_snapshot(bundle: Mapping[str, Any]) -> dict[str, object]:
    payload = {"kind": bundle.get("kind"), "ready": bundle.get("ready_for_manual_desktop_start"), "summary": _m(bundle.get("summary")), "audit_valid": _m(bundle.get("audit")).get("valid")}
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_START_SNAPSHOT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_start_snapshot",
        "payload_hash": _hash(payload),
        "payload": payload,
        "summary": {"ready_for_manual_desktop_start": bool(bundle.get("ready_for_manual_desktop_start")), "local_only": _m(bundle.get("summary")).get("local_only", True), "problem_count": _m(bundle.get("summary")).get("problem_count", 0)},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }

__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_START_SNAPSHOT_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_start_snapshot"]
