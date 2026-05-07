from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

REVIEW_WORKBENCH_APPLY_PREVIEW_SCHEMA_VERSION = "1.0"
REVIEW_WORKBENCH_APPLY_PREVIEW_KIND = "ui_review_workbench_apply_preview"


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


def _selected_lane(service_bundle: Mapping[str, Any]) -> Mapping[str, Any]:
    view_model = _as_mapping(service_bundle.get("view_model"))
    selected = _as_mapping(view_model.get("selected_lane"))
    if selected:
        return selected
    selected_lane_id = _text(view_model.get("selected_lane_id"))
    for lane in _as_list(view_model.get("lanes")):
        lane_map = _as_mapping(lane)
        if _text(lane_map.get("lane_id")) == selected_lane_id:
            return lane_map
    return {}


def _review_status_from_plan(reviewed_decision_plan: Mapping[str, Any]) -> dict[str, object]:
    if not reviewed_decision_plan:
        return {
            "has_reviewed_decision_plan": False,
            "safe_to_preview_apply": False,
            "safe_to_apply": False,
            "blocked_reason": "No reviewed decision plan was provided.",
            "reviewed_decision_count": 0,
            "blocked_decision_count": 0,
            "unresolved_decision_count": 0,
        }

    summary = _as_mapping(reviewed_decision_plan.get("summary"))
    status_text = _text(reviewed_decision_plan.get("status") or summary.get("status"), "unknown").lower().replace("-", "_")
    explicit_safe = reviewed_decision_plan.get("safe_to_apply") is True or summary.get("safe_to_apply") is True
    explicit_preview = reviewed_decision_plan.get("safe_to_preview_apply") is True or summary.get("safe_to_preview_apply") is True
    reviewed_count = _as_int(
        reviewed_decision_plan.get(
            "reviewed_decision_count",
            summary.get("reviewed_decision_count", summary.get("decision_count", summary.get("ready_group_count", 0))),
        )
    )
    blocked_count = _as_int(reviewed_decision_plan.get("blocked_decision_count", summary.get("blocked_decision_count", summary.get("blocked_group_count", 0))))
    unresolved_count = _as_int(reviewed_decision_plan.get("unresolved_decision_count", summary.get("unresolved_decision_count", summary.get("unresolved_group_count", 0))))
    has_errors = _as_int(reviewed_decision_plan.get("error_count", summary.get("error_count", 0))) > 0
    plan_ready_status = status_text in {"ok", "ready", "reviewed", "preview_ready", "safe", "safe_to_apply"}
    safe_to_preview_apply = (explicit_preview or explicit_safe or plan_ready_status) and blocked_count == 0 and unresolved_count == 0 and not has_errors
    blocked_reason = None
    if not safe_to_preview_apply:
        reasons: list[str] = []
        if blocked_count:
            reasons.append(f"{blocked_count} reviewed decision(s) are blocked.")
        if unresolved_count:
            reasons.append(f"{unresolved_count} reviewed decision(s) remain unresolved.")
        if has_errors:
            reasons.append("The reviewed decision plan reports errors.")
        if not reasons and not (explicit_preview or explicit_safe or plan_ready_status):
            reasons.append("The reviewed decision plan is not marked ready for apply preview.")
        blocked_reason = " ".join(reasons)

    return {
        "has_reviewed_decision_plan": True,
        "safe_to_preview_apply": bool(safe_to_preview_apply),
        "safe_to_apply": explicit_safe and bool(safe_to_preview_apply),
        "blocked_reason": blocked_reason,
        "status": status_text,
        "reviewed_decision_count": reviewed_count,
        "blocked_decision_count": blocked_count,
        "unresolved_decision_count": unresolved_count,
    }


def _candidate_commands(
    *,
    selected_lane: Mapping[str, Any],
    reviewed_decision_plan: Mapping[str, Any],
    review_status: Mapping[str, Any],
) -> list[dict[str, object]]:
    lane_id = _text(selected_lane.get("lane_id"), "review-workbench")
    page_id = _text(selected_lane.get("page_id"), "run-history")
    raw_commands = reviewed_decision_plan.get("command_preview") or reviewed_decision_plan.get("commands") or reviewed_decision_plan.get("candidate_commands")
    command_rows: list[dict[str, object]] = []
    if isinstance(raw_commands, list):
        for index, command in enumerate(raw_commands, start=1):
            if isinstance(command, list):
                argv = [str(part) for part in command]
            elif isinstance(command, Mapping):
                argv_value = command.get("argv") or command.get("command_preview")
                argv = [str(part) for part in argv_value] if isinstance(argv_value, list) else []
            else:
                argv = []
            if argv:
                command_rows.append(
                    {
                        "id": f"reviewed-command-{index}",
                        "label": f"Reviewed command {index}",
                        "argv": argv,
                        "source": "reviewed_decision_plan",
                        "executes_commands": False,
                        "requires_explicit_user_confirmation": True,
                    }
                )
    if command_rows:
        return command_rows

    return [
        {
            "id": f"preview-apply-{lane_id}",
            "label": f"Preview apply for {lane_id}",
            "argv": [
                "media-manager",
                "app-services",
                "review-workbench-apply-preview",
                "--selected-lane",
                lane_id,
                "--json",
            ],
            "source": "generated_safe_preview",
            "target_page_id": page_id,
            "enabled": bool(review_status.get("safe_to_preview_apply")),
            "executes_commands": False,
            "requires_explicit_user_confirmation": True,
        }
    ]


