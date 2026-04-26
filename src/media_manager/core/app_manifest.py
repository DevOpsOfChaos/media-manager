from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

from media_manager.media_formats import list_media_format_capabilities
from .plan_snapshot import build_plan_snapshot_from_report

SCHEMA_VERSION = "1.0"


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _option(
    name: str,
    *,
    value_type: str = "string",
    repeatable: bool = False,
    required: bool = False,
    choices: list[str] | None = None,
    default: Any = None,
    help_text: str = "",
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "name": name,
        "type": value_type,
        "repeatable": repeatable,
        "required": required,
        "help": help_text,
    }
    if choices is not None:
        payload["choices"] = choices
    if default is not None:
        payload["default"] = default
    return payload


def _common_source_options(*, target: bool = False, apply: bool = False) -> list[dict[str, Any]]:
    options = [
        _option("--source", value_type="path", repeatable=True, required=True, help_text="Source directory."),
        _option("--non-recursive", value_type="boolean", help_text="Only scan the top level of each source."),
        _option("--include-hidden", value_type="boolean", help_text="Include hidden files and folders."),
        _option("--include-pattern", repeatable=True, help_text="Include paths matching a glob-style pattern."),
        _option("--exclude-pattern", repeatable=True, help_text="Exclude paths matching a glob-style pattern."),
        _option("--json", value_type="boolean", help_text="Print machine-readable JSON output."),
        _option("--report-json", value_type="path", help_text="Write the full report payload."),
        _option("--review-json", value_type="path", help_text="Write a compact review payload."),
        _option("--run-dir", value_type="path", help_text="Write a structured run artifact folder."),
    ]
    if target:
        options.insert(1, _option("--target", value_type="path", required=True, help_text="Target directory root."))
    if apply:
        options.append(_option("--apply", value_type="boolean", help_text="Execute the planned operations."))
    return options


def _people_options() -> list[dict[str, Any]]:
    return [
        _option("--source", value_type="path", repeatable=True, required=True, help_text="Source directory for people scan."),
        _option("--catalog", value_type="path", help_text="Local people catalog JSON path."),
        _option("--backend", choices=["auto", "dlib", "face-recognition", "opencv"], default="auto", help_text="People recognition backend."),
        _option("--include-encodings", value_type="boolean", help_text="Include sensitive face encodings for review-apply workflows."),
        _option("--report-json", value_type="path", help_text="Write people scan report JSON."),
        _option("--review-json", value_type="path", help_text="Write compact unknown-face review JSON."),
        _option("--bundle-dir", value_type="path", help_text="Write a GUI-ready people review bundle directory."),
        _option("--include-pattern", repeatable=True, help_text="Include paths matching a glob-style pattern."),
        _option("--exclude-pattern", repeatable=True, help_text="Exclude paths matching a glob-style pattern."),
    ]


