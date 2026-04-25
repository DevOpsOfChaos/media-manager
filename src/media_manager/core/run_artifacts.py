from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Iterable

from .action_model import build_action_model_from_report
from .app_manifest import build_ui_state_from_report
from .plan_snapshot import build_plan_snapshot_from_report
from .report_export import write_json_report
from .state import write_execution_journal


def _created_at_utc(created_at_utc: str | None = None) -> str:
    if created_at_utc:
        return created_at_utc
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _timestamp_token(created_at_utc: str) -> str:
    try:
        parsed = datetime.fromisoformat(created_at_utc.replace("Z", "+00:00")).astimezone(timezone.utc)
        return parsed.strftime("%Y%m%dT%H%M%SZ")
    except ValueError:
        sanitized = "".join(ch for ch in created_at_utc if ch.isalnum())
        return sanitized or "run"


def build_run_artifact_paths(
    root_dir: str | Path,
    *,
    command_name: str,
    apply_requested: bool,
    created_at_utc: str | None = None,
) -> dict[str, Path | str]:
    """Return deterministic paths for a single structured run artifact directory."""
    resolved_created_at = _created_at_utc(created_at_utc)
    mode_label = "apply" if apply_requested else "preview"
    run_dir = Path(root_dir) / f"{_timestamp_token(resolved_created_at)}-{command_name}-{mode_label}"
    return {
        "created_at_utc": resolved_created_at,
        "run_dir": run_dir,
        "command_path": run_dir / "command.json",
        "report_path": run_dir / "report.json",
        "review_path": run_dir / "review.json",
        "summary_path": run_dir / "summary.txt",
        "ui_state_path": run_dir / "ui_state.json",
        "plan_snapshot_path": run_dir / "plan_snapshot.json",
        "action_model_path": run_dir / "action_model.json",
        "journal_path": run_dir / "journal.json",
    }


def _compact_outcome(payload: dict[str, Any]) -> dict[str, Any]:
    outcome = payload.get("outcome_report")
    if isinstance(outcome, dict):
        return {
            "status": outcome.get("status"),
            "safe_to_apply": outcome.get("safe_to_apply"),
            "needs_review": outcome.get("needs_review"),
            "next_action": outcome.get("next_action"),
        }
    return {}


def build_run_summary_text(
    *,
    command_name: str,
    apply_requested: bool,
    exit_code: int,
    payload: dict[str, Any],
    created_at_utc: str,
) -> str:
    """Build a small human-readable summary for a run artifact directory."""
    lines = [
        f"Media Manager run summary",
        f"Command: {command_name}",
        f"Mode: {'apply' if apply_requested else 'preview'}",
        f"Created at UTC: {created_at_utc}",
        f"Exit code: {exit_code}",
    ]

    outcome = _compact_outcome(payload)
    if outcome:
        lines.extend(
            [
                "",
                "Outcome",
                f"  Status: {outcome.get('status')}",
                f"  Safe to apply: {outcome.get('safe_to_apply')}",
                f"  Needs review: {outcome.get('needs_review')}",
                f"  Next action: {outcome.get('next_action')}",
            ]
        )

    review = payload.get("review")
    if isinstance(review, dict):
        lines.extend(
            [
                "",
                "Review",
                f"  Candidates: {review.get('candidate_count', 0)}",
                f"  Reasons: {review.get('reason_summary', {})}",
            ]
        )

    for section_name in ("scan", "summary", "duplicates", "organize", "rename", "execution"):
        section = payload.get(section_name)
        if not isinstance(section, dict):
            continue
        interesting = {
            key: value
            for key, value in section.items()
            if key.endswith("_count") or key in {"exact_groups", "duplicate_files", "errors", "planned_count", "error_count", "conflict_count", "skipped_count"}
            if isinstance(value, (int, str, bool))
        }
        if not interesting:
            continue
        lines.append("")
        lines.append(section_name.capitalize())
        for key, value in sorted(interesting.items()):
            lines.append(f"  {key}: {value}")

    lines.append("")
    return "\n".join(lines)


def write_run_artifacts(
    root_dir: str | Path,
    *,
    command_name: str,
    argv: Iterable[str],
    apply_requested: bool,
    exit_code: int,
    payload: dict[str, Any],
    review_payload: dict[str, Any] | None = None,
    journal_entries: list[dict[str, Any]] | None = None,
    created_at_utc: str | None = None,
) -> dict[str, Path | str]:
    """Write command/report/review/summary artifacts for one command run."""
    paths = build_run_artifact_paths(
        root_dir,
        command_name=command_name,
        apply_requested=apply_requested,
        created_at_utc=created_at_utc,
    )
    run_dir = Path(paths["run_dir"])
    run_dir.mkdir(parents=True, exist_ok=True)
    resolved_created_at = str(paths["created_at_utc"])

    command_payload = {
        "command": command_name,
        "argv": list(argv),
        "apply_requested": apply_requested,
        "exit_code": exit_code,
        "created_at_utc": resolved_created_at,
    }
    write_json_report(paths["command_path"], command_payload)
    write_json_report(paths["report_path"], payload)
    write_json_report(
        paths["ui_state_path"],
        build_ui_state_from_report(
            command_name=command_name,
            report_payload=payload,
            command_payload=command_payload,
            run_id=run_dir.name,
        ),
    )
    write_json_report(
        paths["plan_snapshot_path"],
        build_plan_snapshot_from_report(
            command_name=command_name,
            report_payload=payload,
            run_id=run_dir.name,
        ),
    )
    write_json_report(
        paths["action_model_path"],
        build_action_model_from_report(
            command_name=command_name,
            report_payload=payload,
            command_payload=command_payload,
            run_id=run_dir.name,
        ),
    )
    if review_payload is not None:
        write_json_report(paths["review_path"], review_payload)
    else:
        Path(paths["review_path"]).write_text("{}\n", encoding="utf-8")

    Path(paths["summary_path"]).write_text(
        build_run_summary_text(
            command_name=command_name,
            apply_requested=apply_requested,
            exit_code=exit_code,
            payload=payload,
            created_at_utc=resolved_created_at,
        ),
        encoding="utf-8",
    )

    if journal_entries is not None:
        write_execution_journal(
            paths["journal_path"],
            command_name=command_name,
            apply_requested=apply_requested,
            exit_code=exit_code,
            entries=journal_entries,
            created_at_utc=resolved_created_at,
        )
    else:
        paths.pop("journal_path", None)

    return paths


__all__ = ["build_run_artifact_paths", "build_run_summary_text", "write_run_artifacts"]
