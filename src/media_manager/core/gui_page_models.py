from __future__ import annotations

from collections.abc import Mapping
import json
from pathlib import Path
from typing import Any

from .gui_dashboard_model import build_dashboard_overview
from .gui_empty_states import build_empty_state
from .gui_file_refs import build_local_file_ref, collect_asset_refs
from .gui_guided_flow_hub import build_guided_flow_hub_page_model
from .gui_i18n import translate
from .gui_people_review_model import build_people_review_card_grid, build_people_review_detail_model
from .gui_trip_manager import build_trip_manager_page_model
from .gui_people_onboarding import build_people_onboarding_page_model
from .gui_people_review_editor_model import build_people_review_editor_state
from .gui_people_review_queue import build_people_review_queue
from .gui_profile_editor_model import build_profile_form_schema, build_profile_list_state
from .gui_review_workbench_service import build_gui_review_workbench_service_bundle
from .gui_run_history_model import build_run_history_page_state
from .gui_run_wizard_model import build_run_wizard_model
from .gui_similar_comparison import build_similar_comparison_page_model
from .gui_table_state import build_table_state
from .gui_validation_panel import build_validation_panel

PAGE_MODEL_SCHEMA_VERSION = "3.0"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _read_json_object(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    resolved = Path(path)
    if not resolved.exists():
        return None
    value = json.loads(resolved.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else None


def _card(card_id: str, title: str, *, subtitle: str = "", metrics: Mapping[str, Any] | None = None, actions: list[dict[str, object]] | None = None) -> dict[str, object]:
    return {
        "id": card_id,
        "component": "metric_card",
        "title": title,
        "subtitle": subtitle,
        "metrics": dict(metrics or {}),
        "actions": list(actions or []),
    }


def build_dashboard_page_model(home_state: Mapping[str, Any], *, language: str = "en", density: str = "comfortable") -> dict[str, object]:
    profiles = _as_mapping(home_state.get("profiles"))
    runs = _as_mapping(home_state.get("runs"))
    people = home_state.get("people_review")
    profile_summary = _as_mapping(profiles.get("summary"))
    run_summary = _as_mapping(runs.get("summary"))
    people_summary = _as_mapping(_as_mapping(people).get("summary")) if isinstance(people, Mapping) else {}
    dashboard = build_dashboard_overview(home_state, language=language)
    cards = [
        _card(
            "profiles",
            translate("dashboard.profiles", language=language),
            subtitle=translate("page.profiles.description", language=language),
            metrics={
                "profiles": profile_summary.get("profile_count", 0),
                "valid": profile_summary.get("valid_count", 0),
                "favorites": profile_summary.get("favorite_count", 0),
            },
            actions=[{"id": "open_profiles", "label": translate("action.open", language=language), "page_id": "profiles"}],
        ),
        _card(
            "runs",
            translate("dashboard.runs", language=language),
            subtitle=translate("page.run-history.description", language=language),
            metrics={"runs": run_summary.get("run_count", 0), "errors": run_summary.get("error_count", 0)},
            actions=[{"id": "open_runs", "label": translate("action.open", language=language), "page_id": "run-history"}],
        ),
        _card(
            "people_review",
            translate("dashboard.people", language=language),
            subtitle=translate("page.people-review.description", language=language),
            metrics={
                "ready_for_gui": bool(_as_mapping(people).get("ready_for_gui")) if isinstance(people, Mapping) else False,
                "groups": people_summary.get("group_count", people_summary.get("groups", 0)),
                "faces": people_summary.get("face_count", people_summary.get("faces", 0)),
            },
            actions=[{"id": "open_people_review", "label": translate("action.review", language=language), "page_id": "people-review"}],
        ),
    ]
    return {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": "dashboard",
        "title": translate("page.dashboard.title", language=language),
        "description": translate("page.dashboard.description", language=language),
        "kind": "dashboard_page",
        "layout": "hero_card_grid",
        "layout_variant": "hero_card_grid_activity",
        "layout_contract": {
            "layout": "hero_card_grid",
            "variant": "hero_card_grid_activity",
            "density": density,
            "regions": ["hero", "cards", "activity", "quick_actions"],
        },
        "density": density,
        "hero": dashboard.get("hero", {}),
        "cards": cards,
        "activity": dashboard.get("activity", {}),
        "quick_actions": dashboard.get("quick_actions", []),
        "validation": build_validation_panel(page_id="dashboard", page_model={"cards": cards}, language=language),
        "suggested_next_step": home_state.get("suggested_next_step"),
    }


def build_runs_page_model(home_state: Mapping[str, Any], *, language: str = "en", query: str = "", density: str = "comfortable") -> dict[str, object]:
    runs = _as_mapping(home_state.get("runs"))
    items = [item for item in _as_list(runs.get("items")) if isinstance(item, Mapping)]
    rows = []
    for item in items:
        rows.append(
            {
                "run_id": item.get("run_id"),
                "command": item.get("command"),
                "mode": item.get("mode"),
                "status": item.get("status"),
                "exit_code": item.get("exit_code"),
                "review_candidate_count": item.get("review_candidate_count", 0),
                "path_ref": build_local_file_ref(item.get("path"), role="run_dir"),
            }
        )
    table_state = build_table_state(table_id="run-history", columns=["run_id", "command", "mode", "status", "exit_code", "review_candidate_count"], rows=rows, query=query, sort_key="run_id", descending=True)
    return {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": "run-history",
        "title": translate("page.run-history.title", language=language),
        "description": translate("page.run-history.description", language=language),
        "kind": "table_page",
        "layout": "data_table_with_filters",
        "density": density,
        "columns": table_state["columns"],
        "rows": table_state["rows"],
        "table_state": table_state,
        "run_history_model": build_run_history_page_state(home_state, language=language),
        "empty_state": build_empty_state("run-history", language=language) if not rows else None,
    }


def build_profiles_page_model(home_state: Mapping[str, Any], *, language: str = "en", query: str = "", density: str = "comfortable") -> dict[str, object]:
    profiles = _as_mapping(home_state.get("profiles"))
    items = [item for item in _as_list(profiles.get("items")) if isinstance(item, Mapping)]
    rows = []
    for item in items:
        rows.append(
            {
                "profile_id": item.get("profile_id"),
                "title": item.get("title"),
                "command": item.get("command"),
                "favorite": item.get("favorite"),
                "valid": item.get("valid"),
                "path_ref": build_local_file_ref(item.get("path"), role="profile"),
            }
        )
    table_state = build_table_state(table_id="profiles", columns=["profile_id", "title", "command", "favorite", "valid"], rows=rows, query=query, sort_key="title")
    return {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": "profiles",
        "title": translate("page.profiles.title", language=language),
        "description": translate("page.profiles.description", language=language),
        "kind": "profiles_page",
        "layout": "table_with_editor_preview",
        "density": density,
        "columns": table_state["columns"],
        "rows": table_state["rows"],
        "table_state": table_state,
        "profile_editor": build_profile_list_state(home_state, language=language),
        "profile_form_schema": build_profile_form_schema(command="people", language=language),
        "empty_state": build_empty_state("profiles", language=language) if not rows else None,
    }


def load_people_review_page_model(bundle_dir: str | Path | None, *, asset_limit: int = 200, language: str = "en", query: str = "", selected_group_id: str | None = None, density: str = "comfortable") -> dict[str, object]:
    root = Path(bundle_dir) if bundle_dir is not None else None
    manifest = _read_json_object(root / "bundle_manifest.json") if root is not None else None
    workspace = _read_json_object(root / "people_review_workspace.json") if root is not None else None
    assets = _read_json_object(root / "assets" / "people_review_assets.json") if root is not None else None
    overview = _as_mapping(_as_mapping(workspace).get("overview")) if workspace else {}
    groups = [item for item in _as_list(_as_mapping(workspace).get("groups")) if isinstance(item, Mapping)] if workspace else []
    queue = build_people_review_queue(groups, query=query)
    selected = selected_group_id or (queue["groups"][0].get("group_id") if queue.get("groups") else None)
    page: dict[str, object] = {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": "people-review",
        "title": translate("page.people-review.title", language=language),
        "description": translate("page.people-review.description", language=language),
        "kind": "people_review_page",
        "layout": "review_queue_master_detail",
        "density": density,
        "bundle_ref": build_local_file_ref(root, role="people_bundle") if root is not None else build_local_file_ref(None, role="people_bundle"),
        "manifest_status": _as_mapping(manifest).get("status") if manifest else None,
        "overview": dict(overview),
        "query": query,
        "selected_group_id": selected,
        "group_count": len(groups),
        "groups": queue.get("groups", []),
        "queue": queue,
        "asset_refs": collect_asset_refs(assets, bundle_dir=root, limit=asset_limit),
        "empty_state": build_empty_state("people-review", language=language) if workspace is None else None,
    }
    page["card_grid"] = build_people_review_card_grid(page)
    page["detail"] = build_people_review_detail_model({**page, "selected_group_id": selected})
    page["editor"] = build_people_review_editor_state(page, selected_group_id=selected, language=language)
    page["validation"] = build_validation_panel(page_id="people-review", page_model=page, language=language)
    return page


def build_people_review_page_model(home_state: Mapping[str, Any], *, asset_limit: int = 200, language: str = "en", query: str = "", selected_group_id: str | None = None, density: str = "comfortable") -> dict[str, object]:
    people = home_state.get("people_review")
    bundle_dir = _as_mapping(people).get("bundle_dir") if isinstance(people, Mapping) else None
    return load_people_review_page_model(bundle_dir, asset_limit=asset_limit, language=language, query=query, selected_group_id=selected_group_id, density=density)


def build_review_workbench_page_model(home_state: Mapping[str, Any], *, language: str = "en", query: str = "", density: str = "comfortable") -> dict[str, object]:
    people = _as_mapping(home_state.get("people_review")) if isinstance(home_state.get("people_review"), Mapping) else {}
    bundle_dir = people.get("bundle_dir")
    service = build_gui_review_workbench_service_bundle(
        people_bundle_dir=bundle_dir if isinstance(bundle_dir, (str, Path)) else None,
        lane_query=query,
    )
    adapter = _as_mapping(service.get("qt_adapter_package"))
    widget_binding_plan = _as_mapping(service.get("qt_widget_binding_plan"))
    widget_skeleton = _as_mapping(service.get("qt_widget_skeleton"))
    interaction_plan = _as_mapping(service.get("interaction_plan"))
    callback_mount_plan = _as_mapping(service.get("callback_mount_plan"))
    apply_preview = _as_mapping(service.get("apply_preview"))
    confirmation_dialog = _as_mapping(service.get("confirmation_dialog"))
    apply_executor_contract = _as_mapping(service.get("apply_executor_contract"))
    executor_handoff_panel = _as_mapping(service.get("executor_handoff_panel"))
    stateful_rebuild_loop = _as_mapping(service.get("stateful_rebuild_loop"))
    stateful_callback_plan = _as_mapping(service.get("stateful_callback_plan"))
    summary = _as_mapping(service.get("summary"))
    return {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": "review-workbench",
        "title": "Review Workbench",
        "description": "One desktop page for duplicate, similar-image, people, and apply-readiness review queues.",
        "kind": "review_workbench_page",
        "layout": "review_workbench_table_detail",
        "density": density,
        "language": language,
        "query": query,
        "workbench_service": service,
        "qt_adapter_package": adapter,
        "qt_widget_binding_plan": widget_binding_plan,
        "qt_widget_skeleton": widget_skeleton,
        "interaction_plan": interaction_plan,
        "callback_mount_plan": callback_mount_plan,
        "apply_preview": apply_preview,
        "confirmation_dialog": confirmation_dialog,
        "apply_executor_contract": apply_executor_contract,
        "executor_handoff_panel": executor_handoff_panel,
        "stateful_rebuild_loop": stateful_rebuild_loop,
        "stateful_callback_plan": stateful_callback_plan,
        "view_model": _as_mapping(service.get("view_model")),
        "table_model": _as_mapping(service.get("table_model")),
        "action_plan": _as_mapping(service.get("action_plan")),
        "summary": dict(summary),
        "empty_state": build_empty_state("review-workbench", language=language) if summary.get("lane_count", 0) == 0 else None,
        "validation": build_validation_panel(page_id="review-workbench", page_model={"summary": summary, "adapter": adapter}, language=language),
    }


def build_settings_page_model(home_state: Mapping[str, Any], *, language: str = "en", density: str = "comfortable") -> dict[str, object]:
    manifest = _as_mapping(home_state.get("manifest_summary"))
    return {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": "settings",
        "title": translate("page.settings.title", language=language),
        "description": translate("page.settings.description", language=language),
        "kind": "settings_page",
        "layout": "settings_sections",
        "density": density,
        "sections": [
            {
                "id": "environment",
                "title": "Environment",
                "items": [
                    {"label": "Manifest schema", "value": manifest.get("schema_version")},
                    {"label": "Known commands", "value": manifest.get("command_count", 0)},
                ],
            },
            {
                "id": "appearance",
                "title": translate("settings.theme", language=language),
                "items": [
                    {"label": translate("settings.language", language=language), "value": language},
                    {"label": translate("settings.theme", language=language), "value": "modern-dark"},
                ],
            },
            {
                "id": "privacy",
                "title": translate("settings.privacy", language=language),
                "items": [
                    {"label": "People data", "value": translate("privacy.people", language=language)},
                ],
            },
        ],
        "validation": build_validation_panel(page_id="settings", page_model={}, language=language),
    }


def build_new_run_page_model(home_state: Mapping[str, Any], *, language: str = "en", density: str = "comfortable") -> dict[str, object]:
    return {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": "new-run",
        "title": translate("page.new-run.title", language=language),
        "description": translate("page.new-run.description", language=language),
        "kind": "new_run_page",
        "layout": "guided_wizard",
        "density": density,
        "wizard": build_run_wizard_model(language=language, selected_command="people"),
        "available_commands": _as_mapping(home_state.get("manifest_summary")).get("entrypoints", {}),
        "recommended_flow": ["Select profile", "Preview", "Review", "Apply only after confirmation"],
    }


def build_page_model(page_id: str, home_state: Mapping[str, Any], *, language: str = "en", density: str = "comfortable", query: str = "", selected_group_id: str | None = None) -> dict[str, object]:
    normalized = str(page_id or "dashboard").strip().lower().replace("_", "-")
    normalized = {"settings-doctor": "settings", "doctor": "settings", "runs": "run-history", "history": "run-history", "people": "people-review", "new run": "new-run"}.get(normalized, normalized)
    if normalized == "dashboard":
        page = build_dashboard_page_model(home_state, language=language, density=density)
        page["layout"] = page.get("layout_variant", "hero_card_grid_activity")
        return page
    if normalized in {"run-history", "runs"}:
        return build_runs_page_model(home_state, language=language, query=query, density=density)
    if normalized == "profiles":
        return build_profiles_page_model(home_state, language=language, query=query, density=density)
    if normalized in {"people-review", "people"}:
        return build_people_review_page_model(home_state, language=language, query=query, selected_group_id=selected_group_id, density=density)
    if normalized == "review-workbench":
        return build_review_workbench_page_model(home_state, language=language, query=query, density=density)
    if normalized in {"settings", "doctor"}:
        return build_settings_page_model(home_state, language=language, density=density)
    if normalized in {"new-run", "new run"}:
        return build_new_run_page_model(home_state, language=language, density=density)
    if normalized == "similar-comparison":
        return build_similar_comparison_page_model(
            home_state,
            language=language,
        )
    if normalized in {"people-setup", "people setup"}:
        return build_people_onboarding_page_model(home_state, language=language)
    if normalized in {"guided-flows", "guided"}:
        return build_guided_flow_hub_page_model(home_state, language=language)
    if normalized in {"trip-manager", "trips", "trip"}:
        return build_trip_manager_page_model(home_state, language=language)
    return {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": normalized,
        "title": normalized.replace("-", " ").title(),
        "kind": "placeholder_page",
        "empty_state": build_empty_state(normalized, language=language),
    }


__all__ = [
    "PAGE_MODEL_SCHEMA_VERSION",
    "build_dashboard_page_model",
    "build_new_run_page_model",
    "build_page_model",
    "build_people_review_page_model",
    "build_profiles_page_model",
    "build_review_workbench_page_model",
    "build_runs_page_model",
    "build_settings_page_model",
    "load_people_review_page_model",
]