def build_command_catalog() -> list[dict[str, Any]]:
    """Return a GUI-oriented description of first-class CLI capabilities."""
    return [
        {
            "id": "organize",
            "label": "Organize media",
            "description": "Plan or execute date-based copy/move organization into a target library.",
            "risk_level": "medium",
            "default_mode": "preview",
            "supports": {"preview": True, "apply": True, "run_artifacts": True, "review_export": True, "report_export": True, "include_exclude": True, "media_groups": True, "conflict_policy": True},
            "options": [*_common_source_options(target=True, apply=True), _option("--pattern", default="{year}/{month}", help_text="Target directory pattern."), _option("--copy", value_type="boolean", help_text="Copy files to the target library."), _option("--move", value_type="boolean", help_text="Move files to the target library."), _option("--include-associated-files", value_type="boolean", help_text="Plan safe sidecars and media pairs together."), _option("--conflict-policy", choices=["conflict", "skip"], default="conflict", help_text="How to handle existing target paths.")],
            "primary_artifacts": ["report.json", "review.json", "summary.txt", "ui_state.json", "plan_snapshot.json", "action_model.json"],
        },
        {
            "id": "rename",
            "label": "Rename media",
            "description": "Plan or execute metadata/filename-based renames in place.",
            "risk_level": "medium",
            "default_mode": "preview",
            "supports": {"preview": True, "apply": True, "run_artifacts": True, "review_export": True, "report_export": True, "include_exclude": True, "media_groups": True, "conflict_policy": True},
            "options": [*_common_source_options(apply=True), _option("--template", default="{date:%Y-%m-%d_%H-%M-%S}_{stem}", help_text="Rename template."), _option("--include-associated-files", value_type="boolean", help_text="Plan safe sidecars and media pairs together."), _option("--conflict-policy", choices=["conflict", "skip"], default="conflict", help_text="How to handle existing target names.")],
            "primary_artifacts": ["report.json", "review.json", "summary.txt", "ui_state.json", "plan_snapshot.json", "action_model.json"],
        },
        {
            "id": "duplicates",
            "label": "Find duplicates",
            "description": "Find exact duplicate media across images, RAW images, videos, and audio.",
            "risk_level": "high",
            "default_mode": "review",
            "supports": {"preview": True, "apply": True, "run_artifacts": True, "review_export": True, "report_export": True, "include_exclude": True, "decision_import_export": True, "media_kind_filter": True, "similar_images": True},
            "options": [*_common_source_options(apply=False), _option("--media-kind", repeatable=True, choices=["all", "image", "raw-image", "video", "audio"], default="all", help_text="Limit duplicate scanning to media kinds."), _option("--include-extension", repeatable=True, help_text="Limit duplicate scanning to specific extensions."), _option("--exclude-extension", repeatable=True, help_text="Exclude specific extensions."), _option("--policy", choices=["first", "newest", "oldest"], help_text="Optional automatic keep policy."), _option("--mode", choices=["copy", "move", "delete"], default="copy", help_text="Duplicate cleanup planning mode."), _option("--export-decisions", value_type="path", help_text="Export editable duplicate decisions."), _option("--import-decisions", value_type="path", help_text="Import reviewed duplicate decisions."), _option("--similar-images", value_type="boolean", help_text="Also collect similar-image review candidates."), _option("--list-supported-formats", value_type="boolean", help_text="Print supported media formats.")],
            "primary_artifacts": ["report.json", "review.json", "summary.txt", "ui_state.json", "plan_snapshot.json", "action_model.json"],
        },
        {
            "id": "cleanup",
            "label": "Guided cleanup",
            "description": "Build a combined scan, duplicate, organize, and rename cleanup report.",
            "risk_level": "high",
            "default_mode": "review",
            "supports": {"preview": True, "apply": True, "run_artifacts": True, "review_export": True, "report_export": True, "include_exclude": True, "media_groups": True, "leftover_consolidation": True, "conflict_policy": True},
            "options": [*_common_source_options(target=True, apply=False), _option("--apply-organize", value_type="boolean", help_text="Execute the embedded organize plan."), _option("--apply-rename", value_type="boolean", help_text="Execute the embedded rename plan."), _option("--duplicate-policy", choices=["first", "newest", "oldest"], help_text="Optional duplicate keep policy."), _option("--duplicate-mode", choices=["copy", "move", "delete"], default="copy", help_text="Duplicate cleanup planning mode."), _option("--leftover-mode", choices=["off", "consolidate"], default="off", help_text="Optional source-leftover consolidation after apply-organize."), _option("--include-associated-files", value_type="boolean", help_text="Plan safe sidecars and media pairs together."), _option("--conflict-policy", choices=["conflict", "skip"], default="conflict", help_text="How to handle existing target paths.")],
            "primary_artifacts": ["report.json", "review.json", "summary.txt", "ui_state.json", "plan_snapshot.json", "action_model.json", "journal.json"],
        },
        {
            "id": "people",
            "label": "Review people",
            "description": "Detect faces locally, group unknown people, curate review decisions, and train a local people catalog.",
            "risk_level": "sensitive",
            "default_mode": "review",
            "supports": {
                "preview": True,
                "apply": False,
                "report_export": True,
                "review_export": True,
                "include_exclude": True,
                "people_catalog": True,
                "face_detection": True,
                "named_person_matching": True,
                "review_bundle": True,
                "face_crop_assets": True,
                "session_controls": True,
                "local_only": True,
            },
            "options": _people_options(),
            "primary_artifacts": [
                "people_report.json",
                "people_review_workflow.json",
                "people_review_workspace.json",
                "bundle_manifest.json",
                "summary.txt",
                "assets/people_review_assets.json",
                "assets/faces/*.jpg",
            ],
        },
        {
            "id": "doctor",
            "label": "Validate setup",
            "description": "Validate inputs, outputs, filters, and environment assumptions without changing files.",
            "risk_level": "safe",
            "default_mode": "diagnostic",
            "supports": {"preview": True, "report_export": True, "include_exclude": True},
            "options": [_option("--command", choices=["general", "organize", "rename", "cleanup", "duplicates", "people", "inspect", "trip"], default="general", help_text="Workflow context."), _option("--source", value_type="path", repeatable=True, help_text="Source directory."), _option("--target", value_type="path", help_text="Optional target directory."), _option("--include-pattern", repeatable=True, help_text="Include paths matching a glob-style pattern."), _option("--exclude-pattern", repeatable=True, help_text="Exclude paths matching a glob-style pattern."), _option("--json", value_type="boolean", help_text="Print machine-readable JSON output."), _option("--report-json", value_type="path", help_text="Write diagnostic report JSON.")],
            "primary_artifacts": ["report.json"],
        },
        {
            "id": "runs",
            "label": "Browse runs",
            "description": "List, inspect, and validate structured run artifact folders.",
            "risk_level": "safe",
            "default_mode": "browse",
            "supports": {"run_artifact_index": True, "json": True},
            "options": [_option("--run-dir", value_type="path", default="runs", help_text="Run artifact root directory."), _option("--json", value_type="boolean", help_text="Print machine-readable JSON output.")],
            "primary_artifacts": ["command.json", "report.json", "review.json", "summary.txt", "ui_state.json", "plan_snapshot.json", "action_model.json", "journal.json"],
        },
    ]


