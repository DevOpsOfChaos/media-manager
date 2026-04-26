from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_MANUAL_SMOKE_PLAN_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _label(en: str, de: str, language: str) -> str:
    return de if language == "de" else en


def build_qt_runtime_manual_smoke_plan(
    handoff_manifest: Mapping[str, Any],
    *,
    language: str = "en",
) -> dict[str, object]:
    """Build a bilingual manual smoke checklist for the future visible Qt runtime."""

    lang = "de" if language == "de" else "en"
    active_page_id = _text(handoff_manifest.get("active_page_id"), "dashboard")
    readiness = _mapping(handoff_manifest.get("readiness"))
    privacy = _mapping(handoff_manifest.get("privacy"))
    contains_sensitive = bool(privacy.get("contains_sensitive_people_data"))
    checks = [
        {
            "id": "launch-window",
            "label": _label("Window opens without traceback", "Fenster öffnet ohne Traceback", lang),
            "required": True,
            "category": "startup",
        },
        {
            "id": "navigation-visible",
            "label": _label("Navigation rail and active page are visible", "Navigation und aktive Seite sind sichtbar", lang),
            "required": True,
            "category": "shell",
        },
        {
            "id": "no-auto-execution",
            "label": _label("No destructive action starts automatically", "Keine destruktive Aktion startet automatisch", lang),
            "required": True,
            "category": "safety",
        },
        {
            "id": "local-only",
            "label": _label("People data remains local-only", "People-Daten bleiben lokal", lang),
            "required": True,
            "category": "privacy",
        },
    ]
    if contains_sensitive or active_page_id == "people-review":
        checks.append(
            {
                "id": "people-sensitive-notice",
                "label": _label(
                    "People Review shows a sensitive local data notice",
                    "People Review zeigt einen Hinweis auf sensible lokale Daten",
                    lang,
                ),
                "required": True,
                "category": "privacy",
            }
        )
        checks.append(
            {
                "id": "face-assets-not-uploaded",
                "label": _label(
                    "Face assets are not uploaded or sent to telemetry",
                    "Face-Assets werden nicht hochgeladen und nicht an Telemetrie gesendet",
                    lang,
                ),
                "required": True,
                "category": "privacy",
            }
        )
    return {
        "schema_version": QT_RUNTIME_MANUAL_SMOKE_PLAN_SCHEMA_VERSION,
        "kind": "qt_runtime_manual_smoke_plan",
        "language": lang,
        "active_page_id": active_page_id,
        "checks": checks,
        "summary": {
            "check_count": len(checks),
            "required_check_count": sum(1 for check in checks if check.get("required")),
            "privacy_check_count": sum(1 for check in checks if check.get("category") == "privacy"),
            "contains_sensitive_people_data": contains_sensitive,
            "handoff_ready": bool(handoff_manifest.get("ready_for_manual_smoke")),
            "safety_problem_count": int(readiness.get("safety_problem_count") or 0),
            "validation_problem_count": int(readiness.get("validation_problem_count") or 0),
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_MANUAL_SMOKE_PLAN_SCHEMA_VERSION", "build_qt_runtime_manual_smoke_plan"]
