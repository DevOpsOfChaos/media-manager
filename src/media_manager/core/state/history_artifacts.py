from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .execution_journal import write_execution_journal
from .run_log import write_command_run_log


def _coerce_created_at_utc(created_at_utc: str | None) -> str:
    if created_at_utc:
        return created_at_utc
    return datetime.now(timezone.utc).isoformat()


def _timestamp_token(created_at_utc: str) -> str:
    try:
        parsed = datetime.fromisoformat(created_at_utc.replace("Z", "+00:00")).astimezone(timezone.utc)
        return parsed.strftime("%Y%m%dT%H%M%SZ")
    except ValueError:
        sanitized = "".join(ch for ch in created_at_utc if ch.isalnum())
        return sanitized or "history"


def build_history_artifact_paths(
    history_dir: str | Path,
    *,
    command_name: str,
    apply_requested: bool,
    created_at_utc: str | None = None,
    include_execution_journal: bool = False,
) -> dict[str, object]:
    resolved_created_at_utc = _coerce_created_at_utc(created_at_utc)
    mode_label = "apply" if apply_requested else "preview"
    token = _timestamp_token(resolved_created_at_utc)
    base_name = f"{token}-{command_name}-{mode_label}"

    root = Path(history_dir)
    payload: dict[str, object] = {
        "created_at_utc": resolved_created_at_utc,
        "run_log_path": root / f"{base_name}-run-log.json",
    }
    if include_execution_journal:
        payload["execution_journal_path"] = root / f"{base_name}-execution-journal.json"
    return payload


def write_history_artifacts(
    history_dir: str | Path,
    *,
    command_name: str,
    apply_requested: bool,
    exit_code: int,
    payload: dict[str, object],
    journal_entries: list[dict[str, object]] | None = None,
    created_at_utc: str | None = None,
) -> dict[str, object]:
    include_execution_journal = journal_entries is not None
    paths = build_history_artifact_paths(
        history_dir,
        command_name=command_name,
        apply_requested=apply_requested,
        created_at_utc=created_at_utc,
        include_execution_journal=include_execution_journal,
    )
    resolved_created_at_utc = str(paths["created_at_utc"])

    run_log_path = write_command_run_log(
        paths["run_log_path"],
        command_name=command_name,
        apply_requested=apply_requested,
        exit_code=exit_code,
        payload=payload,
        created_at_utc=resolved_created_at_utc,
    )

    result: dict[str, object] = {
        "created_at_utc": resolved_created_at_utc,
        "run_log_path": run_log_path,
    }

    if include_execution_journal:
        journal_path = write_execution_journal(
            paths["execution_journal_path"],
            command_name=command_name,
            apply_requested=apply_requested,
            exit_code=exit_code,
            entries=journal_entries or [],
            created_at_utc=resolved_created_at_utc,
        )
        result["execution_journal_path"] = journal_path

    return result
