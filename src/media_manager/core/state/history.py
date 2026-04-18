from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(slots=True, frozen=True)
class WorkflowHistoryEntry:
    path: Path
    record_type: str
    command_name: str
    apply_requested: bool
    exit_code: int
    created_at_utc: str
    entry_count: int
    reversible_entry_count: int

    @property
    def successful(self) -> bool:
        return self.exit_code == 0

    @property
    def has_reversible_entries(self) -> bool:
        return self.reversible_entry_count > 0


def _parse_created_at_sort_key(value: str) -> tuple[int, str]:
    text = value.strip()
    if not text:
        return (0, "")
    try:
        return (1, datetime.fromisoformat(text.replace("Z", "+00:00")).isoformat())
    except ValueError:
        return (0, text)


def _load_json_file(path: Path) -> dict[str, object] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def summarize_history_file(path: str | Path) -> WorkflowHistoryEntry | None:
    file_path = Path(path)
    payload = _load_json_file(file_path)
    if payload is None:
        return None

    journal_type = str(payload.get("journal_type", "")).strip()
    if journal_type == "execution_journal":
        return WorkflowHistoryEntry(
            path=file_path,
            record_type="execution_journal",
            command_name=str(payload.get("command_name", "unknown")),
            apply_requested=bool(payload.get("apply_requested", False)),
            exit_code=int(payload.get("exit_code", 0)),
            created_at_utc=str(payload.get("created_at_utc", "")),
            entry_count=int(payload.get("entry_count", 0)),
            reversible_entry_count=int(payload.get("reversible_entry_count", 0)),
        )

    if int(payload.get("schema_version", 0)) == 1 and "command_name" in payload and "payload" in payload:
        nested_payload = payload.get("payload")
        nested_entries = nested_payload.get("entries", []) if isinstance(nested_payload, dict) else []
        entry_count = len(nested_entries) if isinstance(nested_entries, list) else 0
        return WorkflowHistoryEntry(
            path=file_path,
            record_type="run_log",
            command_name=str(payload.get("command_name", "unknown")),
            apply_requested=bool(payload.get("apply_requested", False)),
            exit_code=int(payload.get("exit_code", 0)),
            created_at_utc=str(payload.get("created_at_utc", "")),
            entry_count=entry_count,
            reversible_entry_count=0,
        )

    return None


def scan_history_directory(root_path: str | Path) -> list[WorkflowHistoryEntry]:
    root = Path(root_path)
    if not root.exists() or not root.is_dir():
        return []

    entries: list[WorkflowHistoryEntry] = []
    for path in sorted(root.rglob("*.json"), key=lambda item: str(item).lower()):
        summary = summarize_history_file(path)
        if summary is not None:
            entries.append(summary)

    entries.sort(
        key=lambda item: (
            _parse_created_at_sort_key(item.created_at_utc),
            str(item.path).lower(),
        ),
        reverse=True,
    )
    return entries


def find_latest_history_entry(
    root_path: str | Path,
    *,
    command_name: str | None = None,
) -> WorkflowHistoryEntry | None:
    entries = scan_history_directory(root_path)
    if command_name is None:
        return entries[0] if entries else None

    normalized = command_name.strip().lower()
    for entry in entries:
        if entry.command_name.strip().lower() == normalized:
            return entry
    return None


def build_history_summary(entries: list[WorkflowHistoryEntry]) -> dict[str, object]:
    record_type_summary: dict[str, int] = {}
    command_summary: dict[str, int] = {}
    exit_code_summary: dict[str, int] = {}
    successful_count = 0
    failed_count = 0
    reversible_entry_count = 0
    entries_with_reversible_count = 0
    apply_requested_count = 0
    preview_only_count = 0

    for entry in entries:
        record_type_summary[entry.record_type] = record_type_summary.get(entry.record_type, 0) + 1
        command_summary[entry.command_name] = command_summary.get(entry.command_name, 0) + 1
        exit_key = str(entry.exit_code)
        exit_code_summary[exit_key] = exit_code_summary.get(exit_key, 0) + 1
        if entry.successful:
            successful_count += 1
        else:
            failed_count += 1
        reversible_entry_count += entry.reversible_entry_count
        if entry.has_reversible_entries:
            entries_with_reversible_count += 1
        if entry.apply_requested:
            apply_requested_count += 1
        else:
            preview_only_count += 1

    latest_created_at_utc = entries[0].created_at_utc if entries else ""

    summary = {
        "entry_count": len(entries),
        "total_entries": len(entries),
        "successful_count": successful_count,
        "failed_count": failed_count,
        "reversible_entry_count": reversible_entry_count,
        "entries_with_reversible_count": entries_with_reversible_count,
        "command_summary": dict(sorted(command_summary.items())),
        "command_name_summary": dict(sorted(command_summary.items())),
        "record_type_summary": dict(sorted(record_type_summary.items())),
        "apply_summary": {
            "apply_requested": apply_requested_count,
            "preview_only": preview_only_count,
        },
        "exit_code_summary": dict(sorted(exit_code_summary.items())),
        "latest_created_at_utc": latest_created_at_utc,
    }
    return summary
