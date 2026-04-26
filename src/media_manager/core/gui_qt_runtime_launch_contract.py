from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_LAUNCH_CONTRACT_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def build_qt_runtime_launch_contract(
    handoff_manifest: Mapping[str, Any],
    *,
    entry_point: str = "media-manager-gui",
    language: str = "en",
    theme: str = "modern-dark",
) -> dict[str, object]:
    """Build a manual-only launch contract for the future visible Qt runtime."""

    active_page_id = _text(handoff_manifest.get("active_page_id"), "dashboard")
    readiness = _mapping(handoff_manifest.get("readiness"))
    privacy = _mapping(handoff_manifest.get("privacy"))
    requirements = _mapping(handoff_manifest.get("runtime_requirements"))
    argv = [
        entry_point,
        "--active-page",
        active_page_id,
        "--language",
        _text(language, "en"),
        "--theme",
        _text(theme, "modern-dark"),
    ]
    return {
        "schema_version": QT_RUNTIME_LAUNCH_CONTRACT_SCHEMA_VERSION,
        "kind": "qt_runtime_launch_contract",
        "active_page_id": active_page_id,
        "entry_point": entry_point,
        "argv": argv,
        "display_command": " ".join(argv),
        "preflight": [
            {
                "id": "handoff-ready",
                "label": "Runtime handoff is ready",
                "passed": bool(handoff_manifest.get("ready_for_manual_smoke")),
                "required": True,
            },
            {
                "id": "no-safety-problems",
                "label": "No runtime safety problems",
                "passed": int(readiness.get("safety_problem_count") or 0) == 0,
                "required": True,
            },
            {
                "id": "no-validation-problems",
                "label": "No runtime validation problems",
                "passed": int(readiness.get("validation_problem_count") or 0) == 0,
                "required": True,
            },
            {
                "id": "local-only",
                "label": "Sensitive people data remains local",
                "passed": bool(privacy.get("local_only", True)) and privacy.get("network_required") is False,
                "required": True,
            },
        ],
        "runtime_requirements": {
            **dict(requirements),
            "requires_pyside6_to_open_window": True,
            "install_hint": 'python -m pip install -e ".[gui]"',
        },
        "execution_policy": {
            "mode": "manual_only",
            "executes_immediately": False,
            "opens_window": False,
            "requires_confirmation": True,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
        "ready_for_launch_attempt": all(item["passed"] for item in [
            {"passed": bool(handoff_manifest.get("ready_for_manual_smoke"))},
            {"passed": int(readiness.get("safety_problem_count") or 0) == 0},
            {"passed": int(readiness.get("validation_problem_count") or 0) == 0},
            {"passed": bool(privacy.get("local_only", True)) and privacy.get("network_required") is False},
        ]),
    }


def summarize_qt_runtime_launch_contract(contract: Mapping[str, Any]) -> str:
    execution = _mapping(contract.get("execution_policy"))
    return "\n".join(
        [
            "Qt runtime launch contract",
            f"  Active page: {contract.get('active_page_id')}",
            f"  Ready for launch attempt: {contract.get('ready_for_launch_attempt')}",
            f"  Command: {contract.get('display_command')}",
            f"  Execution mode: {execution.get('mode')}",
            f"  Opens window now: {execution.get('opens_window')}",
        ]
    )


__all__ = [
    "QT_RUNTIME_LAUNCH_CONTRACT_SCHEMA_VERSION",
    "build_qt_runtime_launch_contract",
    "summarize_qt_runtime_launch_contract",
]
