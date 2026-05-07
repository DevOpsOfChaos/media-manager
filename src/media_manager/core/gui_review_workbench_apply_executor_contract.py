from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

REVIEW_WORKBENCH_APPLY_EXECUTOR_CONTRACT_SCHEMA_VERSION = "1.0"
REVIEW_WORKBENCH_APPLY_EXECUTOR_CONTRACT_KIND = "ui_review_workbench_apply_executor_contract"
DEFAULT_EXECUTOR_CONFIRMATION_PHRASE = "APPLY REVIEWED DECISIONS"


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object, fallback: str = "") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text or fallback


def _as_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _confirmation_phrase(confirmation_dialog: Mapping[str, Any], fallback: str = DEFAULT_EXECUTOR_CONFIRMATION_PHRASE) -> str:
    confirmation = _as_mapping(confirmation_dialog.get("confirmation"))
    return _text(confirmation.get("phrase"), fallback)


def _command_rows(confirmation_dialog: Mapping[str, Any]) -> list[dict[str, object]]:
    command_plan = _as_mapping(confirmation_dialog.get("command_plan_preview"))
    rows: list[dict[str, object]] = []
    for index, command in enumerate(_as_list(command_plan.get("commands")), start=1):
        command_map = _as_mapping(command)
        argv = [str(part) for part in _as_list(command_map.get("argv"))]
        rows.append(
            {
                "index": index,
                "id": _text(command_map.get("id"), f"command-{index}"),
                "label": _text(command_map.get("label"), f"Command {index}"),
                "argv": argv,
                "argv_preview": _text(command_map.get("argv_preview"), " ".join(argv)),
                "source": _text(command_map.get("source"), "confirmation_dialog"),
                "enabled_in_preview": command_map.get("enabled", True) is True,
                "enabled_for_execution": False,
                "executable_in_this_contract": False,
                "executes_commands": False,
                "requires_explicit_user_confirmation": True,
            }
        )
    return rows


def _required_dialog_checks(confirmation_dialog: Mapping[str, Any]) -> tuple[int, int]:
    required = [item for item in _as_list(confirmation_dialog.get("checklist")) if _as_mapping(item).get("required") is True]
    satisfied = [item for item in required if _as_mapping(item).get("satisfied") is True]
    return len(required), len(satisfied)


