from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_batch_action_panel import build_batch_action_panel
from .gui_qt_job_launcher_plan import build_job_launcher_plan
from .gui_qt_page_storyboard import build_page_storyboard
from .gui_qt_people_review_dashboard import build_people_review_dashboard
from .gui_qt_profile_workbench import build_profile_workbench
from .gui_qt_release_gate import build_release_gate
from .gui_qt_run_history_workbench import build_run_history_workbench
from .gui_qt_settings_apply_plan import build_settings_apply_plan
from .gui_qt_theme_preview import build_theme_preview
from .gui_qt_user_journey_map import build_user_journey_map
from .gui_qt_visual_regression_manifest import build_visual_regression_manifest

PRODUCT_EXPERIENCE_SCHEMA_VERSION = "1.0"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_product_experience(
    *,
    shell_model: Mapping[str, Any] | None = None,
    people_page: Mapping[str, Any] | None = None,
    profiles: list[Mapping[str, Any]] | None = None,
    runs: list[Mapping[str, Any]] | None = None,
    current_settings: Mapping[str, Any] | None = None,
    desired_settings: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    shell = _mapping(shell_model)
    active_page = str(shell.get("active_page_id") or "dashboard")
    page_ids = [item.get("id") for item in shell.get("navigation", []) if isinstance(item, Mapping)] or None
    page_storyboard = build_page_storyboard(page_ids, active_page_id=active_page, language=str(shell.get("language") or "en"))
    people_dashboard = build_people_review_dashboard(_mapping(people_page or shell.get("page")))
    profile_workbench = build_profile_workbench(profiles or [])
    run_workbench = build_run_history_workbench(runs or [])
    settings_plan = build_settings_apply_plan(_mapping(current_settings), _mapping(desired_settings or current_settings or {}))
    theme_preview = build_theme_preview(_mapping(shell.get("theme")))
    launcher = build_job_launcher_plan(["media-manager-gui", "--active-page", active_page])
    batch_panel = build_batch_action_panel(selected_count=0)
    journey = build_user_journey_map("people-review")
    release_gate = build_release_gate(
        [
            {"id": "storyboard", "passed": page_storyboard["scene_count"] > 0},
            {"id": "theme", "passed": theme_preview["has_required_colors"]},
            {"id": "safe-launch", "passed": not launcher["executes_immediately"]},
        ]
    )
    manifest = build_visual_regression_manifest([page_storyboard, people_dashboard, profile_workbench, run_workbench, theme_preview])
    return {
        "schema_version": PRODUCT_EXPERIENCE_SCHEMA_VERSION,
        "kind": "qt_product_experience",
        "active_page_id": active_page,
        "page_storyboard": page_storyboard,
        "people_dashboard": people_dashboard,
        "profile_workbench": profile_workbench,
        "run_history_workbench": run_workbench,
        "settings_apply_plan": settings_plan,
        "theme_preview": theme_preview,
        "job_launcher_plan": launcher,
        "batch_action_panel": batch_panel,
        "user_journey": journey,
        "release_gate": release_gate,
        "visual_regression_manifest": manifest,
        "ready": bool(release_gate["ready"]),
    }


__all__ = ["PRODUCT_EXPERIENCE_SCHEMA_VERSION", "build_product_experience"]
