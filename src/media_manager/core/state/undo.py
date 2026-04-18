from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from .execution_journal import load_execution_journal


@dataclass(slots=True)
class UndoEntryResult:
    undo_action: str | None
    source_path: Path | None
    target_path: Path | None
    status: str
    reason: str


@dataclass(slots=True)
class UndoExecutionResult:
    apply_requested: bool
    journal_path: Path
    journal_command_name: str
    original_apply_requested: bool
    original_exit_code: int
    entry_count: int = 0
    reversible_entry_count: int = 0
    planned_count: int = 0
    undone_count: int = 0
    skipped_count: int = 0
    error_count: int = 0
    entries: list[UndoEntryResult] = field(default_factory=list)

    @property
    def ready_to_apply_count(self) -> int:
        return sum(1 for item in self.entries if item.status == "planned")

    @property
    def status_summary(self) -> dict[str, int]:
        summary: dict[str, int] = {}
        for item in self.entries:
            summary[item.status] = summary.get(item.status, 0) + 1
        return dict(sorted(summary.items()))

    @property
    def undo_action_summary(self) -> dict[str, int]:
        summary: dict[str, int] = {}
        for item in self.entries:
            key = item.undo_action or "none"
            summary[key] = summary.get(key, 0) + 1
        return dict(sorted(summary.items()))

    @property
    def reason_summary(self) -> dict[str, int]:
        summary: dict[str, int] = {}
        for item in self.entries:
            summary[item.reason] = summary.get(item.reason, 0) + 1
        return dict(sorted(summary.items()))


def _path_or_none(value: object) -> Path | None:
    if value is None:
        return None
    text = str(value).strip()
    return Path(text) if text else None


def execute_undo_journal(file_path: str | Path, *, apply: bool) -> UndoExecutionResult:
    journal_path = Path(file_path)
    payload = load_execution_journal(journal_path)
    result = UndoExecutionResult(
        apply_requested=apply,
        journal_path=journal_path,
        journal_command_name=str(payload.get("command_name", "unknown")),
        original_apply_requested=bool(payload.get("apply_requested", False)),
        original_exit_code=int(payload.get("exit_code", 0)),
    )

    for raw_entry in payload.get("entries", []):
        if not isinstance(raw_entry, dict):
            result.error_count += 1
            result.entries.append(
                UndoEntryResult(
                    undo_action=None,
                    source_path=None,
                    target_path=None,
                    status="error",
                    reason="journal entry is not a JSON object",
                )
            )
            continue

        result.entry_count += 1
        reversible = bool(raw_entry.get("reversible"))
        undo_action = str(raw_entry.get("undo_action")) if raw_entry.get("undo_action") is not None else None
        undo_from_path = _path_or_none(raw_entry.get("undo_from_path"))
        undo_to_path = _path_or_none(raw_entry.get("undo_to_path"))

        if not reversible or not undo_action:
            result.skipped_count += 1
            result.entries.append(
                UndoEntryResult(
                    undo_action=undo_action,
                    source_path=undo_from_path,
                    target_path=undo_to_path,
                    status="skipped",
                    reason="journal entry is not reversible",
                )
            )
            continue

        result.reversible_entry_count += 1

        if undo_action == "delete_target":
            if undo_from_path is None:
                result.error_count += 1
                result.entries.append(
                    UndoEntryResult(
                        undo_action=undo_action,
                        source_path=None,
                        target_path=None,
                        status="error",
                        reason="reversible journal entry is missing undo_from_path",
                    )
                )
                continue

            if not apply:
                result.planned_count += 1
                result.entries.append(
                    UndoEntryResult(
                        undo_action=undo_action,
                        source_path=undo_from_path,
                        target_path=None,
                        status="planned",
                        reason="would delete the journal target path",
                    )
                )
                continue

            if not undo_from_path.exists():
                result.skipped_count += 1
                result.entries.append(
                    UndoEntryResult(
                        undo_action=undo_action,
                        source_path=undo_from_path,
                        target_path=None,
                        status="skipped",
                        reason="undo source path no longer exists",
                    )
                )
                continue

            try:
                undo_from_path.unlink()
            except Exception as exc:  # pragma: no cover
                result.error_count += 1
                result.entries.append(
                    UndoEntryResult(
                        undo_action=undo_action,
                        source_path=undo_from_path,
                        target_path=None,
                        status="error",
                        reason=str(exc),
                    )
                )
                continue

            result.undone_count += 1
            result.entries.append(
                UndoEntryResult(
                    undo_action=undo_action,
                    source_path=undo_from_path,
                    target_path=None,
                    status="undone",
                    reason="deleted the journal target path",
                )
            )
            continue

        if undo_action in {"move_back", "rename_back"}:
            if undo_from_path is None or undo_to_path is None:
                result.error_count += 1
                result.entries.append(
                    UndoEntryResult(
                        undo_action=undo_action,
                        source_path=undo_from_path,
                        target_path=undo_to_path,
                        status="error",
                        reason="reversible journal entry is missing undo paths",
                    )
                )
                continue

            if not apply:
                result.planned_count += 1
                result.entries.append(
                    UndoEntryResult(
                        undo_action=undo_action,
                        source_path=undo_from_path,
                        target_path=undo_to_path,
                        status="planned",
                        reason="would restore the original source path from the journal",
                    )
                )
                continue

            if not undo_from_path.exists():
                result.skipped_count += 1
                result.entries.append(
                    UndoEntryResult(
                        undo_action=undo_action,
                        source_path=undo_from_path,
                        target_path=undo_to_path,
                        status="skipped",
                        reason="undo source path no longer exists",
                    )
                )
                continue

            if undo_to_path.exists():
                result.error_count += 1
                result.entries.append(
                    UndoEntryResult(
                        undo_action=undo_action,
                        source_path=undo_from_path,
                        target_path=undo_to_path,
                        status="error",
                        reason="undo target path already exists",
                    )
                )
                continue

            try:
                undo_to_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(undo_from_path), str(undo_to_path))
            except Exception as exc:  # pragma: no cover
                result.error_count += 1
                result.entries.append(
                    UndoEntryResult(
                        undo_action=undo_action,
                        source_path=undo_from_path,
                        target_path=undo_to_path,
                        status="error",
                        reason=str(exc),
                    )
                )
                continue

            result.undone_count += 1
            result.entries.append(
                UndoEntryResult(
                    undo_action=undo_action,
                    source_path=undo_from_path,
                    target_path=undo_to_path,
                    status="undone",
                    reason="restored the original source path from the journal",
                )
            )
            continue

        result.error_count += 1
        result.entries.append(
            UndoEntryResult(
                undo_action=undo_action,
                source_path=undo_from_path,
                target_path=undo_to_path,
                status="error",
                reason=f"unsupported undo action: {undo_action}",
            )
        )

    return result