def build_review_workbench_apply_preview(
    service_bundle: Mapping[str, Any],
    reviewed_decision_plan: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    """Build a non-executing apply-preview contract for the Review Workbench.

    This deliberately does not apply decisions. It only turns a reviewed decision
    payload into a GUI command-plan preview that can be inspected and explicitly
    confirmed by a future desktop shell.
    """

    reviewed_plan = _as_mapping(reviewed_decision_plan)
    selected_lane = _selected_lane(service_bundle)
    selected_lane_id = _text(selected_lane.get("lane_id")) or None
    view_model = _as_mapping(service_bundle.get("view_model"))
    summary = _as_mapping(view_model.get("summary"))
    review_status = _review_status_from_plan(reviewed_plan)
    safe_to_preview_apply = bool(review_status.get("safe_to_preview_apply"))
    commands = _candidate_commands(selected_lane=selected_lane, reviewed_decision_plan=reviewed_plan, review_status=review_status)
    enabled_command_count = sum(1 for command in commands if _as_mapping(command).get("enabled", safe_to_preview_apply) is True)
    blockers: list[str] = []
    if not selected_lane_id:
        blockers.append("No review lane is selected.")
    blocked_reason = _text(review_status.get("blocked_reason"))
    if blocked_reason:
        blockers.append(blocked_reason)
    ready = not blockers and safe_to_preview_apply
    confirmation = {
        "required": True,
        "confirmation_phrase": "APPLY REVIEWED DECISIONS",
        "requires_fresh_preview": True,
        "requires_reviewed_decision_plan": True,
        "requires_user_confirmation": True,
        "executes_commands": False,
    }
    command_plan_preview = {
        "kind": "ui_review_workbench_reviewed_command_plan_preview",
        "plan_id": "review-workbench-apply-reviewed-decisions-preview",
        "title": "Apply reviewed decisions preview",
        "enabled": False,
        "preview_ready": ready,
        "selected_lane_id": selected_lane_id,
        "candidate_command_count": len(commands),
        "enabled_candidate_command_count": enabled_command_count if ready else 0,
        "commands": commands,
        "confirmation": confirmation,
        "blocked_reasons": blockers,
        "executes_commands": False,
        "opens_window": False,
        "requires_pyside6": False,
    }
    return {
        "schema_version": REVIEW_WORKBENCH_APPLY_PREVIEW_SCHEMA_VERSION,
        "kind": REVIEW_WORKBENCH_APPLY_PREVIEW_KIND,
        "generated_at_utc": _now_utc(),
        "selected_lane_id": selected_lane_id,
        "selected_lane_status": selected_lane.get("status") if selected_lane else None,
        "review_status": review_status,
        "command_plan_preview": command_plan_preview,
        "readiness": {
            "ready": ready,
            "status": "preview_ready" if ready else "blocked",
            "blocked_reasons": blockers,
            "next_action": (
                "Render the reviewed command plan preview and require explicit confirmation before enabling any apply execution path."
                if ready
                else "Load a clean reviewed decision plan before surfacing an apply confirmation."
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
            "lane_count": summary.get("lane_count", 0),
            "attention_count": summary.get("attention_count", 0),
            "selected_lane_id": selected_lane_id,
            "reviewed_decision_count": review_status.get("reviewed_decision_count", 0),
            "blocked_decision_count": review_status.get("blocked_decision_count", 0),
            "unresolved_decision_count": review_status.get("unresolved_decision_count", 0),
            "candidate_command_count": len(commands),
            "preview_ready": ready,
            "apply_enabled": False,
            "status": "preview_ready" if ready else "blocked",
        },
    }


def write_review_workbench_apply_preview(
    out_dir: str | Path,
    service_bundle: Mapping[str, Any],
    reviewed_decision_plan: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    payload = build_review_workbench_apply_preview(service_bundle, reviewed_decision_plan=reviewed_decision_plan)
    files: list[tuple[str, Mapping[str, Any]]] = [
        ("review_workbench_apply_preview.json", payload),
        ("review_workbench_reviewed_command_plan_preview.json", _as_mapping(payload.get("command_plan_preview"))),
    ]
    written_files: list[str] = []
    for filename, item in files:
        path = root / filename
        _write_json(path, item)
        written_files.append(str(path))
    readme = root / "README.txt"
    readme.write_text(
        "Review Workbench apply preview\n"
        "Generated by media-manager app-services review-workbench-apply-preview.\n"
        "This is a non-executing confirmation contract. It does not apply media operations or write catalogs.\n",
        encoding="utf-8",
    )
    written_files.append(str(readme))
    return {**payload, "output_dir": str(root), "written_files": written_files, "written_file_count": len(written_files)}


__all__ = [
    "REVIEW_WORKBENCH_APPLY_PREVIEW_KIND",
    "REVIEW_WORKBENCH_APPLY_PREVIEW_SCHEMA_VERSION",
    "build_review_workbench_apply_preview",
    "write_review_workbench_apply_preview",
]