def build_review_workbench_apply_executor_contract(
    confirmation_dialog: Mapping[str, Any],
    *,
    typed_confirmation: str | None = None,
    executor_enabled: bool = False,
    dry_run: bool = True,
) -> dict[str, object]:
    """Build the disabled-by-default Review Workbench apply executor contract.

    This is not the executor implementation. It formalizes the future execution
    boundary behind the confirmation dialog: preflight checks, audit data,
    dry-run command previews, and explicit disabled-by-default safety gates.
    The payload deliberately never executes commands or media operations.
    """

    dialog = _as_mapping(confirmation_dialog)
    summary = _as_mapping(dialog.get("summary"))
    readiness = _as_mapping(dialog.get("readiness"))
    capabilities = _as_mapping(dialog.get("capabilities"))
    phrase = _confirmation_phrase(dialog)
    typed_value = _text(typed_confirmation)
    typed_matches = bool(typed_value) and typed_value == phrase
    dialog_ready = readiness.get("ready") is True and summary.get("status") == "confirmation_ready"
    non_executing_dialog = capabilities.get("executes_commands") is False and capabilities.get("executes_media_operations") is False
    command_rows = _command_rows(dialog)
    required_check_count, required_satisfied_count = _required_dialog_checks(dialog)
    generated_checks_satisfied = _as_mapping(dialog.get("confirmation")).get("all_generated_checks_satisfied") is True

    preflight_checks = [
        {
            "id": "confirmation-dialog-ready",
            "label": "The guarded confirmation dialog is ready.",
            "required": True,
            "satisfied": dialog_ready,
            "blocked_reason": None if dialog_ready else "Confirmation dialog is blocked or stale.",
        },
        {
            "id": "generated-dialog-checks-satisfied",
            "label": "All generated confirmation checks except typed input are satisfied.",
            "required": True,
            "satisfied": generated_checks_satisfied,
            "blocked_reason": None if generated_checks_satisfied else "Generated confirmation checklist is incomplete.",
        },
        {
            "id": "typed-confirmation-matches",
            "label": f"Typed confirmation phrase matches: {phrase}",
            "required": True,
            "satisfied": typed_matches,
            "blocked_reason": None if typed_matches else "Typed confirmation phrase is missing or does not match.",
        },
        {
            "id": "candidate-command-plan-visible",
            "label": "A candidate command plan is available for dry-run preview.",
            "required": True,
            "satisfied": bool(command_rows),
            "blocked_reason": None if command_rows else "No candidate command plan is available.",
        },
        {
            "id": "dry-run-only",
            "label": "This contract remains dry-run only.",
            "required": True,
            "satisfied": dry_run is True,
            "blocked_reason": None if dry_run is True else "Dry-run mode was disabled.",
        },
        {
            "id": "executor-disabled-by-default",
            "label": "The future executor flag is disabled by default.",
            "required": True,
            "satisfied": executor_enabled is False,
            "blocked_reason": None if executor_enabled is False else "Executor enablement was requested; this contract refuses execution.",
        },
        {
            "id": "non-executing-contract",
            "label": "The contract does not execute commands or media operations.",
            "required": True,
            "satisfied": non_executing_dialog,
            "blocked_reason": None if non_executing_dialog else "Upstream dialog capabilities are not non-executing.",
        },
    ]
    blockers = [str(item["blocked_reason"]) for item in preflight_checks if item["required"] is True and not item["satisfied"]]
    typed_gate_ready = dialog_ready and generated_checks_satisfied and typed_matches and bool(command_rows) and non_executing_dialog
    future_executor_eligible = typed_gate_ready and dry_run is True and executor_enabled is False
    status = "future_executor_eligible" if future_executor_eligible else "blocked"
    if executor_enabled:
        status = "execution_refused"
    elif not typed_matches and dialog_ready and generated_checks_satisfied and bool(command_rows):
        status = "awaiting_typed_confirmation"

    dry_run_plan = {
        "plan_id": "review-workbench-apply-dry-run-executor-plan",
        "title": "Review Workbench apply dry-run executor plan",
        "dry_run": True,
        "execution_enabled": False,
        "future_executor_eligible": future_executor_eligible,
        "candidate_command_count": len(command_rows),
        "commands": command_rows,
        "executes_commands": False,
        "executes_media_operations": False,
    }
    audit_plan = {
        "audit_event_kind": "review_workbench_apply_executor_contract_built",
        "audit_required_before_future_execution": True,
        "selected_lane_id": summary.get("selected_lane_id"),
        "risk_level": summary.get("risk_level"),
        "reviewed_decision_count": _as_int(summary.get("reviewed_decision_count")),
        "candidate_command_count": len(command_rows),
        "typed_confirmation_provided": bool(typed_value),
        "typed_confirmation_matches": typed_matches,
        "dry_run": True,
        "execution_enabled": False,
        "local_only": True,
    }
    return {
        "schema_version": REVIEW_WORKBENCH_APPLY_EXECUTOR_CONTRACT_SCHEMA_VERSION,
        "kind": REVIEW_WORKBENCH_APPLY_EXECUTOR_CONTRACT_KIND,
        "generated_at_utc": _now_utc(),
        "contract_id": "review-workbench-apply-executor-disabled-contract",
        "title": "Review Workbench apply executor contract",
        "description": "Disabled-by-default executor boundary for a future reviewed apply path.",
        "selected_lane_id": summary.get("selected_lane_id"),
        "status": status,
        "confirmation_gate": {
            "required": True,
            "phrase": phrase,
            "typed_confirmation_provided": bool(typed_value),
            "typed_confirmation_matches": typed_matches,
            "typed_confirmation_is_persisted": False,
            "required_check_count": required_check_count,
            "required_satisfied_count": required_satisfied_count,
        },
        "preflight": {
            "ready_for_future_executor": future_executor_eligible,
            "status": status,
            "check_count": len(preflight_checks),
            "failed_check_count": len(blockers),
            "checks": preflight_checks,
            "blocked_reasons": blockers,
        },
        "dry_run_execution_plan": dry_run_plan,
        "audit_plan": audit_plan,
        "mutation_policy": {
            "mode": "disabled_by_default",
            "apply_enabled": False,
            "execution_enabled": False,
            "dry_run_only": True,
            "requires_separate_executor_implementation": True,
            "requires_fresh_confirmation_dialog": True,
            "requires_audit_record": True,
            "writes_media_files": False,
            "writes_catalogs": False,
            "runs_subprocesses": False,
        },
        "readiness": {
            "ready": future_executor_eligible,
            "status": status,
            "blocked_reasons": blockers,
            "next_action": (
                "Keep execution disabled; a future executor implementation may consume this dry-run plan only after separate enablement and audit wiring."
                if future_executor_eligible
                else "Resolve preflight blockers before the GUI may present a future executor handoff."
            ),
        },
        "capabilities": {
            "headless_testable": True,
            "requires_pyside6": False,
            "opens_window": False,
            "executes_commands": False,
            "executes_media_operations": False,
            "apply_enabled": False,
            "execution_enabled": False,
            "dry_run_only": True,
            "confirmation_required": True,
            "local_only": True,
        },
        "summary": {
            "selected_lane_id": summary.get("selected_lane_id"),
            "status": status,
            "risk_level": summary.get("risk_level"),
            "reviewed_decision_count": _as_int(summary.get("reviewed_decision_count")),
            "candidate_command_count": len(command_rows),
            "preflight_check_count": len(preflight_checks),
            "preflight_failed_check_count": len(blockers),
            "typed_confirmation_matches": typed_matches,
            "ready_for_future_executor": future_executor_eligible,
            "apply_enabled": False,
            "execution_enabled": False,
            "executes_commands": False,
        },
    }


