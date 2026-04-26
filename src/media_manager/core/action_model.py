from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

SCHEMA_VERSION = "1.0"


COMMAND_LABELS = {
    "organize": "Organize media",
    "rename": "Rename media",
    "cleanup": "Guided cleanup",
    "duplicates": "Find duplicates",
    "doctor": "Validate setup",
    "runs": "Run history",
    "people": "Review people",
}


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_int(value: Any) -> int:
    return value if isinstance(value, int) else 0


def _is_truthy(value: Any) -> bool:
    return bool(value) if isinstance(value, bool) else False


def _command_argv(command_payload: Mapping[str, Any] | None) -> list[str]:
    payload = _as_mapping(command_payload)
    argv = payload.get("argv")
    if isinstance(argv, list):
        return [str(item) for item in argv if item is not None]
    return []


def _apply_requested(command_payload: Mapping[str, Any] | None, report_payload: Mapping[str, Any]) -> bool:
    payload = _as_mapping(command_payload)
    value = payload.get("apply_requested")
    if isinstance(value, bool):
        return value
    execution = report_payload.get("execution")
    return isinstance(execution, Mapping)


def _outcome(report_payload: Mapping[str, Any]) -> Mapping[str, Any]:
    return _as_mapping(report_payload.get("outcome_report"))


def _review(report_payload: Mapping[str, Any]) -> Mapping[str, Any]:
    return _as_mapping(report_payload.get("review"))


def _candidate_count(report_payload: Mapping[str, Any], *, command_name: str = "") -> int:
    review = _review(report_payload)
    count = review.get("candidate_count")
    if isinstance(count, int):
        return count
    candidates = review.get("candidates")
    if isinstance(candidates, list):
        return len(candidates)
    if command_name == "people":
        summary = _as_mapping(report_payload.get("summary"))
        return _as_int(summary.get("unknown_faces"))
    return 0


def _has_errors(report_payload: Mapping[str, Any]) -> bool:
    outcome = _outcome(report_payload)
    status = outcome.get("status") or report_payload.get("status")
    if status in {"blocked", "failed", "error", "backend_missing", "completed_with_errors"}:
        return True
    errors = report_payload.get("errors")
    if isinstance(errors, list) and errors:
        return True
    for section_name in ("scan", "summary", "duplicates", "organize", "rename", "execution"):
        section = _as_mapping(report_payload.get(section_name))
        if _as_int(section.get("error_count")) > 0 or _as_int(section.get("errors")) > 0:
            return True
        missing = section.get("missing_sources")
        if isinstance(missing, list) and missing:
            return True
    return False


def _has_conflicts(report_payload: Mapping[str, Any]) -> bool:
    for section_name in ("summary", "duplicates", "organize", "rename", "execution"):
        section = _as_mapping(report_payload.get(section_name))
        if _as_int(section.get("conflict_count")) > 0:
            return True
    return False


def _has_apply_target(command_name: str, report_payload: Mapping[str, Any]) -> bool:
    if command_name in {"organize", "rename", "cleanup"}:
        return True
    if command_name == "duplicates":
        dry_run = _as_mapping(report_payload.get("dry_run"))
        execution_preview = _as_mapping(report_payload.get("execution_preview"))
        planned = _as_int(dry_run.get("planned_count"))
        executable = _as_int(execution_preview.get("executable_count"))
        deferred = _as_int(execution_preview.get("deferred_count"))
        return planned > 0 or executable > 0 or deferred > 0
    return False


def _extract_run_dir(command_payload: Mapping[str, Any] | None) -> str | None:
    payload = _as_mapping(command_payload)
    value = payload.get("run_dir")
    if value is not None:
        return str(value)
    argv = _command_argv(command_payload)
    for index, item in enumerate(argv):
        if item == "--run-dir" and index + 1 < len(argv):
            return argv[index + 1]
        if item.startswith("--run-dir="):
            return item.split("=", 1)[1]
    return None


def _arg_after(argv: list[str], flag: str) -> str | None:
    for index, item in enumerate(argv):
        if item == flag and index + 1 < len(argv):
            return argv[index + 1]
        if item.startswith(flag + "="):
            return item.split("=", 1)[1]
    return None


