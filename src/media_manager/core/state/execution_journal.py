from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def _build_value_summary(entries: list[dict[str, object]], key: str) -> dict[str, int]:
    summary: dict[str, int] = {}
    for item in entries:
        value = item.get(key)
        if value is None:
            continue
        label = str(value)
        summary[label] = summary.get(label, 0) + 1
    return dict(sorted(summary.items()))



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
        "outcome_summary": _build_value_summary(entries, "outcome"),
        "reason_summary": _build_value_summary(entries, "reason"),
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


def load_execution_journal(file_path: str | Path) -> dict[str, object]:
    path = Path(file_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Execution journal must contain a JSON object.")
    if str(payload.get("journal_type", "")) != "execution_journal":
        raise ValueError("Unsupported execution journal type.")
    if int(payload.get("schema_version", 0)) != 1:
        raise ValueError("Unsupported execution journal schema version.")
    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("Execution journal entries must be a JSON list.")
    return payload