def _media_formats_by_kind() -> dict[str, list[str]]:
    by_kind: dict[str, list[str]] = {}
    for item in list_media_format_capabilities():
        key = item.media_kind.replace("-", "_")
        by_kind.setdefault(key, []).append(item.extension)
    return {key: sorted(values) for key, values in sorted(by_kind.items())}


def build_app_manifest() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": _now_utc(),
        "application": {
            "id": "media-manager",
            "name": "Media Manager",
            "product_focus": "CLI/Core first with GUI-ready structured artifacts",
            "default_run_dir": "runs",
            "primary_entrypoint": "media-manager",
        },
        "entrypoints": {
            "main": "media-manager",
            "app": "media-manager app",
            "organize": "media-manager organize",
            "rename": "media-manager rename",
            "duplicates": "media-manager duplicates",
            "cleanup": "media-manager cleanup",
            "people": "media-manager people",
            "people_session": "media-manager-people-session",
            "doctor": "media-manager doctor",
            "runs": "media-manager runs",
            "profiles": "media-manager app profiles",
        },
        "artifact_contract": {
            "run_directory_files": ["command.json", "report.json", "review.json", "summary.txt", "ui_state.json", "plan_snapshot.json", "action_model.json"],
            "optional_files": ["journal.json"],
            "ui_state_file": "ui_state.json",
            "plan_snapshot_file": "plan_snapshot.json",
            "action_model_file": "action_model.json",
            "people_review_bundle_files": ["bundle_manifest.json", "people_report.json", "people_review_workflow.json", "people_review_workspace.json", "summary.txt", "assets/people_review_assets.json"],
            "people_face_asset_glob": "assets/faces/*.jpg",
            "app_profile_schema_version": 1,
            "profile_files": "GUI-friendly app profiles are JSON files managed with media-manager app profiles.",
            "versioning": "Additive JSON fields are preferred; existing fields should remain stable.",
        },
        "commands": build_command_catalog(),
        "media_formats": _media_formats_by_kind(),
        "ui_guidance": {
            "safe_defaults": [
                "Prefer preview/report flows before apply.",
                "Show review candidates prominently before destructive duplicate cleanup.",
                "Use run artifacts as the GUI persistence layer instead of parsing CLI text.",
                "Use people review bundles as the GUI persistence layer for face/person curation.",
                "Keep people catalogs, face crops, and reports local/private because they can contain biometric metadata.",
                "Use plan_snapshot.json for table/list previews, ui_state.json for dashboard cards, and action_model.json for GUI buttons/next steps.",
                "Use app profiles for saved GUI presets instead of storing raw CLI text only.",
            ],
            "recommended_primary_views": ["Dashboard", "New run", "Saved profiles", "Plan preview", "Review candidates", "People review", "People catalog", "Run history", "Settings/Doctor"],
        },
    }


