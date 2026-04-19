from __future__ import annotations

import json
from dataclasses import dataclass, field
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


@dataclass(slots=True, frozen=True)
class WorkflowHistoryCommandSummary:
    command_name: str
    entry_count: int
    successful_count: int
    failed_count: int
    apply_requested_count: int
    preview_only_count: int
    reversible_entry_count: int
    entries_with_reversible_count: int
    latest_created_at_utc: str
    latest_path: str
    latest_record_type: str
    latest_exit_code: int
    record_type_summary: dict[str, int] = field(default_factory=dict)
    exit_code_summary: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "command_name": self.command_name,
            "entry_count": self.entry_count,
            "successful_count": self.successful_count,
            "failed_count": self.failed_count,
            "apply_requested_count": self.apply_requested_count,
            "preview_only_count": self.preview_only_count,
            "reversible_entry_count": self.reversible_entry_count,
            "entries_with_reversible_count": self.entries_with_reversible_count,
            "latest_created_at_utc": self.latest_created_at_utc,
            "latest_path": self.latest_path,
            "latest_record_type": self.latest_record_type,
            "latest_exit_code": self.latest_exit_code,
            "record_type_summary": dict(self.record_type_summary),
            "exit_code_summary": dict(self.exit_code_summary),
        }


def _parse_timestamp(value: str) -> datetime | None:
    text = value.strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def _history_sort_key(item: WorkflowHistoryEntry) -> tuple[int, str, str]:
    parsed = _parse_timestamp(item.created_at_utc)
    if parsed is None:
        return (0, item.created_at_utc.strip(), str(item.path).lower())
    return (1, parsed.isoformat(), str(item.path).lower())


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


def filter_history_entries(
    entries: list[WorkflowHistoryEntry],
    *,
    command_name: str | None = None,
    record_type: str | None = None,
    only_successful: bool = False,
    only_failed: bool = False,
    only_apply_requested: bool = False,
    only_preview: bool = False,
    has_reversible_entries: bool = False,
    min_entry_count: int | None = None,
    min_reversible_entry_count: int | None = None,
    created_at_after: str | None = None,
    created_at_before: str | None = None,
) -> list[WorkflowHistoryEntry]:
    filtered = list(entries)

    if command_name:
        normalized = command_name.strip().lower()
        filtered = [item for item in filtered if item.command_name.strip().lower() == normalized]

    if record_type:
        normalized = record_type.strip().lower()
        filtered = [item for item in filtered if item.record_type.strip().lower() == normalized]

    if only_successful and not only_failed:
        filtered = [item for item in filtered if item.successful]
    elif only_failed and not only_successful:
        filtered = [item for item in filtered if not item.successful]

    if only_apply_requested and not only_preview:
        filtered = [item for item in filtered if item.apply_requested]
    elif only_preview and not only_apply_requested:
        filtered = [item for item in filtered if not item.apply_requested]

    if has_reversible_entries:
        filtered = [item for item in filtered if item.has_reversible_entries]

    if min_entry_count is not None:
        filtered = [item for item in filtered if item.entry_count >= min_entry_count]

    if min_reversible_entry_count is not None:
        filtered = [item for item in filtered if item.reversible_entry_count >= min_reversible_entry_count]

    after_dt = _parse_timestamp(created_at_after or "") if created_at_after is not None else None
    if after_dt is not None:
        filtered = [
            item
            for item in filtered
            if (parsed := _parse_timestamp(item.created_at_utc)) is not None and parsed >= after_dt
        ]

    before_dt = _parse_timestamp(created_at_before or "") if created_at_before is not None else None
    if before_dt is not None:
        filtered = [
            item
            for item in filtered
            if (parsed := _parse_timestamp(item.created_at_utc)) is not None and parsed <= before_dt
        ]

    filtered.sort(key=_history_sort_key, reverse=True)
    return filtered


def latest_history_entries_by_command(entries: list[WorkflowHistoryEntry]) -> list[WorkflowHistoryEntry]:
    sorted_entries = filter_history_entries(entries)
    latest_by_command: dict[str, WorkflowHistoryEntry] = {}
    ordered: list[WorkflowHistoryEntry] = []
    for item in sorted_entries:
        normalized = item.command_name.strip().lower()
        if not normalized or normalized in latest_by_command:
            continue
        latest_by_command[normalized] = item
        ordered.append(item)
    return ordered


