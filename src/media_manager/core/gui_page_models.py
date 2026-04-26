from __future__ import annotations

from collections.abc import Mapping
import json
from pathlib import Path
from typing import Any

from .gui_dashboard_model import build_dashboard_overview
from .gui_file_refs import build_local_file_ref, collect_asset_refs
from .gui_i18n import translate
from .gui_layout import build_page_layout
from .gui_modern_components import build_card, build_table_model
from .gui_people_review_editor_model import build_people_review_editor_state
from .gui_people_review_model import build_people_review_card_grid, build_people_review_detail_model
from .gui_profile_editor_model import build_profile_list_state
from .gui_run_history_model import build_run_history_page_state
from .gui_validation_panel import validation_panel_from_status

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


def build_dashboard_page_model(home_state: Mapping[str, Any], *, language: str = "en", density: str = "comfortable") -> dict[str, object]:
    overview = build_dashboard_overview(home_state, language=language)
    return {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": "dashboard",
        "title": translate("page.dashboard.title", language=language),
        "description": translate("page.dashboard.description", language=language),
        "kind": "dashboard_page",
        "layout": "hero_card_grid",
        "layout_contract": build_page_layout("dashboard", density=density),
        "hero": overview.get("hero"),
        "metric_tiles": overview.get("metrics", []),
        "cards": overview.get("cards", []),
        "suggested_next_step": home_state.get("suggested_next_step"),
    }


def build_runs_page_model(home_state: Mapping[str, Any], *, language: str = "en", density: str = "comfortable") -> dict[str, object]:
    state = build_run_history_page_state(home_state, language=language)
    table = _as_mapping(state.get("table"))
    return {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": "run-history",
        "title": translate("page.run-history.title", language=language),
        "description": translate("page.run-history.description", language=language),
        "kind": "table_page",
        "layout": "filterable_table",
        "layout_contract": build_page_layout("run-history", density=density),
        "filters": state.get("filters"),
        "table": dict(table),
        "columns": table.get("columns", []),
        "rows": table.get("rows", []),
        "empty_state": table.get("empty_state"),
    }


def build_profiles_page_model(home_state: Mapping[str, Any], *, language: str = "en", density: str = "comfortable") -> dict[str, object]:
    profile_state = build_profile_list_state(home_state, language=language)
    rows = []
    for item in _as_list(profile_state.get("items")):
        if not isinstance(item, Mapping):
            continue
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
    table = build_table_model("profiles", ["profile_id", "title", "command", "favorite", "valid"], rows, empty_state="No app profiles found yet.")
    return {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": "profiles",
        "title": translate("page.profiles.title", language=language),
        "description": translate("page.profiles.description", language=language),
        "kind": "table_page",
        "layout": "profile_card_table",
        "layout_contract": build_page_layout("profiles", density=density),
        "profile_state": profile_state,
        "table": table,
        "columns": table["columns"],
        "rows": table["rows"],
        "empty_state": table.get("empty_state"),
    }


def load_people_review_page_model(bundle_dir: str | Path | None, *, asset_limit: int = 200, language: str = "en", density: str = "comfortable") -> dict[str, object]:
    root = Path(bundle_dir) if bundle_dir is not None else None
    manifest = _read_json_object(root / "bundle_manifest.json") if root is not None else None
    workspace = _read_json_object(root / "people_review_workspace.json") if root is not None else None
    assets = _read_json_object(root / "assets" / "people_review_assets.json") if root is not None else None
    overview = _as_mapping(_as_mapping(workspace).get("overview")) if workspace else {}
    groups = [item for item in _as_list(_as_mapping(workspace).get("groups")) if isinstance(item, Mapping)] if workspace else []
    page: dict[str, object] = {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": "people-review",
        "title": translate("page.people-review.title", language=language),
        "description": translate("page.people-review.description", language=language),
        "kind": "people_review_page",
        "layout": "master_detail_gallery",
        "layout_contract": build_page_layout("people-review", density=density),
        "bundle_ref": build_local_file_ref(root, role="people_bundle") if root is not None else build_local_file_ref(None, role="people_bundle"),
        "manifest_status": _as_mapping(manifest).get("status") if manifest else None,
        "overview": dict(overview),
        "group_count": len(groups),
        "groups": [
            {
                "group_id": group.get("group_id"),
                "display_label": group.get("display_label"),
                "status": group.get("status"),
                "face_count": _as_mapping(group.get("counts")).get("face_count", group.get("face_count", 0)),
                "included_faces": _as_mapping(group.get("counts")).get("included_faces", group.get("included_faces", 0)),
                "excluded_faces": _as_mapping(group.get("counts")).get("excluded_faces", group.get("excluded_faces", 0)),
                "primary_face_id": group.get("primary_face_id"),
            }
            for group in groups[:200]
        ],
        "asset_refs": collect_asset_refs(assets, bundle_dir=root, limit=asset_limit),
        "empty_state": translate("people.empty", language=language) if workspace is None else None,
    }
    page["card_grid"] = build_people_review_card_grid(page)
    page["detail"] = build_people_review_detail_model(page)
    page["editor"] = build_people_review_editor_state(page, language=language)
    page["validation_panel"] = validation_panel_from_status(page)
    return page