def _int_or_zero(value: Any) -> int:
    return value if isinstance(value, int) else 0


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _extract_counters(payload: Mapping[str, Any]) -> dict[str, Any]:
    counters: dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, (int, str, bool)) and (
            key.endswith("_count")
            or key in {"exact_groups", "duplicate_files", "extra_duplicates", "errors", "planned_count", "skipped_count", "conflict_count", "error_count", "ready"}
        ):
            counters[key] = value
    return dict(sorted(counters.items()))


def _section_card(name: str, section: Any) -> dict[str, Any] | None:
    if not isinstance(section, Mapping):
        return None
    counters = _extract_counters(section)
    if not counters and name not in {"summary", "scan", "duplicates", "organize", "rename", "cleanup", "execution", "people"}:
        return None
    return {
        "id": name,
        "title": name.replace("_", " ").title(),
        "counters": counters,
        "status": section.get("status") if isinstance(section.get("status"), str) else None,
        "next_action": section.get("next_action") if isinstance(section.get("next_action"), str) else None,
    }


def _review_preview(review: Mapping[str, Any]) -> dict[str, Any]:
    candidates = review.get("candidates")
    if not isinstance(candidates, list):
        candidates = []
    preview_rows = []
    for item in candidates[:10]:
        if not isinstance(item, Mapping):
            continue
        preview_rows.append(
            {
                "section": item.get("section", "people"),
                "source_path": item.get("source_path", item.get("path")),
                "target_path": item.get("target_path"),
                "status": item.get("status"),
                "reason": item.get("reason"),
                "review_reasons": item.get("review_reasons", []),
                "face_index": item.get("face_index"),
                "unknown_cluster_id": item.get("unknown_cluster_id"),
            }
        )
    return {
        "candidate_count": _int_or_zero(review.get("candidate_count")),
        "section_summary": review.get("section_summary", {}) if isinstance(review.get("section_summary"), dict) else {},
        "reason_summary": review.get("reason_summary", {}) if isinstance(review.get("reason_summary"), dict) else {},
        "truncated": bool(review.get("truncated", False)),
        "preview": preview_rows,
    }


def _people_overview(report_payload: Mapping[str, Any]) -> dict[str, Any] | None:
    if report_payload.get("schema_version") != 1 and "detections" not in report_payload:
        return None
    summary = _as_mapping(report_payload.get("summary"))
    if not summary and "detections" not in report_payload:
        return None
    return {
        "backend": report_payload.get("backend"),
        "backend_available": report_payload.get("backend_available"),
        "strong_backend_available": report_payload.get("strong_backend_available"),
        "face_count": summary.get("face_count", 0),
        "matched_faces": summary.get("matched_faces", 0),
        "unknown_faces": summary.get("unknown_faces", 0),
        "unknown_cluster_count": summary.get("unknown_cluster_count", 0),
        "catalog_person_count": summary.get("catalog_person_count", 0),
    }