def write_review_workbench_apply_executor_contract(
    out_dir: str | Path,
    confirmation_dialog: Mapping[str, Any],
    *,
    typed_confirmation: str | None = None,
    executor_enabled: bool = False,
    dry_run: bool = True,
) -> dict[str, object]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = build_review_workbench_apply_executor_contract(
        confirmation_dialog,
        typed_confirmation=typed_confirmation,
        executor_enabled=executor_enabled,
        dry_run=dry_run,
    )
    files: list[tuple[str, Mapping[str, Any]]] = [
        ("review_workbench_apply_executor_contract.json", payload),
        ("review_workbench_apply_executor_preflight.json", _as_mapping(payload.get("preflight"))),
        ("review_workbench_apply_executor_audit_plan.json", _as_mapping(payload.get("audit_plan"))),
        ("review_workbench_apply_dry_run_execution_plan.json", _as_mapping(payload.get("dry_run_execution_plan"))),
    ]
    written_files: list[str] = []
    for filename, item in files:
        path = root / filename
        _write_json(path, item)
        written_files.append(str(path))
    readme = root / "README.txt"
    readme.write_text(
        "Review Workbench apply executor contract\n"
        "Generated by media-manager app-services review-workbench-apply-executor-contract.\n"
        "This is a disabled-by-default dry-run contract. It does not run commands, mutate catalogs, or apply media operations.\n",
        encoding="utf-8",
    )
    written_files.append(str(readme))
    return {**payload, "output_dir": str(root), "written_files": written_files, "written_file_count": len(written_files)}


__all__ = [
    "DEFAULT_EXECUTOR_CONFIRMATION_PHRASE",
    "REVIEW_WORKBENCH_APPLY_EXECUTOR_CONTRACT_KIND",
    "REVIEW_WORKBENCH_APPLY_EXECUTOR_CONTRACT_SCHEMA_VERSION",
    "build_review_workbench_apply_executor_contract",
    "write_review_workbench_apply_executor_contract",
]
