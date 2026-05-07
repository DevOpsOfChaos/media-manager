from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

REVIEW_WORKBENCH_CONFIRMATION_DIALOG_SCHEMA_VERSION = "1.0"
REVIEW_WORKBENCH_CONFIRMATION_DIALOG_KIND = "ui_review_workbench_confirmation_dialog_model"
DEFAULT_CONFIRMATION_PHRASE = "APPLY REVIEWED DECISIONS"


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


def _text(value: object, fallback: str = "") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text or fallback


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _blocked_reasons(apply_preview: Mapping[str, Any]) -> list[str]:
    readiness = _as_mapping(apply_preview.get("readiness"))
    command_plan = _as_mapping(apply_preview.get("command_plan_preview"))
    reasons = [str(item) for item in _as_list(readiness.get("blocked_reasons")) if str(item).strip()]
    reasons.extend(str(item) for item in _as_list(command_plan.get("blocked_reasons")) if str(item).strip())
    if not reasons and readiness.get("ready") is not True:
        next_action = _text(readiness.get("next_action"))
        reasons.append(next_action or "The apply preview is not ready for confirmation.")
    return list(dict.fromkeys(reasons))


def _commands_for_display(command_plan_preview: Mapping[str, Any]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index, command in enumerate(_as_list(command_plan_preview.get("commands")), start=1):
        command_map = _as_mapping(command)
        argv = [str(part) for part in _as_list(command_map.get("argv"))]
        rows.append(
            {
                "index": index,
                "id": _text(command_map.get("id"), f"command-{index}"),
                "label": _text(command_map.get("label"), f"Command {index}"),
                "argv": argv,
                "argv_preview": " ".join(argv),
                "source": _text(command_map.get("source"), "unknown"),
                "enabled": command_map.get("enabled", True) is True,
                "executes_commands": False,
                "requires_explicit_user_confirmation": True,
            }
        )
    return rows


def _risk_level(*, ready: bool, command_count: int, blocked_count: int, unresolved_count: int) -> str:
    if not ready:
        return "blocked"
    if blocked_count or unresolved_count:
        return "high"
    if command_count > 1:
        return "medium"
    return "medium" if command_count == 1 else "low"


def build_review_workbench_confirmation_dialog_model(
    apply_preview: Mapping[str, Any],
    *,
    confirmation_phrase: str = DEFAULT_CONFIRMATION_PHRASE,
) -> dict[str, object]:
    """Build the guarded GUI confirmation model for Review Workbench apply.

    This is intentionally a non-executing dialog contract. It renders the
    reviewed command-plan preview, explicit acknowledgements, and the exact
    phrase a future desktop shell must require before any later apply path can
    become eligible.
    """

    preview = _as_mapping(apply_preview)
    preview_summary = _as_mapping(preview.get("summary"))
    readiness = _as_mapping(preview.get("readiness"))
    capabilities = _as_mapping(preview.get("capabilities"))
    command_plan_preview = _as_mapping(preview.get("command_plan_preview"))
    confirmation = _as_mapping(command_plan_preview.get("confirmation"))
    review_status = _as_mapping(preview.get("review_status"))
    commands = _commands_for_display(command_plan_preview)
    blockers = _blocked_reasons(preview)
    preview_ready = readiness.get("ready") is True and preview_summary.get("preview_ready") is True
    preview_safe = capabilities.get("executes_commands") is False and command_plan_preview.get("executes_commands") is False
    phrase = _text(confirmation.get("confirmation_phrase"), confirmation_phrase)
    ready = preview_ready and preview_safe and bool(commands) and not blockers
    reviewed_count = _as_int(preview_summary.get("reviewed_decision_count", review_status.get("reviewed_decision_count", 0)))
    blocked_count = _as_int(preview_summary.get("blocked_decision_count", review_status.get("blocked_decision_count", 0)))
    unresolved_count = _as_int(preview_summary.get("unresolved_decision_count", review_status.get("unresolved_decision_count", 0)))
    command_count = len(commands)
    risk = _risk_level(ready=ready, command_count=command_count, blocked_count=blocked_count, unresolved_count=unresolved_count)

    checklist = [
        {
            "id": "fresh-preview",
            "label": "A fresh non-executing apply preview is available.",
            "required": True,
            "satisfied": preview_ready,
            "blocked_reason": None if preview_ready else "Apply preview is blocked or missing.",
        },
        {
            "id": "reviewed-decision-plan",
            "label": "A reviewed decision plan is loaded.",
            "required": True,
            "satisfied": review_status.get("has_reviewed_decision_plan") is True,
            "blocked_reason": None if review_status.get("has_reviewed_decision_plan") is True else "No reviewed decision plan was provided.",
        },
        {
            "id": "no-unresolved-decisions",
            "label": "No reviewed decisions are blocked or unresolved.",
            "required": True,
            "satisfied": blocked_count == 0 and unresolved_count == 0,
            "blocked_reason": None if blocked_count == 0 and unresolved_count == 0 else "Blocked or unresolved reviewed decisions remain.",
        },
        {
            "id": "command-plan-visible",
            "label": "The candidate command plan is visible before confirmation.",
            "required": True,
            "satisfied": command_count > 0,
            "blocked_reason": None if command_count > 0 else "There is no command plan to confirm.",
        },
        {
            "id": "non-executing-dialog",
            "label": "This dialog model does not execute commands or media operations.",
            "required": True,
            "satisfied": preview_safe,
            "blocked_reason": None if preview_safe else "Apply preview capabilities are not marked non-executing.",
        },
        {
            "id": "typed-confirmation-required",
            "label": f"The user must type: {phrase}",
            "required": True,
            "satisfied": False,
            "blocked_reason": "Typed confirmation is intentionally not satisfied by a generated model.",
        },
    ]
    required_satisfied_count = sum(1 for item in checklist if item["required"] is True and item["satisfied"] is True)
    required_count = sum(1 for item in checklist if item["required"] is True)
    return {
        "schema_version": REVIEW_WORKBENCH_CONFIRMATION_DIALOG_SCHEMA_VERSION,
        "kind": REVIEW_WORKBENCH_CONFIRMATION_DIALOG_KIND,
        "generated_at_utc": _now_utc(),
        "dialog_id": "review-workbench-apply-confirmation",
        "title": "Confirm reviewed apply plan",
        "description": "Guarded confirmation model for a reviewed Review Workbench apply preview.",
        "mode": "confirmation_ready" if ready else "blocked",
        "selected_lane_id": preview_summary.get("selected_lane_id"),
        "apply_preview_status": preview_summary.get("status"),
        "risk_summary": {
            "risk_level": risk,
            "reviewed_decision_count": reviewed_count,
            "blocked_decision_count": blocked_count,
            "unresolved_decision_count": unresolved_count,
            "candidate_command_count": command_count,
            "executes_commands": False,
            "executes_media_operations": False,
        },
        "command_plan_preview": {
            "plan_id": command_plan_preview.get("plan_id"),
            "title": command_plan_preview.get("title"),
            "preview_ready": command_plan_preview.get("preview_ready") is True,
            "enabled": False,
            "commands": commands,
            "executes_commands": False,
        },
        "checklist": checklist,
        "confirmation": {
            "required": True,
            "phrase": phrase,
            "phrase_input_required": True,
            "requires_fresh_preview": confirmation.get("requires_fresh_preview", True) is True,
            "requires_reviewed_decision_plan": confirmation.get("requires_reviewed_decision_plan", True) is True,
            "required_check_count": required_count,
            "required_satisfied_count": required_satisfied_count,
            "all_generated_checks_satisfied": required_satisfied_count == required_count - 1 and checklist[-1]["id"] == "typed-confirmation-required",
            "typed_confirmation_satisfied": False,
            "executes_commands": False,
        },
        "controls": [
            {
                "id": "confirmation_phrase_input",
                "widget_role": "QLineEdit",
                "label": "Type confirmation phrase",
                "required": True,
                "expected_value": phrase,
                "masked": False,
                "executes_commands": False,
            },
            {
                "id": "refresh_apply_preview",
                "widget_role": "QPushButton",
                "label": "Refresh preview",
                "intent_kind": "toolbar_refresh",
                "enabled": True,
                "executes_commands": False,
            },
            {
                "id": "cancel_confirmation",
                "widget_role": "QPushButton",
                "label": "Cancel",
                "intent_kind": "dismiss_confirmation_dialog",
                "enabled": True,
                "executes_commands": False,
            },
            {
                "id": "confirm_apply_preview",
                "widget_role": "QPushButton",
                "label": "Confirm reviewed apply plan",
                "intent_kind": "confirm_apply_preview",
                "enabled": False,
                "requires_explicit_user_confirmation": True,
                "executes_commands": False,
                "future_execution_gate": "requires separate apply executor contract, not this dialog model",
            },
        ],
        "readiness": {
            "ready": ready,
            "status": "confirmation_ready" if ready else "blocked",
            "blocked_reasons": blockers,
            "next_action": (
                "Render this confirmation dialog, require the exact phrase, and keep command execution disabled until a separate apply executor contract exists."
                if ready
                else "Resolve the blocked apply preview before rendering an enabled confirmation dialog."
            ),
        },
        "capabilities": {
            "headless_testable": True,
            "requires_pyside6": False,
            "opens_window": False,
            "executes_commands": False,
            "executes_media_operations": False,
            "apply_enabled": False,
            "confirmation_required": True,
            "local_only": True,
        },
        "summary": {
            "selected_lane_id": preview_summary.get("selected_lane_id"),
            "status": "confirmation_ready" if ready else "blocked",
            "risk_level": risk,
            "reviewed_decision_count": reviewed_count,
            "candidate_command_count": command_count,
            "required_check_count": required_count,
            "required_satisfied_count": required_satisfied_count,
            "typed_confirmation_required": True,
            "apply_enabled": False,
            "executes_commands": False,
        },
    }


def write_review_workbench_confirmation_dialog_model(
    out_dir: str | Path,
    apply_preview: Mapping[str, Any],
    *,
    confirmation_phrase: str = DEFAULT_CONFIRMATION_PHRASE,
) -> dict[str, object]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = build_review_workbench_confirmation_dialog_model(apply_preview, confirmation_phrase=confirmation_phrase)
    files: list[tuple[str, Mapping[str, Any]]] = [
        ("review_workbench_confirmation_dialog_model.json", payload),
        ("review_workbench_confirmation_checklist.json", {"checklist": _as_list(payload.get("checklist"))}),
    ]
    written_files: list[str] = []
    for filename, item in files:
        path = root / filename
        _write_json(path, item)
        written_files.append(str(path))
    readme = root / "README.txt"
    readme.write_text(
        "Review Workbench confirmation dialog model\n"
        "Generated by media-manager app-services review-workbench-confirmation-dialog.\n"
        "This is a non-executing guarded confirmation contract. It does not apply media operations, mutate catalogs, or run commands.\n",
        encoding="utf-8",
    )
    written_files.append(str(readme))
    return {**payload, "output_dir": str(root), "written_files": written_files, "written_file_count": len(written_files)}


__all__ = [
    "DEFAULT_CONFIRMATION_PHRASE",
    "REVIEW_WORKBENCH_CONFIRMATION_DIALOG_KIND",
    "REVIEW_WORKBENCH_CONFIRMATION_DIALOG_SCHEMA_VERSION",
    "build_review_workbench_confirmation_dialog_model",
    "write_review_workbench_confirmation_dialog_model",
]