def build_people_review_page_model(home_state: Mapping[str, Any], *, asset_limit: int = 200, language: str = "en", density: str = "comfortable") -> dict[str, object]:
    people = home_state.get("people_review")
    bundle_dir = _as_mapping(people).get("bundle_dir") if isinstance(people, Mapping) else None
    return load_people_review_page_model(bundle_dir, asset_limit=asset_limit, language=language, density=density)


def build_settings_page_model(home_state: Mapping[str, Any], *, language: str = "en", density: str = "comfortable") -> dict[str, object]:
    manifest = _as_mapping(home_state.get("manifest_summary"))
    return {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": "settings",
        "title": translate("page.settings.title", language=language),
        "description": translate("page.settings.description", language=language),
        "kind": "settings_page",
        "layout": "settings_sections",
        "layout_contract": build_page_layout("settings", density=density),
        "sections": [
            {"id": "environment", "title": "Environment", "items": [{"label": "Manifest schema", "value": manifest.get("schema_version")}, {"label": "Known commands", "value": manifest.get("command_count", 0)}]},
            {"id": "appearance", "title": translate("settings.theme", language=language), "items": [{"label": translate("settings.language", language=language), "value": language}, {"label": translate("settings.theme", language=language), "value": "modern-dark"}]},
            {"id": "privacy", "title": translate("settings.privacy", language=language), "items": [{"label": "People data", "value": translate("privacy.people", language=language)}]},
        ],
    }


def build_new_run_page_model(home_state: Mapping[str, Any], *, language: str = "en", density: str = "comfortable") -> dict[str, object]:
    return {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": "new-run",
        "title": translate("page.new-run.title", language=language),
        "description": translate("page.new-run.description", language=language),
        "kind": "new_run_page",
        "layout": "guided_wizard",
        "layout_contract": build_page_layout("new-run", density=density),
        "available_commands": _as_mapping(home_state.get("manifest_summary")).get("entrypoints", {}),
        "recommended_flow": ["Select profile", "Preview", "Review", "Apply only after confirmation"],
        "cards": [
            build_card("profile_start", "Start from a profile", subtitle="Use a saved preset for repeatable workflows.", icon="bookmark"),
            build_card("people_scan", "People scan", subtitle="Detect and review people groups locally.", icon="users"),
            build_card("doctor", "Run Doctor", subtitle="Validate paths and environment before apply.", icon="stethoscope"),
        ],
    }


def build_page_model(page_id: str, home_state: Mapping[str, Any], *, language: str = "en", density: str = "comfortable") -> dict[str, object]:
    normalized = str(page_id or "dashboard").strip().lower()
    if normalized == "dashboard":
        return build_dashboard_page_model(home_state, language=language, density=density)
    if normalized in {"run-history", "runs"}:
        return build_runs_page_model(home_state, language=language, density=density)
    if normalized == "profiles":
        return build_profiles_page_model(home_state, language=language, density=density)
    if normalized in {"people-review", "people"}:
        return build_people_review_page_model(home_state, language=language, density=density)
    if normalized in {"settings", "doctor"}:
        return build_settings_page_model(home_state, language=language, density=density)
    if normalized in {"new-run", "new run"}:
        return build_new_run_page_model(home_state, language=language, density=density)
    return {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": normalized,
        "title": normalized.replace("-", " ").title(),
        "kind": "placeholder_page",
        "layout_contract": build_page_layout(normalized, density=density),
        "empty_state": "This page is not implemented yet.",
    }


__all__ = [
    "PAGE_MODEL_SCHEMA_VERSION",
    "build_dashboard_page_model",
    "build_new_run_page_model",
    "build_page_model",
    "build_people_review_page_model",
    "build_profiles_page_model",
    "build_runs_page_model",
    "build_settings_page_model",
    "load_people_review_page_model",
]
