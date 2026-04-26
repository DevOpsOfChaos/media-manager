from __future__ import annotations

from collections.abc import Mapping
from typing import Any

HOME_INSIGHTS_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_home_insight(insight_id: str, title: str, *, level: str = "info", details: str = "", action_id: str | None = None) -> dict[str, object]:
    return {
        "schema_version": HOME_INSIGHTS_SCHEMA_VERSION,
        "kind": "home_insight",
        "insight_id": insight_id,
        "title": title,
        "level": level,
        "details": details,
        "action_id": action_id,
    }


def build_home_insights(home_state: Mapping[str, Any]) -> dict[str, object]:
    insights = []
    profiles = _mapping(_mapping(home_state.get("profiles")).get("summary"))
    runs = _mapping(_mapping(home_state.get("runs")).get("summary"))
    people = _mapping(home_state.get("people_review"))
    if profiles.get("profile_count", 0) == 0:
        insights.append(build_home_insight("no_profiles", "Create your first profile", level="info", action_id="open_profiles"))
    if runs.get("error_count", 0) > 0:
        insights.append(build_home_insight("run_errors", "Some runs need attention", level="warning", details=f"{runs.get('error_count')} runs reported errors.", action_id="open_runs"))
    if people.get("ready_for_gui"):
        insights.append(build_home_insight("people_ready", "People review bundle is ready", level="success", action_id="open_people_review"))
    if not insights:
        insights.append(build_home_insight("all_clear", "Everything looks ready", level="success"))
    return {
        "schema_version": HOME_INSIGHTS_SCHEMA_VERSION,
        "kind": "home_insights",
        "insights": insights,
        "insight_count": len(insights),
        "warning_count": sum(1 for item in insights if item["level"] == "warning"),
        "next_action_id": insights[0].get("action_id"),
    }


__all__ = ["HOME_INSIGHTS_SCHEMA_VERSION", "build_home_insight", "build_home_insights"]