def summarize_history_entries_by_command(entries: list[WorkflowHistoryEntry]) -> list[WorkflowHistoryCommandSummary]:
    latest_entries = latest_history_entries_by_command(entries)
    grouped: dict[str, list[WorkflowHistoryEntry]] = {}
    for item in entries:
        grouped.setdefault(item.command_name.strip().lower(), []).append(item)

    summaries: list[WorkflowHistoryCommandSummary] = []
    for latest in latest_entries:
        key = latest.command_name.strip().lower()
        command_entries = filter_history_entries(grouped.get(key, []))
        successful_count = sum(1 for item in command_entries if item.successful)
        failed_count = len(command_entries) - successful_count
        apply_requested_count = sum(1 for item in command_entries if item.apply_requested)
        preview_only_count = len(command_entries) - apply_requested_count
        reversible_entry_count = sum(item.reversible_entry_count for item in command_entries)
        entries_with_reversible_count = sum(1 for item in command_entries if item.has_reversible_entries)

        record_type_summary: dict[str, int] = {}
        exit_code_summary: dict[str, int] = {}
        for item in command_entries:
            record_type_summary[item.record_type] = record_type_summary.get(item.record_type, 0) + 1
            exit_key = str(item.exit_code)
            exit_code_summary[exit_key] = exit_code_summary.get(exit_key, 0) + 1

        summaries.append(
            WorkflowHistoryCommandSummary(
                command_name=latest.command_name,
                entry_count=len(command_entries),
                successful_count=successful_count,
                failed_count=failed_count,
                apply_requested_count=apply_requested_count,
                preview_only_count=preview_only_count,
                reversible_entry_count=reversible_entry_count,
                entries_with_reversible_count=entries_with_reversible_count,
                latest_created_at_utc=latest.created_at_utc,
                latest_path=str(latest.path),
                latest_record_type=latest.record_type,
                latest_exit_code=latest.exit_code,
                record_type_summary=dict(sorted(record_type_summary.items())),
                exit_code_summary=dict(sorted(exit_code_summary.items())),
            )
        )
    return summaries


def scan_history_directory(
    root_path: str | Path,
    *,
    command_name: str | None = None,
    record_type: str | None = None,
    only_successful: bool = False,
    only_failed: bool = False,
    only_apply_requested: bool = False,
    only_preview: bool = False,
    has_reversible_entries: bool = False,
    min_entry_count: int | None = None,
    min_reversible_entry_count: int | None = None,
    created_at_after: str | None = None,
    created_at_before: str | None = None,
) -> list[WorkflowHistoryEntry]:
    root = Path(root_path)
    if not root.exists() or not root.is_dir():
        return []

    entries: list[WorkflowHistoryEntry] = []
    for path in sorted(root.rglob("*.json"), key=lambda item: str(item).lower()):
        summary = summarize_history_file(path)
        if summary is not None:
            entries.append(summary)

    return filter_history_entries(
        entries,
        command_name=command_name,
        record_type=record_type,
        only_successful=only_successful,
        only_failed=only_failed,
        only_apply_requested=only_apply_requested,
        only_preview=only_preview,
        has_reversible_entries=has_reversible_entries,
        min_entry_count=min_entry_count,
        min_reversible_entry_count=min_reversible_entry_count,
        created_at_after=created_at_after,
        created_at_before=created_at_before,
    )


def find_latest_history_entry(
    root_path: str | Path,
    *,
    command_name: str | None = None,
    record_type: str | None = None,
    only_successful: bool = False,
    only_failed: bool = False,
    only_apply_requested: bool = False,
    only_preview: bool = False,
    has_reversible_entries: bool = False,
    min_entry_count: int | None = None,
    min_reversible_entry_count: int | None = None,
    created_at_after: str | None = None,
    created_at_before: str | None = None,
) -> WorkflowHistoryEntry | None:
    entries = scan_history_directory(
        root_path,
        command_name=command_name,
        record_type=record_type,
        only_successful=only_successful,
        only_failed=only_failed,
        only_apply_requested=only_apply_requested,
        only_preview=only_preview,
        has_reversible_entries=has_reversible_entries,
        min_entry_count=min_entry_count,
        min_reversible_entry_count=min_reversible_entry_count,
        created_at_after=created_at_after,
        created_at_before=created_at_before,
    )
    return entries[0] if entries else None


def find_latest_history_entries_by_command(
    root_path: str | Path,
    *,
    command_name: str | None = None,
    record_type: str | None = None,
    only_successful: bool = False,
    only_failed: bool = False,
    only_apply_requested: bool = False,
    only_preview: bool = False,
    has_reversible_entries: bool = False,
    min_entry_count: int | None = None,
    min_reversible_entry_count: int | None = None,
    created_at_after: str | None = None,
    created_at_before: str | None = None,
) -> list[WorkflowHistoryEntry]:
    entries = scan_history_directory(
        root_path,
        command_name=command_name,
        record_type=record_type,
        only_successful=only_successful,
        only_failed=only_failed,
        only_apply_requested=only_apply_requested,
        only_preview=only_preview,
        has_reversible_entries=has_reversible_entries,
        min_entry_count=min_entry_count,
        min_reversible_entry_count=min_reversible_entry_count,
        created_at_after=created_at_after,
        created_at_before=created_at_before,
    )
    return latest_history_entries_by_command(entries)


def build_history_summary_by_command(
    root_path: str | Path,
    *,
    command_name: str | None = None,
    record_type: str | None = None,
    only_successful: bool = False,
    only_failed: bool = False,
    only_apply_requested: bool = False,
    only_preview: bool = False,
    has_reversible_entries: bool = False,
    min_entry_count: int | None = None,
    min_reversible_entry_count: int | None = None,
    created_at_after: str | None = None,
    created_at_before: str | None = None,
) -> list[WorkflowHistoryCommandSummary]:
    entries = scan_history_directory(
        root_path,
        command_name=command_name,
        record_type=record_type,
        only_successful=only_successful,
        only_failed=only_failed,
        only_apply_requested=only_apply_requested,
        only_preview=only_preview,
        has_reversible_entries=has_reversible_entries,
        min_entry_count=min_entry_count,
        min_reversible_entry_count=min_reversible_entry_count,
        created_at_after=created_at_after,
        created_at_before=created_at_before,
    )
    return summarize_history_entries_by_command(entries)


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

    return {
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
