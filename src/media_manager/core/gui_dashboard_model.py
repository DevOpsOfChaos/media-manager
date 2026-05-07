from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_i18n import translate
from .gui_modern_components import build_action_button, build_card, build_metric_tile

DASHBOARD_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_dashboard_overview(home_state: Mapping[str, Any], *, language: str = "en") -> dict[str, object]:
    profiles = _mapping(home_state.get("profiles"))
    runs = _mapping(home_state.get("runs"))
    people = _mapping(home_state.get("people_review"))
    profile_summary = _mapping(profiles.get("summary"))
    run_summary = _mapping(runs.get("summary"))
    people_summary = _mapping(people.get("summary"))
    return {
        "schema_version": DASHBOARD_SCHEMA_VERSION,
        "kind": "dashboard_overview",
        "hero": {
            "title": translate("dashboard.hero.title", language=language, fallback=translate("page.dashboard.title", language=language)),
            "subtitle": translate("dashboard.hero.subtitle", language=language),
            "primary_action": build_action_button("open_guided_flows", translate("action.guided_flows", language=language, fallback="Guided workflows"), variant="primary", icon="compass"),
            "secondary_action": build_action_button("new_preview", translate("action.preview", language=language), variant="secondary", icon="sparkles"),
        },
        "metrics": [
            build_metric_tile("profiles", translate("dashboard.profiles", language=language), profile_summary.get("profile_count", 0), helper=f"{profile_summary.get('valid_count', 0)} valid"),
            build_metric_tile("runs", translate("dashboard.runs", language=language), run_summary.get("run_count", 0), helper=f"{run_summary.get('error_count', 0)} errors"),
            build_metric_tile("people", translate("dashboard.people", language=language), people_summary.get("group_count", people_summary.get("groups", 0)), helper=f"{people_summary.get('face_count', people_summary.get('faces', 0))} faces"),
        ],
        "cards": [
            build_card("guided_flows", translate("dashboard.guided_flows.title", language=language, fallback="Guided workflows"), subtitle=translate("dashboard.guided_flows.subtitle", language=language, fallback="Pick your goal and follow the steps. No CLI flags needed."), icon="compass", tone="success"),
            build_card("safe_preview", translate("dashboard.safe_preview.title", language=language), subtitle=translate("dashboard.safe_preview.subtitle", language=language), icon="shield", tone="success"),
            build_card("people_privacy", translate("dashboard.people_privacy.title", language=language), subtitle=translate("privacy.people", language=language), icon="lock", tone="warning"),
            build_card("recent_activity", translate("dashboard.recent_activity.title", language=language), subtitle=str(home_state.get("suggested_next_step") or ""), icon="activity"),
        ],
    }


__all__ = ["DASHBOARD_SCHEMA_VERSION", "build_dashboard_overview"]
