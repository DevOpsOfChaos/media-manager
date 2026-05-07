from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

REVIEW_WORKBENCH_EXECUTOR_HANDOFF_PANEL_SCHEMA_VERSION = "1.0"
REVIEW_WORKBENCH_EXECUTOR_HANDOFF_PANEL_KIND = "ui_review_workbench_apply_executor_handoff_panel"


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


def _as_bool(value: object, default: bool = False) -> bool:
    return value if isinstance(value, bool) else default


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


def _checklist_rows(confirmation_dialog: Mapping[str, Any]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index, item in enumerate(_as_list(confirmation_dialog.get("checklist")), start=1):
        check = _as_mapping(item)
        rows.append(
            {
                "index": index,
                "id": _text(check.get("id"), f"confirmation-check-{index}"),
                "label": _text(check.get("label"), f"Confirmation check {index}"),
                "required": _as_bool(check.get("required"), True),
                "satisfied": _as_bool(check.get("satisfied"), False),
                "blocked_reason": check.get("blocked_reason"),
                "source": "confirmation_dialog",
            }
        )
    return rows


def _preflight_rows(apply_executor_contract: Mapping[str, Any]) -> list[dict[str, object]]:
    preflight = _as_mapping(apply_executor_contract.get("preflight"))
    rows: list[dict[str, object]] = []
    for index, item in enumerate(_as_list(preflight.get("checks")), start=1):
        check = _as_mapping(item)
        rows.append(
            {
                "index": index,
                "id": _text(check.get("id"), f"preflight-check-{index}"),
                "label": _text(check.get("label"), f"Preflight check {index}"),
                "required": _as_bool(check.get("required"), True),
                "satisfied": _as_bool(check.get("satisfied"), False),
                "blocked_reason": check.get("blocked_reason"),
                "source": "apply_executor_contract",
            }
        )
    return rows


def _command_rows(apply_executor_contract: Mapping[str, Any]) -> list[dict[str, object]]:
    dry_run = _as_mapping(apply_executor_contract.get("dry_run_execution_plan"))
    rows: list[dict[str, object]] = []
    for index, command in enumerate(_as_list(dry_run.get("commands")), start=1):
        item = _as_mapping(command)
        rows.append(
            {
                "index": index,
                "id": _text(item.get("id"), f"dry-run-command-{index}"),
                "label": _text(item.get("label"), f"Dry-run command {index}"),
                "argv_preview": _text(item.get("argv_preview"), " ".join(str(part) for part in _as_list(item.get("argv")))),
                "enabled_in_preview": _as_bool(item.get("enabled_in_preview"), False),
                "enabled_for_execution": False,
                "executable_in_this_contract": False,
                "executes_commands": False,
                "source": _text(item.get("source"), "dry_run_execution_plan"),
            }
        )
    return rows


def _audit_rows(apply_executor_contract: Mapping[str, Any]) -> list[dict[str, object]]:
    audit = _as_mapping(apply_executor_contract.get("audit_plan"))
    keys = [
        "audit_event_kind",
        "audit_required_before_future_execution",
        "selected_lane_id",
        "risk_level",
        "reviewed_decision_count",
        "candidate_command_count",
        "typed_confirmation_provided",
        "typed_confirmation_matches",
        "dry_run",
        "execution_enabled",
        "local_only",
    ]
    return [
        {
            "id": str(key),
            "label": str(key).replace("_", " ").title(),
            "value": audit.get(key),
            "source": "apply_executor_audit_plan",
        }
        for key in keys
        if key in audit
    ]


def build_review_workbench_executor_handoff_panel(
    confirmation_dialog: Mapping[str, Any],
    apply_executor_contract: Mapping[str, Any],
) -> dict[str, object]:
    """Build the GUI-facing handoff panel between confirmation and future executor.

    The panel is display-only. It combines the guarded confirmation dialog, the
    disabled-by-default executor contract, preflight checks, dry-run commands,
    and audit metadata into a layout payload that a Qt page can render without
    enabling command execution.
    """

    dialog = _as_mapping(confirmation_dialog)
    executor = _as_mapping(apply_executor_contract)
    dialog_summary = _as_mapping(dialog.get("summary"))
    executor_summary = _as_mapping(executor.get("summary"))
    confirmation = _as_mapping(dialog.get("confirmation"))
    preflight = _as_mapping(executor.get("preflight"))
    mutation_policy = _as_mapping(executor.get("mutation_policy"))
    capabilities = _as_mapping(executor.get("capabilities"))

    confirmation_rows = _checklist_rows(dialog)
    preflight_rows = _preflight_rows(executor)
    command_rows = _command_rows(executor)
    audit_rows = _audit_rows(executor)
    blocked_reasons = [str(item) for item in _as_list(preflight.get("blocked_reasons"))]
    status = _text(executor_summary.get("status") or executor.get("status"), "blocked")
    renderable = bool(dialog) and bool(executor) and capabilities.get("executes_commands") is False
    ready_for_future_executor = _as_bool(executor_summary.get("ready_for_future_executor"), False)

    sections: list[dict[str, object]] = [
        {
            "id": "risk-summary",
            "title": "Risk summary",
            "region": "top",
            "component": "summary_strip",
            "items": [
                {"label": "Selected lane", "value": dialog_summary.get("selected_lane_id") or executor_summary.get("selected_lane_id")},
                {"label": "Risk", "value": dialog_summary.get("risk_level") or executor_summary.get("risk_level")},
                {"label": "Status", "value": status},
                {"label": "Ready for future executor", "value": ready_for_future_executor},
            ],
        },
        {
            "id": "typed-confirmation",
            "title": "Typed confirmation gate",
            "region": "left",
            "component": "typed_confirmation_gate",
            "phrase": confirmation.get("phrase") or _as_mapping(executor.get("confirmation_gate")).get("phrase"),
            "typed_confirmation_persisted": False,
            "typed_confirmation_matches": _as_bool(executor_summary.get("typed_confirmation_matches"), False),
            "all_generated_checks_satisfied": _as_bool(confirmation.get("all_generated_checks_satisfied"), False),
            "rows": confirmation_rows,
        },
        {
            "id": "preflight",
            "title": "Executor preflight",
            "region": "left",
            "component": "preflight_checklist",
            "status": preflight.get("status"),
            "failed_check_count": _as_int(preflight.get("failed_check_count")),
            "rows": preflight_rows,
        },
        {
            "id": "dry-run-plan",
            "title": "Dry-run command plan",
            "region": "right",
            "component": "dry_run_command_table",
            "rows": command_rows,
            "candidate_command_count": len(command_rows),
            "execution_enabled": False,
            "executes_commands": False,
        },
        {
            "id": "audit-plan",
            "title": "Audit handoff",
            "region": "right",
            "component": "audit_key_value_panel",
            "rows": audit_rows,
            "audit_required_before_future_execution": True,
        },
        {
            "id": "blocked-actions",
            "title": "Blocked actions",
            "region": "bottom",
            "component": "disabled_action_bar",
            "actions": [
                {
                    "id": "copy_dry_run_plan",
                    "label": "Copy dry-run plan",
                    "enabled": bool(command_rows),
                    "executes_commands": False,
                },
                {
                    "id": "export_audit_plan",
                    "label": "Export audit plan",
                    "enabled": bool(audit_rows),
                    "executes_commands": False,
                },
                {
                    "id": "confirm_apply",
                    "label": "Confirm apply",
                    "enabled": False,
                    "disabled_reason": "Execution remains disabled in the handoff panel.",
                    "executes_commands": False,
                },
            ],
            "blocked_reasons": blocked_reasons,
        },
    ]

    return {
        "schema_version": REVIEW_WORKBENCH_EXECUTOR_HANDOFF_PANEL_SCHEMA_VERSION,
        "kind": REVIEW_WORKBENCH_EXECUTOR_HANDOFF_PANEL_KIND,
        "generated_at_utc": _now_utc(),
        "panel_id": "review-workbench-apply-executor-handoff",
        "title": "Review Workbench apply handoff",
        "description": "Display-only handoff panel for confirmation, preflight, dry-run, and audit data before any future executor implementation.",
        "selected_lane_id": dialog_summary.get("selected_lane_id") or executor_summary.get("selected_lane_id"),
        "status": "renderable" if renderable else "blocked",
        "executor_status": status,
        "layout": {
            "kind": "split_confirmation_executor_handoff",
            "regions": ["top", "left", "right", "bottom"],
            "primary_region": "right",
            "confirmation_region": "left",
            "audit_region": "right",
        },
        "sections": sections,
        "blocked_reasons": blocked_reasons,
        "mutation_policy": {
            "mode": mutation_policy.get("mode", "disabled_by_default"),
            "apply_enabled": False,
            "execution_enabled": False,
            "dry_run_only": True,
            "runs_subprocesses": False,
            "writes_media_files": False,
            "writes_catalogs": False,
            "requires_fresh_confirmation_dialog": True,
            "requires_audit_record": True,
        },
        "readiness": {
            "ready": renderable,
            "status": "renderable" if renderable else "blocked",
            "next_action": (
                "Render this panel in the Review Workbench and keep the future executor disabled."
                if renderable
                else "Build confirmation and executor contracts before rendering the handoff panel."
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
            "selected_lane_id": dialog_summary.get("selected_lane_id") or executor_summary.get("selected_lane_id"),
            "status": "renderable" if renderable else "blocked",
            "executor_status": status,
            "risk_level": dialog_summary.get("risk_level") or executor_summary.get("risk_level"),
            "section_count": len(sections),
            "confirmation_check_count": len(confirmation_rows),
            "preflight_check_count": len(preflight_rows),
            "preflight_failed_check_count": len(blocked_reasons),
            "dry_run_command_count": len(command_rows),
            "audit_row_count": len(audit_rows),
            "typed_confirmation_matches": _as_bool(executor_summary.get("typed_confirmation_matches"), False),
            "ready_for_future_executor": ready_for_future_executor,
            "apply_enabled": False,
            "execution_enabled": False,
            "executes_commands": False,
        },
    }


def write_review_workbench_executor_handoff_panel(
    out_dir: str | Path,
    confirmation_dialog: Mapping[str, Any],
    apply_executor_contract: Mapping[str, Any],
) -> dict[str, object]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = build_review_workbench_executor_handoff_panel(confirmation_dialog, apply_executor_contract)
    sections = [section for section in _as_list(payload.get("sections")) if isinstance(section, Mapping)]
    files: list[tuple[str, Mapping[str, Any]]] = [
        ("review_workbench_apply_executor_handoff_panel.json", payload),
        ("review_workbench_apply_handoff_risk_summary.json", _as_mapping(sections[0]) if len(sections) > 0 else {}),
        ("review_workbench_apply_handoff_preflight.json", _as_mapping(sections[2]) if len(sections) > 2 else {}),
        ("review_workbench_apply_handoff_dry_run_plan.json", _as_mapping(sections[3]) if len(sections) > 3 else {}),
        ("review_workbench_apply_handoff_audit_plan.json", _as_mapping(sections[4]) if len(sections) > 4 else {}),
    ]
    written_files: list[str] = []
    for filename, item in files:
        path = root / filename
        _write_json(path, item)
        written_files.append(str(path))
    readme = root / "README.txt"
    readme.write_text(
        "Review Workbench apply executor handoff panel\n"
        "Generated by media-manager app-services review-workbench-apply-handoff-panel.\n"
        "This is display-only UI data. It does not run commands, mutate catalogs, or apply media operations.\n",
        encoding="utf-8",
    )
    written_files.append(str(readme))
    return {**payload, "output_dir": str(root), "written_files": written_files, "written_file_count": len(written_files)}


__all__ = [
    "REVIEW_WORKBENCH_EXECUTOR_HANDOFF_PANEL_KIND",
    "REVIEW_WORKBENCH_EXECUTOR_HANDOFF_PANEL_SCHEMA_VERSION",
    "build_review_workbench_executor_handoff_panel",
    "write_review_workbench_executor_handoff_panel",
]
