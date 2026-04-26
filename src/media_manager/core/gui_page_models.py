from __future__ import annotations

from collections.abc import Mapping
import json
from pathlib import Path
from typing import Any

from .gui_file_refs import build_local_file_ref, collect_asset_refs
from .gui_i18n import translate
from .gui_people_review_model import build_people_review_card_grid, build_people_review_detail_model

PAGE_MODEL_SCHEMA_VERSION = "2.0"


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
        "title": title,
        "subtitle": subtitle,
        "metrics": dict(metrics or {}),
        "actions": list(actions or []),
    }


def build_dashboard_page_model(home_state: Mapping[str, Any], *, language: str = "en") -> dict[str, object]:
    profiles = _as_mapping(home_state.get("profiles"))
    runs = _as_mapping(home_state.get("runs"))
    people = home_state.get("people_review")
    profile_summary = _as_mapping(profiles.get("summary"))
    run_summary = _as_mapping(runs.get("summary"))
    people_summary = _as_mapping(_as_mapping(people).get("summary")) if isinstance(people, Mapping) else {}
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
        "layout": "card_grid",
        "cards": cards,
        "suggested_next_step": home_state.get("suggested_next_step"),
    }


def build_runs_page_model(home_state: Mapping[str, Any], *, language: str = "en") -> dict[str, object]:
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
    return {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": "run-history",
        "title": translate("page.run-history.title", language=language),
        "description": translate("page.run-history.description", language=language),
        "kind": "table_page",
        "layout": "data_table",
        "columns": ["run_id", "command", "mode", "status", "exit_code", "review_candidate_count"],
        "rows": rows,
        "empty_state": "No run artifacts found yet." if not rows else None,
    }


def build_profiles_page_model(home_state: Mapping[str, Any], *, language: str = "en") -> dict[str, object]:
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
    return {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": "profiles",
        "title": translate("page.profiles.title", language=language),
        "description": translate("page.profiles.description", language=language),
        "kind": "table_page",
        "layout": "data_table",
        "columns": ["profile_id", "title", "command", "favorite", "valid"],
        "rows": rows,
        "empty_state": "No app profiles found yet." if not rows else None,
    }


def load_people_review_page_model(bundle_dir: str | Path | None, *, asset_limit: int = 200, language: str = "en") -> dict[str, object]:
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
        "layout": "master_detail_cards",
        "bundle_ref": build_local_file_ref(root, role="people_bundle") if root is not None else build_local_file_ref(None, role="people_bundle"),
        "manifest_status": _as_mapping(manifest).get("status") if manifest else None,
        "overview": dict(overview),
        "group_count": len(groups),
        "groups": [
            {
                "group_id": group.get("group_id"),
                "display_label": group.get("display_label"),
                "status": group.get("status"),
                "face_count": _as_mapping(group.get("counts")).get("face_count", 0),
                "included_faces": _as_mapping(group.get("counts")).get("included_faces", 0),
                "excluded_faces": _as_mapping(group.get("counts")).get("excluded_faces", 0),
                "primary_face_id": group.get("primary_face_id"),
            }
            for group in groups[:200]
        ],
        "asset_refs": collect_asset_refs(assets, bundle_dir=root, limit=asset_limit),
        "empty_state": translate("people.empty", language=language) if workspace is None else None,
    }
    page["card_grid"] = build_people_review_card_grid(page)
    page["detail"] = build_people_review_detail_model(page)
    return page


def build_people_review_page_model(home_state: Mapping[str, Any], *, asset_limit: int = 200, language: str = "en") -> dict[str, object]:
    people = home_state.get("people_review")
    bundle_dir = _as_mapping(people).get("bundle_dir") if isinstance(people, Mapping) else None
    return load_people_review_page_model(bundle_dir, asset_limit=asset_limit, language=language)


def build_settings_page_model(home_state: Mapping[str, Any], *, language: str = "en") -> dict[str, object]:
    manifest = _as_mapping(home_state.get("manifest_summary"))
    return {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": "settings",
        "title": translate("page.settings.title", language=language),
        "description": translate("page.settings.description", language=language),
        "kind": "settings_page",
        "layout": "settings_sections",
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
    }


def build_new_run_page_model(home_state: Mapping[str, Any], *, language: str = "en") -> dict[str, object]:
    return {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": "new-run",
        "title": translate("page.new-run.title", language=language),
        "description": translate("page.new-run.description", language=language),
        "kind": "new_run_page",
        "layout": "wizard_shell",
        "available_commands": _as_mapping(home_state.get("manifest_summary")).get("entrypoints", {}),
        "recommended_flow": ["Select profile", "Preview", "Review", "Apply only after confirmation"],
    }


def build_page_model(page_id: str, home_state: Mapping[str, Any], *, language: str = "en") -> dict[str, object]:
    normalized = str(page_id or "dashboard").strip().lower()
    if normalized == "dashboard":
        return build_dashboard_page_model(home_state, language=language)
    if normalized in {"run-history", "runs"}:
        return build_runs_page_model(home_state, language=language)
    if normalized == "profiles":
        return build_profiles_page_model(home_state, language=language)
    if normalized in {"people-review", "people"}:
        return build_people_review_page_model(home_state, language=language)
    if normalized in {"settings", "doctor"}:
        return build_settings_page_model(home_state, language=language)
    if normalized in {"new-run", "new run"}:
        return build_new_run_page_model(home_state, language=language)
    return {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": normalized,
        "title": normalized.replace("-", " ").title(),
        "kind": "placeholder_page",
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