def _action(
    action_id: str,
    label: str,
    *,
    description: str,
    category: str,
    risk_level: str = "safe",
    enabled: bool = True,
    recommended: bool = False,
    requires_confirmation: bool = False,
    command_preview: list[str] | None = None,
    blocked_reason: str | None = None,
    ui_hint: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": action_id,
        "label": label,
        "description": description,
        "category": category,
        "risk_level": risk_level,
        "enabled": enabled,
        "recommended": recommended,
        "requires_confirmation": requires_confirmation,
    }
    if command_preview:
        payload["command_preview"] = command_preview
    if blocked_reason:
        payload["blocked_reason"] = blocked_reason
    if ui_hint:
        payload["ui_hint"] = ui_hint
    return payload


def _base_cli_args(command_name: str, command_payload: Mapping[str, Any] | None) -> list[str]:
    argv = _command_argv(command_payload)
    if argv and argv[0] == command_name:
        return ["media-manager", *argv]
    if argv:
        return ["media-manager", command_name, *argv]
    return ["media-manager", command_name]


def _without_apply_flags(argv: list[str]) -> list[str]:
    return [item for item in argv if item not in {"--apply", "--apply-organize", "--apply-rename"}]


def _with_flag(argv: list[str], flag: str) -> list[str]:
    if flag in argv:
        return argv
    return [*argv, flag]


def _safe_apply_preview(command_name: str, argv: list[str]) -> list[str]:
    if command_name == "cleanup":
        if "--apply-rename" in argv or "--apply-organize" in argv:
            return argv
        return [*argv, "--apply-organize"]
    if command_name in {"organize", "rename"}:
        return _with_flag(argv, "--apply")
    return argv


def _duplicate_decision_state(report_payload: Mapping[str, Any]) -> tuple[bool, int, int]:
    summary = _as_mapping(report_payload.get("decision_summary"))
    decided = _as_int(summary.get("resolved_group_count"))
    unresolved = _as_int(summary.get("unresolved_group_count"))
    from_file = _as_int(summary.get("from_decision_file_count"))
    has_decisions = decided > 0 or from_file > 0
    if unresolved == 0:
        cleanup_plan = _as_mapping(_as_mapping(report_payload.get("duplicates")).get("cleanup_plan"))
        unresolved = _as_int(cleanup_plan.get("unresolved_groups"))
    return has_decisions, decided, unresolved


def _people_actions(
    *,
    report_payload: Mapping[str, Any],
    command_payload: Mapping[str, Any] | None,
    candidate_count: int,
    has_errors: bool,
    run_id: str | None,
) -> list[dict[str, Any]]:
    base_argv = _base_cli_args("people", command_payload)
    report_json = _arg_after(base_argv, "--report-json") or "people-report.json"
    workflow_json = _arg_after(base_argv, "--workflow-json") or "people-review-workflow.json"
    bundle_dir = _arg_after(base_argv, "--bundle-dir") or "people-review-bundle"
    catalog = _arg_after(base_argv, "--catalog") or "people.json"
    summary = _as_mapping(report_payload.get("summary"))
    has_encodings = any(isinstance(item, Mapping) and isinstance(item.get("encoding"), list) and item.get("encoding") for item in _as_list(report_payload.get("detections")))
    ready_unknown_faces = _as_int(summary.get("unknown_faces")) > 0 or candidate_count > 0
    return [
        _action(
            "people_review_export",
            "Create people review workflow",
            description="Create an editable workflow JSON for grouping, naming, accepting, and rejecting detected faces.",
            category="review",
            enabled=not has_errors and ready_unknown_faces,
            recommended=not has_errors and ready_unknown_faces,
            command_preview=["media-manager", "people", "review-export", "--report-json", report_json, "--out", workflow_json],
            blocked_reason=None if ready_unknown_faces else "No unknown faces were reported.",
            ui_hint="people_review_workflow",
        ),
        _action(
            "people_review_bundle",
            "Build people review bundle",
            description="Build a GUI-ready people review bundle with workspace JSON and face crop assets.",
            category="review",
            enabled=not has_errors,
            recommended=not has_errors and ready_unknown_faces,
            command_preview=["media-manager", "people", "review-bundle", "--report-json", report_json, "--workflow-json", workflow_json, "--bundle-dir", bundle_dir, "--catalog", catalog],
            ui_hint="people_review_page",
        ),
        _action(
            "people_review_session",
            "Open people review session",
            description="Use session controls to mark groups, reject wrong faces, split groups, and merge groups before applying.",
            category="review",
            enabled=True,
            recommended=ready_unknown_faces,
            command_preview=["media-manager-people-session", "summary", "--workflow-json", workflow_json],
            ui_hint="interactive_people_review",
        ),
        _action(
            "people_review_apply",
            "Apply reviewed people to catalog",
            description="Write confirmed reviewed face embeddings to the local people catalog.",
            category="apply",
            risk_level="sensitive",
            enabled=has_encodings,
            recommended=False,
            requires_confirmation=True,
            command_preview=["media-manager", "people", "review-apply", "--catalog", catalog, "--workflow-json", workflow_json, "--report-json", report_json],
            blocked_reason=None if has_encodings else "review-apply needs a report created with --include-encodings.",
            ui_hint="sensitive_apply",
        ),
        _action(
            "people_rerun_scan_with_encodings",
            "Rerun people scan with encodings",
            description="Refresh the people scan and include face encodings needed for catalog training.",
            category="run",
            enabled=not has_encodings,
            recommended=ready_unknown_faces and not has_encodings,
            command_preview=[*base_argv, "--include-encodings"] if "--include-encodings" not in base_argv else base_argv,
            ui_hint="refresh_people_scan",
        ),
        _action(
            "people_backend_check",
            "Check people backend",
            description="Check whether the strong local dlib backend or OpenCV fallback is available.",
            category="diagnostic",
            enabled=True,
            recommended=has_errors,
            command_preview=["media-manager", "people", "backend"],
            ui_hint="backend_health",
        ),
    ]


