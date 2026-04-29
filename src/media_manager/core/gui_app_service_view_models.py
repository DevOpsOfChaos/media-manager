from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .app_services import build_app_home_state, read_json_object, write_json_object
from .gui_i18n import normalize_language, translate
from .gui_review_workbench_view_models import build_ui_review_workbench_view_model
from .gui_run_history_model import build_run_history_page_state

APP_SERVICE_VIEW_MODELS_SCHEMA_VERSION = "1.0"
APP_SERVICE_VIEW_MODELS_KIND = "ui_app_service_view_models"


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


def _first_mapping(items: object) -> Mapping[str, Any]:
    for item in _as_list(items):
        if isinstance(item, Mapping):
            return item
    return {}


def _runs_from_home_state(home_state: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    runs = _as_mapping(home_state.get("runs"))
    return [item for item in _as_list(runs.get("items")) if isinstance(item, Mapping)]


def _count_matching_runs(runs: list[Mapping[str, Any]], *needles: str) -> int:
    lowered = tuple(needle.lower() for needle in needles if needle)
    count = 0
    for run in runs:
        command = str(run.get("command") or "").lower()
        run_id = str(run.get("run_id") or "").lower()
        if any(needle in command or needle in run_id for needle in lowered):
            count += 1
    return count


def _latest_matching_run(runs: list[Mapping[str, Any]], *needles: str) -> Mapping[str, Any]:
    lowered = tuple(needle.lower() for needle in needles if needle)
    for run in runs:
        command = str(run.get("command") or "").lower()
        run_id = str(run.get("run_id") or "").lower()
        if any(needle in command or needle in run_id for needle in lowered):
            return run
    return {}


def _profile_summary(home_state: Mapping[str, Any]) -> Mapping[str, Any]:
    return _as_mapping(_as_mapping(home_state.get("profiles")).get("summary"))


def _run_summary(home_state: Mapping[str, Any]) -> Mapping[str, Any]:
    return _as_mapping(_as_mapping(home_state.get("runs")).get("summary"))


def _people_summary(home_state: Mapping[str, Any]) -> Mapping[str, Any]:
    return _as_mapping(_as_mapping(home_state.get("people_review")).get("summary"))


def build_ui_home_view_model(home_state: Mapping[str, Any], *, language: str = "en") -> dict[str, object]:
    profile_summary = _profile_summary(home_state)
    run_summary = _run_summary(home_state)
    people_summary = _people_summary(home_state)
    return {
        "kind": "ui_home_view_model",
        "title": translate("page.dashboard.title", language=language),
        "subtitle": translate("dashboard.hero.subtitle", language=language),
        "primary_action": {"id": "start-preview", "label": translate("action.preview", language=language), "page_id": "new-run"},
        "secondary_action": {"id": "open-run-history", "label": translate("nav.run-history", language=language), "page_id": "run-history"},
        "metrics": {
            "profiles": {"label": translate("dashboard.profiles", language=language), "value": _as_int(profile_summary.get("profile_count")), "helper": f"{_as_int(profile_summary.get('valid_count'))} valid"},
            "recent_runs": {"label": translate("dashboard.runs", language=language), "value": _as_int(run_summary.get("run_count")), "helper": f"{_as_int(run_summary.get('error_count'))} errors"},
            "people_review": {"label": translate("dashboard.people", language=language), "value": _as_int(people_summary.get("group_count", people_summary.get("groups"))), "helper": f"{_as_int(people_summary.get('face_count', people_summary.get('faces')))} faces"},
        },
        "next_step": str(home_state.get("suggested_next_step") or ""),
    }


def build_scan_setup_view_model(home_state: Mapping[str, Any], *, language: str = "en") -> dict[str, object]:
    manifest = _as_mapping(home_state.get("manifest_summary"))
    entrypoints = _as_mapping(manifest.get("entrypoints"))
    profile_summary = _profile_summary(home_state)
    return {
        "kind": "ui_scan_setup_view_model",
        "title": translate("page.new-run.title", language=language),
        "description": translate("page.new-run.description", language=language),
        "preview_first": True,
        "executes_commands": False,
        "available_workflows": [
            {"id": "duplicates", "label": "Find duplicates", "entrypoint": entrypoints.get("duplicates"), "enabled": bool(entrypoints.get("duplicates")), "risk": "review_required"},
            {"id": "similar-images", "label": "Find similar images", "entrypoint": entrypoints.get("duplicates"), "enabled": bool(entrypoints.get("duplicates")), "risk": "review_required"},
            {"id": "people", "label": translate("nav.people-review", language=language), "entrypoint": entrypoints.get("people"), "enabled": bool(entrypoints.get("people")), "risk": "sensitive_local_data"},
            {"id": "organize", "label": "Organize media", "entrypoint": entrypoints.get("organize"), "enabled": bool(entrypoints.get("organize")), "risk": "preview_required"},
        ],
        "profile_status": {"profile_count": _as_int(profile_summary.get("profile_count")), "valid_count": _as_int(profile_summary.get("valid_count")), "has_profiles": _as_int(profile_summary.get("profile_count")) > 0},
        "safety_notes": [
            "Preview does not change files.",
            "Apply actions must stay disabled until a reviewed decision model exists.",
            translate("privacy.people", language=language),
        ],
    }


def build_duplicate_review_view_model(home_state: Mapping[str, Any], *, language: str = "en") -> dict[str, object]:
    runs = _runs_from_home_state(home_state)
    latest = _latest_matching_run(runs, "duplicate", "duplicates")
    review_candidates = sum(_as_int(run.get("review_candidate_count")) for run in runs if "duplicate" in str(run.get("command") or run.get("run_id") or "").lower())
    return {
        "kind": "ui_duplicate_review_view_model",
        "title": "Duplicate review",
        "description": "Review exact duplicate groups before any apply action.",
        "latest_run": dict(latest) if latest else None,
        "run_count": _count_matching_runs(runs, "duplicate", "duplicates"),
        "review_candidate_count": review_candidates,
        "decision_state": "needs_scan" if not latest else "needs_review" if review_candidates else "ready_for_preview",
        "safe_default_action": "preview",
        "executes_commands": False,
        "apply_enabled": False,
        "empty_state": None if latest else "Run a duplicate preview to populate this review queue.",
    }


def build_similar_images_view_model(home_state: Mapping[str, Any], *, language: str = "en") -> dict[str, object]:
    runs = _runs_from_home_state(home_state)
    latest = _latest_matching_run(runs, "similar", "image")
    return {
        "kind": "ui_similar_images_view_model",
        "title": "Similar images",
        "description": "Compare visually similar image groups before deciding what to keep.",
        "latest_run": dict(latest) if latest else None,
        "run_count": _count_matching_runs(runs, "similar", "image"),
        "review_candidate_count": _as_int(latest.get("review_candidate_count")) if latest else 0,
        "safe_default_action": "preview",
        "executes_commands": False,
        "apply_enabled": False,
        "empty_state": None if latest else "Run a similar-images preview to populate this workbench.",
    }


def build_decision_summary_view_model(home_state: Mapping[str, Any], *, language: str = "en") -> dict[str, object]:
    runs = _runs_from_home_state(home_state)
    error_count = _as_int(_run_summary(home_state).get("error_count"))
    review_candidate_count = sum(_as_int(run.get("review_candidate_count")) for run in runs)
    latest = _first_mapping(runs)
    has_blockers = error_count > 0 or review_candidate_count > 0
    return {
        "kind": "ui_decision_summary_view_model",
        "title": "Decision summary",
        "status": "blocked" if has_blockers else "ready_for_preview",
        "latest_run": dict(latest) if latest else None,
        "error_count": error_count,
        "review_candidate_count": review_candidate_count,
        "apply_enabled": False,
        "requires_explicit_user_confirmation": True,
        "next_action": "Resolve review candidates or run a fresh preview." if has_blockers else "Choose a workflow and build a preview.",
    }


def build_ui_run_history_view_model(home_state: Mapping[str, Any], *, language: str = "en") -> dict[str, object]:
    page_state = build_run_history_page_state(home_state, language=language)
    table = _as_mapping(page_state.get("table"))
    return {
        "kind": "ui_run_history_view_model",
        "title": translate("page.run-history.title", language=language),
        "description": translate("page.run-history.description", language=language),
        "filters": page_state.get("filters"),
        "table": table,
        "row_count": len(_as_list(table.get("rows"))),
        "executes_commands": False,
    }


def _summary(view_models: Mapping[str, Any]) -> dict[str, object]:
    duplicate = _as_mapping(view_models.get("duplicate_review"))
    similar = _as_mapping(view_models.get("similar_images"))
    run_history = _as_mapping(view_models.get("run_history"))
    decision = _as_mapping(view_models.get("decision_summary"))
    review_workbench = _as_mapping(view_models.get("review_workbench"))
    review_summary = _as_mapping(review_workbench.get("summary"))
    return {
        "view_model_count": len(view_models),
        "run_history_rows": _as_int(run_history.get("row_count")),
        "duplicate_run_count": _as_int(duplicate.get("run_count")),
        "similar_run_count": _as_int(similar.get("run_count")),
        "review_workbench_attention_count": _as_int(review_summary.get("attention_count")),
        "decision_status": decision.get("status"),
        "apply_enabled": bool(decision.get("apply_enabled")),
    }


def build_ui_app_service_view_models(
    home_state: Mapping[str, Any] | None = None,
    *,
    profile_dir: str | Path | None = None,
    run_dir: str | Path | None = None,
    people_bundle_dir: str | Path | None = None,
    active_page_id: str = "dashboard",
    home_state_json: str | Path | None = None,
    language: str | None = None,
) -> dict[str, object]:
    lang = normalize_language(language)
    if home_state is None:
        if home_state_json is not None:
            home_state = read_json_object(home_state_json)
        else:
            home_state = build_app_home_state(profile_dir=profile_dir, run_dir=run_dir, people_bundle_dir=people_bundle_dir, active_page_id=active_page_id)
    duplicate_review = build_duplicate_review_view_model(home_state, language=lang)
    similar_images = build_similar_images_view_model(home_state, language=lang)
    decision_summary = build_decision_summary_view_model(home_state, language=lang)
    view_models = {
        "home": build_ui_home_view_model(home_state, language=lang),
        "scan_setup": build_scan_setup_view_model(home_state, language=lang),
        "duplicate_review": duplicate_review,
        "similar_images": similar_images,
        "decision_summary": decision_summary,
        "run_history": build_ui_run_history_view_model(home_state, language=lang),
        "review_workbench": build_ui_review_workbench_view_model(
            duplicate_review=duplicate_review,
            similar_images=similar_images,
            decision_summary=decision_summary,
            people_review_summary=_people_summary(home_state),
        ),
    }
    return {
        "schema_version": APP_SERVICE_VIEW_MODELS_SCHEMA_VERSION,
        "kind": APP_SERVICE_VIEW_MODELS_KIND,
        "generated_at_utc": _now_utc(),
        "language": lang,
        "active_page_id": str(active_page_id or "dashboard"),
        "view_models": view_models,
        "summary": _summary(view_models),
        "capabilities": {
            "headless_testable": True,
            "requires_pyside6": False,
            "opens_window": False,
            "executes_commands": False,
            "local_only": True,
            "apply_requires_explicit_confirmation": True,
        },
    }


def summarize_ui_app_service_view_models(payload: Mapping[str, Any]) -> str:
    summary = _as_mapping(payload.get("summary"))
    capabilities = _as_mapping(payload.get("capabilities"))
    return "\n".join(
        [
            "Media Manager UI app-service view models",
            f"  View models: {summary.get('view_model_count')}",
            f"  Run history rows: {summary.get('run_history_rows')}",
            f"  Duplicate runs: {summary.get('duplicate_run_count')}",
            f"  Similar-image runs: {summary.get('similar_run_count')}",
            f"  Review attention: {summary.get('review_workbench_attention_count')}",
            f"  Decision status: {summary.get('decision_status')}",
            f"  Apply enabled: {summary.get('apply_enabled')}",
            f"  Requires PySide6: {capabilities.get('requires_pyside6')}",
            f"  Opens window: {capabilities.get('opens_window')}",
            f"  Executes commands: {capabilities.get('executes_commands')}",
        ]
    )


def write_ui_app_service_view_models(
    out_dir: str | Path,
    *,
    profile_dir: str | Path | None = None,
    run_dir: str | Path | None = None,
    people_bundle_dir: str | Path | None = None,
    active_page_id: str = "dashboard",
    home_state_json: str | Path | None = None,
    language: str | None = None,
) -> dict[str, object]:
    payload = build_ui_app_service_view_models(
        profile_dir=profile_dir,
        run_dir=run_dir,
        people_bundle_dir=people_bundle_dir,
        active_page_id=active_page_id,
        home_state_json=home_state_json,
        language=language,
    )
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    written_files: list[str] = []
    write_json_object(root / "ui_app_service_view_models.json", payload)
    written_files.append(str(root / "ui_app_service_view_models.json"))
    for name, model in _as_mapping(payload.get("view_models")).items():
        path = root / f"{str(name).replace('_', '-')}.json"
        write_json_object(path, _as_mapping(model))
        written_files.append(str(path))
    readme = root / "README.txt"
    readme.write_text(
        summarize_ui_app_service_view_models(payload)
        + "\n\nThese files are headless UI view models for a future Qt renderer. They do not execute commands or open windows.\n",
        encoding="utf-8",
    )
    written_files.append(str(readme))
    return {**payload, "output_dir": str(root), "written_files": written_files, "written_file_count": len(written_files)}


__all__ = [
    "APP_SERVICE_VIEW_MODELS_KIND",
    "APP_SERVICE_VIEW_MODELS_SCHEMA_VERSION",
    "build_decision_summary_view_model",
    "build_duplicate_review_view_model",
    "build_scan_setup_view_model",
    "build_similar_images_view_model",
    "build_ui_app_service_view_models",
    "build_ui_home_view_model",
    "build_ui_run_history_view_model",
    "summarize_ui_app_service_view_models",
    "write_ui_app_service_view_models",
]
