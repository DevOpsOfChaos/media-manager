from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def _coerce_int(value: object) -> int | None:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    return None


SUMMARY_KEYS = (
    "total_files",
    "media_file_count",
    "planned_count",
    "skipped_count",
    "conflict_count",
    "error_count",
    "warning_count",
)

EXECUTION_SUMMARY_KEYS = (
    "processed_count",
    "executed_count",
    "copied_count",
    "moved_count",
    "preview_count",
    "renamed_count",
    "skipped_count",
    "conflict_count",
    "error_count",
)


def _build_payload_summary(payload: dict[str, object]) -> dict[str, object]:
    summary: dict[str, object] = {
        "top_level_keys": sorted(payload.keys()),
    }

    for key in SUMMARY_KEYS:
        value = _coerce_int(payload.get(key))
        if value is not None:
            summary[key] = value

    execution = payload.get("execution")
    if isinstance(execution, dict):
        execution_summary: dict[str, int] = {}
        for key in EXECUTION_SUMMARY_KEYS:
            value = _coerce_int(execution.get(key))
            if value is not None:
                execution_summary[key] = value
        if execution_summary:
            summary["execution"] = execution_summary

    return summary


def build_command_run_log(
    *,
    command_name: str,
    apply_requested: bool,
    exit_code: int,
    payload: dict[str, object],
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "log_type": "command_run_log",
        "command_name": command_name,
        "apply_requested": apply_requested,
        "exit_code": exit_code,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "payload_summary": _build_payload_summary(payload),
        "payload": payload,
    }


def write_command_run_log(
    file_path: str | Path,
    *,
    command_name: str,
    apply_requested: bool,
    exit_code: int,
    payload: dict[str, object],
) -> Path:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = build_command_run_log(
        command_name=command_name,
        apply_requested=apply_requested,
        exit_code=exit_code,
        payload=payload,
    )
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
