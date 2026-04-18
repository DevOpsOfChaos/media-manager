from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def build_execution_journal(
    *,
    command_name: str,
    apply_requested: bool,
    exit_code: int,
    entries: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "journal_type": "execution_journal",
        "command_name": command_name,
        "apply_requested": apply_requested,
        "exit_code": exit_code,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "entry_count": len(entries),
        "reversible_entry_count": sum(1 for item in entries if bool(item.get("reversible"))),
        "entries": entries,
    }


def write_execution_journal(
    file_path: str | Path,
    *,
    command_name: str,
    apply_requested: bool,
    exit_code: int,
    entries: list[dict[str, object]],
) -> Path:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_execution_journal(
        command_name=command_name,
        apply_requested=apply_requested,
        exit_code=exit_code,
        entries=entries,
    )
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
