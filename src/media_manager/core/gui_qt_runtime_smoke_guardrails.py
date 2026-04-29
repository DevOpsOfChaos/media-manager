from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_GUARDRAILS_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _bool_from_capabilities(payload: Mapping[str, Any], key: str, default: bool) -> bool:
    capabilities = _mapping(payload.get("capabilities"))
    return bool(capabilities.get(key, default))


def evaluate_qt_runtime_smoke_guardrails(*payloads: Mapping[str, Any]) -> dict[str, object]:
    """Evaluate the hard safety contract for guarded Runtime Smoke integration.

    This remains metadata-only. It checks that every supplied layer is headless,
    local-only, non-executing, and does not require PySide6 to build.
    """

    problems: list[dict[str, object]] = []
    checked = 0
    for index, payload in enumerate(payloads):
        if not isinstance(payload, Mapping):
            continue
        checked += 1
        kind = str(payload.get("kind") or f"payload-{index + 1}")
        if _bool_from_capabilities(payload, "requires_pyside6", False):
            problems.append({"kind": kind, "code": "requires_pyside6"})
        if _bool_from_capabilities(payload, "opens_window", False):
            problems.append({"kind": kind, "code": "opens_window"})
        if _bool_from_capabilities(payload, "executes_commands", False):
            problems.append({"kind": kind, "code": "executes_commands"})
        if not _bool_from_capabilities(payload, "local_only", True):
            problems.append({"kind": kind, "code": "not_local_only"})
    return {
        "schema_version": QT_RUNTIME_SMOKE_GUARDRAILS_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_guardrails",
        "valid": not problems,
        "checked_payload_count": checked,
        "problem_count": len(problems),
        "problems": problems,
        "summary": {
            "checked_payload_count": checked,
            "problem_count": len(problems),
            "requires_pyside6": False,
            "opens_window": False,
            "executes_commands": False,
            "local_only": not problems,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_GUARDRAILS_SCHEMA_VERSION", "evaluate_qt_runtime_smoke_guardrails"]
