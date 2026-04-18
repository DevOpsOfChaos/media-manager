from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def build_command_run_log(
    *,
    command_name: str,
    apply_requested: bool,
    exit_code: int,
    payload: dict[str, object],
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "command_name": command_name,
        "apply_requested": apply_requested,
        "exit_code": exit_code,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
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
