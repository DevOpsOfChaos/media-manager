from __future__ import annotations

from collections.abc import Mapping
from typing import Any

RELEASE_SMOKE_SCHEMA_VERSION = "1.0"


def build_release_smoke_scenarios(*, include_people: bool = True, language: str = "en") -> list[dict[str, object]]:
    scenarios = [
        {"id": "launch-dashboard", "title": "Launch dashboard", "page_id": "dashboard", "required": True},
        {"id": "switch-run-history", "title": "Switch to run history", "page_id": "run-history", "required": True},
        {"id": "open-settings", "title": "Open settings", "page_id": "settings", "required": True},
    ]
    if include_people:
        scenarios.extend([
            {"id": "open-people-review", "title": "Open people review", "page_id": "people-review", "required": True, "privacy_sensitive": True},
            {"id": "people-apply-preview", "title": "Open people apply preview", "page_id": "people-review", "required": False, "privacy_sensitive": True},
        ])
    for scenario in scenarios:
        scenario["language"] = language
        scenario["executes_commands"] = False
    return scenarios


def build_release_smoke_pack(*, shell_model: Mapping[str, Any] | None = None, include_people: bool = True, language: str = "en") -> dict[str, object]:
    scenarios = build_release_smoke_scenarios(include_people=include_people, language=language)
    active_page = shell_model.get("active_page_id") if isinstance(shell_model, Mapping) else None
    return {
        "schema_version": RELEASE_SMOKE_SCHEMA_VERSION,
        "kind": "release_smoke_pack",
        "active_page_id": active_page,
        "scenario_count": len(scenarios),
        "required_count": sum(1 for item in scenarios if item.get("required")),
        "privacy_sensitive_count": sum(1 for item in scenarios if item.get("privacy_sensitive")),
        "scenarios": scenarios,
    }


def validate_release_smoke_pack(pack: Mapping[str, Any]) -> dict[str, object]:
    scenarios = pack.get("scenarios") if isinstance(pack.get("scenarios"), list) else []
    problems = []
    if not scenarios:
        problems.append("no_scenarios")
    if any(item.get("executes_commands") for item in scenarios if isinstance(item, Mapping)):
        problems.append("scenario_executes_commands")
    return {
        "schema_version": RELEASE_SMOKE_SCHEMA_VERSION,
        "valid": not problems,
        "problem_count": len(problems),
        "problems": problems,
    }


__all__ = ["RELEASE_SMOKE_SCHEMA_VERSION", "build_release_smoke_pack", "build_release_smoke_scenarios", "validate_release_smoke_pack"]