def build_action_model_from_report(
    *,
    command_name: str,
    report_payload: Mapping[str, Any],
    command_payload: Mapping[str, Any] | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    command_name = str(command_name)
    outcome = _outcome(report_payload)
    candidate_count = _candidate_count(report_payload, command_name=command_name)
    needs_review = _is_truthy(outcome.get("needs_review")) or candidate_count > 0 or command_name == "people"
    safe_to_apply = _is_truthy(outcome.get("safe_to_apply"))
    has_errors = _has_errors(report_payload)
    has_conflicts = _has_conflicts(report_payload)
    apply_requested = _apply_requested(command_payload, report_payload)
    run_dir = _extract_run_dir(command_payload)
    base_argv = _base_cli_args(command_name, command_payload)
    preview_argv = _without_apply_flags(base_argv)
    actions: list[dict[str, Any]] = []

    actions.append(_action("open_report", "Open full report", description="Inspect the full machine-readable report for this run.", category="inspect", command_preview=["media-manager", "runs", "show", run_id or "<run-id>", "--artifact", "report"] if run_id else None, ui_hint="primary_detail"))
    actions.append(_action("open_plan_snapshot", "Open plan snapshot", description="Show the compact table/list snapshot for planned or reviewable entries.", category="inspect", enabled=command_name != "people", recommended=needs_review and command_name != "people", command_preview=["media-manager", "runs", "show", run_id or "<run-id>", "--artifact", "plan-snapshot"] if run_id else None, ui_hint="table_view"))
    actions.append(_action("open_review", "Review candidates", description="Inspect review candidates before applying changes.", category="review", enabled=candidate_count > 0, recommended=candidate_count > 0 and command_name != "people", command_preview=["media-manager", "runs", "show", run_id or "<run-id>", "--artifact", "review"] if run_id else None, blocked_reason=None if candidate_count > 0 else "No review candidates were reported.", ui_hint="review_queue"))

    if run_id and run_dir:
        actions.append(_action("validate_run_artifacts", "Validate run artifacts", description="Check whether the run folder still contains the expected GUI-facing files.", category="diagnostic", command_preview=["media-manager", "runs", "--run-dir", run_dir, "validate"], ui_hint="health_check"))

    actions.append(_action("rerun_preview", "Run preview again", description="Re-run the same command in preview mode to refresh the report.", category="run", enabled=bool(preview_argv), recommended=has_errors or has_conflicts, command_preview=preview_argv, ui_hint="refresh"))

    if command_name == "people":
        actions.extend(_people_actions(report_payload=report_payload, command_payload=command_payload, candidate_count=candidate_count, has_errors=has_errors, run_id=run_id))
    elif command_name == "doctor":
        actions.append(_action("fix_diagnostics", "Fix diagnostics and rerun", description="Resolve reported input/output issues, then run the diagnostic again.", category="diagnostic", enabled=has_errors or needs_review, recommended=has_errors or needs_review, command_preview=preview_argv, blocked_reason=None if (has_errors or needs_review) else "Doctor did not report blocking diagnostics.", ui_hint="fix_inputs"))
    elif command_name == "duplicates":
        has_decisions, _decided_count, unresolved_count = _duplicate_decision_state(report_payload)
        actions.append(_action("export_duplicate_decisions", "Export duplicate decisions", description="Create an editable decision file so a reviewer can choose keep files before cleanup.", category="review", risk_level="safe", enabled=True, recommended=unresolved_count > 0 or needs_review, command_preview=[*preview_argv, "--export-decisions", "duplicate-decisions.json"], ui_hint="decision_file"))
        actions.append(_action("import_duplicate_decisions_preview", "Preview with reviewed decisions", description="Import a reviewed decision file and preview the resulting duplicate cleanup plan.", category="review", risk_level="safe", enabled=True, recommended=not has_decisions, command_preview=[*preview_argv, "--import-decisions", "duplicate-decisions.json", "--show-plan"], ui_hint="decision_preview"))
        apply_enabled = safe_to_apply and has_decisions and not has_errors and not has_conflicts and unresolved_count == 0
        actions.append(_action("apply_duplicate_cleanup", "Apply duplicate cleanup", description="Execute the duplicate cleanup plan after decisions have been reviewed.", category="apply", risk_level="destructive", enabled=apply_enabled, recommended=False, requires_confirmation=True, command_preview=[*preview_argv, "--import-decisions", "duplicate-decisions.json", "--mode", "delete", "--apply", "--yes"], blocked_reason=None if apply_enabled else "Duplicate cleanup needs valid reviewed decisions and a clean preview before apply.", ui_hint="danger_apply"))
    elif command_name in {"organize", "rename", "cleanup"}:
        apply_enabled = _has_apply_target(command_name, report_payload) and safe_to_apply and not needs_review and not has_errors and not has_conflicts and not apply_requested
        actions.append(_action("apply_plan", "Apply this plan", description="Execute the planned filesystem changes after the preview is clean.", category="apply", risk_level="high" if command_name == "cleanup" else "medium", enabled=apply_enabled, recommended=apply_enabled, requires_confirmation=True, command_preview=_safe_apply_preview(command_name, preview_argv), blocked_reason=None if apply_enabled else "Apply is available only for a clean preview with no review candidates, conflicts, or errors.", ui_hint="apply_confirmation"))
        actions.append(_action("run_doctor", "Run diagnostics for this setup", description="Validate paths, filters, output locations, and environment assumptions before applying.", category="diagnostic", risk_level="safe", enabled=True, recommended=has_errors or has_conflicts, command_preview=["media-manager", "doctor", "--command", command_name], ui_hint="preflight"))

    next_action_id = None
    preferred_order = ["people_review_bundle", "people_review_export", "people_review_session", "apply_plan", "export_duplicate_decisions", "import_duplicate_decisions_preview", "open_review", "open_plan_snapshot", "fix_diagnostics", "run_doctor", "people_backend_check", "rerun_preview", "open_report"]
    for action_id in preferred_order:
        match = next((item for item in actions if item.get("id") == action_id and item.get("enabled") and item.get("recommended")), None)
        if match is not None:
            next_action_id = str(match["id"])
            break
    if next_action_id is None:
        for action in actions:
            if action.get("enabled"):
                next_action_id = str(action["id"])
                break

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": _now_utc(),
        "command": command_name,
        "command_label": COMMAND_LABELS.get(command_name, command_name.title()),
        "run_id": run_id,
        "status": outcome.get("status", report_payload.get("status")),
        "next_action": outcome.get("next_action", report_payload.get("next_action")),
        "next_action_id": next_action_id,
        "safe_to_apply": safe_to_apply,
        "needs_review": needs_review,
        "review_candidate_count": candidate_count,
        "has_errors": has_errors,
        "has_conflicts": has_conflicts,
        "apply_requested": apply_requested,
        "action_count": len(actions),
        "enabled_action_count": sum(1 for action in actions if action.get("enabled")),
        "recommended_action_count": sum(1 for action in actions if action.get("recommended") and action.get("enabled")),
        "actions": actions,
    }


__all__ = ["SCHEMA_VERSION", "build_action_model_from_report"]
