from __future__ import annotations

from collections.abc import Mapping
import json
from pathlib import Path
from typing import Any

from .gui_file_refs import build_local_file_ref, collect_asset_refs

PAGE_MODEL_SCHEMA_VERSION = "1.0"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_text(value: object) -> str:
    return value if isinstance(value, str) else ""


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


def build_dashboard_page_model(home_state: Mapping[str, Any]) -> dict[str, object]:
    profiles = _as_mapping(home_state.get("profiles"))
    runs = _as_mapping(home_state.get("runs"))
    people = home_state.get("people_review")
    profile_summary = _as_mapping(profiles.get("summary"))
    run_summary = _as_mapping(runs.get("summary"))
    people_summary = _as_mapping(_as_mapping(people).get("summary")) if isinstance(people, Mapping) else {}
    cards = [
        _card(
            "profiles",
            "Profiles",
            subtitle="Saved presets for repeatable workflows.",
            metrics={
                "profiles": profile_summary.get("profile_count", 0),
                "valid": profile_summary.get("valid_count", 0),
                "favorites": profile_summary.get("favorite_count", 0),
            },
        ),
        _card(
            "runs",
            "Recent runs",
            subtitle="Latest run artifact folders.",
            metrics={"runs": run_summary.get("run_count", 0), "errors": run_summary.get("error_count", 0)},
        ),
        _card(
            "people_review",
            "People review",
            subtitle="Curate detected people groups before training the local catalog.",
            metrics={
                "ready_for_gui": bool(_as_mapping(people).get("ready_for_gui")) if isinstance(people, Mapping) else False,
                "groups": people_summary.get("group_count", people_summary.get("groups", 0)),
                "faces": people_summary.get("face_count", people_summary.get("faces", 0)),
            },
        ),
    ]
    return {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": "dashboard",
        "title": "Dashboard",
        "kind": "dashboard_page",
        "cards": cards,
        "suggested_next_step": home_state.get("suggested_next_step"),
    }


def build_runs_page_model(home_state: Mapping[str, Any]) -> dict[str, object]:
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
        "title": "Run history",
        "kind": "table_page",
        "columns": ["run_id", "command", "mode", "status", "exit_code", "review_candidate_count"],
        "rows": rows,
        "empty_state": "No run artifacts found yet." if not rows else None,
    }


def build_profiles_page_model(home_state: Mapping[str, Any]) -> dict[str, object]:
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
        "title": "Profiles",
        "kind": "table_page",
        "columns": ["profile_id", "title", "command", "favorite", "valid"],
        "rows": rows,
        "empty_state": "No app profiles found yet." if not rows else None,
    }


def load_people_review_page_model(bundle_dir: str | Path | None, *, asset_limit: int = 200) -> dict[str, object]:
    root = Path(bundle_dir) if bundle_dir is not None else None
    manifest = _read_json_object(root / "bundle_manifest.json") if root is not None else None
    workspace = _read_json_object(root / "people_review_workspace.json") if root is not None else None
    assets = _read_json_object(root / "assets" / "people_review_assets.json") if root is not None else None
    overview = _as_mapping(_as_mapping(workspace).get("overview")) if workspace else {}
    groups = [item for item in _as_list(_as_mapping(workspace).get("groups")) if isinstance(item, Mapping)] if workspace else []
    return {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": "people-review",
        "title": "People review",
        "kind": "people_review_page",
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
        "empty_state": "Open or create a people review bundle." if workspace is None else None,
    }


def build_people_review_page_model(home_state: Mapping[str, Any], *, asset_limit: int = 200) -> dict[str, object]:
    people = home_state.get("people_review")
    bundle_dir = _as_mapping(people).get("bundle_dir") if isinstance(people, Mapping) else None
    return load_people_review_page_model(bundle_dir, asset_limit=asset_limit)


def build_settings_page_model(home_state: Mapping[str, Any]) -> dict[str, object]:
    manifest = _as_mapping(home_state.get("manifest_summary"))
    return {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": "settings",
        "title": "Settings / Doctor",
        "kind": "settings_page",
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
                "id": "privacy",
                "title": "Privacy",
                "items": [
                    {"label": "People data", "value": "Local only; face crops and embeddings stay in local artifacts."},
                ],
            },
        ],
    }


def build_new_run_page_model(home_state: Mapping[str, Any]) -> dict[str, object]:
    return {
        "schema_version": PAGE_MODEL_SCHEMA_VERSION,
        "page_id": "new-run",
        "title": "New run",
        "kind": "new_run_page",
        "available_commands": _as_mapping(home_state.get("manifest_summary")).get("entrypoints", {}),
        "recommended_flow": ["Select profile", "Preview", "Review", "Apply only after confirmation"],
    }


def build_page_model(page_id: str, home_state: Mapping[str, Any]) -> dict[str, object]:
    normalized = str(page_id or "dashboard").strip().lower()
    if normalized == "dashboard":
        return build_dashboard_page_model(home_state)
    if normalized in {"run-history", "runs"}:
        return build_runs_page_model(home_state)
    if normalized == "profiles":
        return build_profiles_page_model(home_state)
    if normalized in {"people-review", "people"}:
        return build_people_review_page_model(home_state)
    if normalized in {"settings", "doctor"}:
        return build_settings_page_model(home_state)
    if normalized in {"new-run", "new run"}:
        return build_new_run_page_model(home_state)
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
