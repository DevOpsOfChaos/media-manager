from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

QT_RUNTIME_BUILD_SNAPSHOT_SCHEMA_VERSION = "1.0"


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_qt_runtime_build_snapshot(build_plan: Mapping[str, Any]) -> dict[str, object]:
    """Build a stable snapshot for build-step regression checks."""

    steps = [dict(step) for step in _list(build_plan.get("steps")) if isinstance(step, Mapping)]
    compact = {
        "kind": build_plan.get("kind"),
        "root_id": build_plan.get("root_id"),
        "step_ids": [step.get("step_id") for step in steps],
        "operations": [step.get("operation") for step in steps],
        "summary": dict(_mapping(build_plan.get("summary"))),
    }
    payload = json.dumps(compact, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return {
        "schema_version": QT_RUNTIME_BUILD_SNAPSHOT_SCHEMA_VERSION,
        "kind": "qt_runtime_build_snapshot",
        "root_id": build_plan.get("root_id"),
        "step_count": len(steps),
        "payload_hash": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "payload": compact,
    }


__all__ = ["QT_RUNTIME_BUILD_SNAPSHOT_SCHEMA_VERSION", "build_qt_runtime_build_snapshot"]
