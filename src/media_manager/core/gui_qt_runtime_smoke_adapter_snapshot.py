from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_ADAPTER_SNAPSHOT_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _stable_hash(payload: Mapping[str, Any]) -> str:
    data = json.dumps(dict(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def build_qt_runtime_smoke_adapter_snapshot(bundle: Mapping[str, Any]) -> dict[str, object]:
    surface = _mapping(bundle.get("visible_surface"))
    validation = _mapping(bundle.get("validation"))
    payload = {
        "kind": bundle.get("kind"),
        "page_id": bundle.get("page_id"),
        "surface_summary": _mapping(surface.get("summary")),
        "validation_summary": _mapping(validation.get("summary")),
        "valid": validation.get("valid"),
    }
    return {
        "schema_version": QT_RUNTIME_SMOKE_ADAPTER_SNAPSHOT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_adapter_snapshot",
        "payload_hash": _stable_hash(payload),
        "payload": payload,
        "summary": {
            "valid": bool(validation.get("valid")),
            "ready_for_qt_runtime": bool(bundle.get("ready_for_qt_runtime")),
            "local_only": bool(_mapping(surface.get("summary")).get("local_only", True)),
        },
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }


__all__ = ["QT_RUNTIME_SMOKE_ADAPTER_SNAPSHOT_SCHEMA_VERSION", "build_qt_runtime_smoke_adapter_snapshot"]