def build_ui_state_from_report(
    *,
    command_name: str,
    report_payload: Mapping[str, Any],
    command_payload: Mapping[str, Any] | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    command_payload = command_payload or {}
    outcome = _as_mapping(report_payload.get("outcome_report"))
    review = _as_mapping(report_payload.get("review"))
    people_overview = _people_overview(report_payload) if command_name == "people" else None

    section_cards: list[dict[str, Any]] = []
    for name in ("summary", "scan", "duplicates", "organize", "rename", "cleanup", "execution", "decision_summary"):
        card = _section_card(name, report_payload.get(name))
        if card is not None:
            section_cards.append(card)
    if people_overview is not None:
        section_cards.append({"id": "people", "title": "People", "counters": {key: value for key, value in people_overview.items() if isinstance(value, (int, str, bool))}, "status": report_payload.get("status"), "next_action": report_payload.get("next_action")})

    status = outcome.get("status") if outcome else report_payload.get("status")
    next_action = outcome.get("next_action") if outcome else report_payload.get("next_action")
    exit_code = command_payload.get("exit_code")
    apply_requested = command_payload.get("apply_requested")
    if not isinstance(exit_code, int):
        exit_code = None
    if not isinstance(apply_requested, bool):
        apply_requested = None

    review_candidate_count = _int_or_zero(review.get("candidate_count"))
    if command_name == "people" and review_candidate_count == 0:
        summary = _as_mapping(report_payload.get("summary"))
        review_candidate_count = _int_or_zero(summary.get("unknown_faces"))

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": _now_utc(),
        "run_id": run_id,
        "command": command_name,
        "mode": "apply" if apply_requested else "preview" if apply_requested is False else "review" if command_name == "people" else None,
        "exit_code": exit_code,
        "overview": {
            "status": status,
            "safe_to_apply": outcome.get("safe_to_apply") if outcome else False if command_name == "people" else None,
            "needs_review": outcome.get("needs_review") if outcome else review_candidate_count > 0 if command_name == "people" else None,
            "blocked_count": outcome.get("blocked_count") if outcome else None,
            "actionable_count": outcome.get("actionable_count") if outcome else None,
            "next_action": next_action,
            "review_candidate_count": review_candidate_count,
            "people": people_overview,
        },
        "review": _review_preview(review) if review else _review_preview({"candidate_count": review_candidate_count}),
        "sections": section_cards,
        "suggested_actions": [
            item
            for item in [
                {"id": "review_people", "label": "Review detected people", "enabled": command_name == "people" and review_candidate_count > 0},
                {"id": "review", "label": "Review candidates", "enabled": review_candidate_count > 0},
                {"id": "apply", "label": "Apply planned changes", "enabled": bool(outcome.get("safe_to_apply")) if outcome else False},
                {"id": "open_report", "label": "Open full report", "enabled": True},
                {"id": "open_plan_snapshot", "label": "Open plan snapshot", "enabled": command_name != "people"},
                {"id": "open_people_bundle", "label": "Open people review bundle", "enabled": command_name == "people"},
                {"id": "open_action_model", "label": "Open action model", "enabled": True},
                {"id": "open_run_folder", "label": "Open run folder", "enabled": run_id is not None},
            ]
        ],
    }


def build_plan_snapshot_state(
    *,
    command_name: str,
    report_payload: Mapping[str, Any],
    run_id: str | None = None,
    entry_limit: int = 200,
) -> dict[str, Any]:
    return build_plan_snapshot_from_report(
        command_name=command_name,
        report_payload=report_payload,
        run_id=run_id,
        entry_limit=entry_limit,
    )


__all__ = [
    "SCHEMA_VERSION",
    "build_app_manifest",
    "build_command_catalog",
    "build_ui_state_from_report",
    "build_plan_snapshot_state",
]
