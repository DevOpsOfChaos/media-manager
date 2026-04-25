from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Iterable


RUN_ARTIFACT_FILENAMES = ("command.json", "report.json", "review.json", "summary.txt")
OPTIONAL_RUN_ARTIFACT_FILENAMES = ("ui_state.json", "plan_snapshot.json", "action_model.json", "journal.json")


@dataclass(slots=True, frozen=True)
class RunArtifactRecord:
    run_dir: Path
    command: str | None
    mode: str | None
    created_at_utc: str | None
    exit_code: int | None
    status: str | None
    next_action: str | None
    review_candidate_count: int
    has_ui_state: bool
    has_plan_snapshot: bool
    has_action_model: bool
    action_count: int
    recommended_action_count: int
    has_journal: bool
    missing_files: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    @property
    def valid(self) -> bool:
        return not self.missing_files and not self.errors


@dataclass(slots=True, frozen=True)
class RunArtifactValidation:
    root_dir: Path
    records: tuple[RunArtifactRecord, ...]
    errors: tuple[str, ...] = ()

    @property
    def run_count(self) -> int:
        return len(self.records)

    @property
    def valid_count(self) -> int:
        return sum(1 for item in self.records if item.valid)

    @property
    def invalid_count(self) -> int:
        return sum(1 for item in self.records if not item.valid)

    @property
    def ready(self) -> bool:
        return not self.errors and self.invalid_count == 0


def _read_json(path: Path) -> tuple[dict[str, Any], str | None]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}, f"missing file: {path.name}"
    except json.JSONDecodeError as exc:
        return {}, f"invalid JSON in {path.name}: {exc}"
    except OSError as exc:
        return {}, f"could not read {path.name}: {exc}"
    if not isinstance(value, dict):
        return {}, f"expected JSON object in {path.name}"
    return value, None


def _first_existing_dict(*values: Any) -> dict[str, Any]:
    for value in values:
        if isinstance(value, dict):
            return value
    return {}


def _as_int(value: Any) -> int:
    return value if isinstance(value, int) else 0


def _extract_record(run_dir: Path) -> RunArtifactRecord:
    missing_files = [name for name in RUN_ARTIFACT_FILENAMES if not (run_dir / name).is_file()]
    errors: list[str] = []

    command_payload: dict[str, Any] = {}
    report_payload: dict[str, Any] = {}
    review_payload: dict[str, Any] = {}
    action_payload: dict[str, Any] = {}

    if "command.json" not in missing_files:
        command_payload, error = _read_json(run_dir / "command.json")
        if error:
            errors.append(error)
    if "report.json" not in missing_files:
        report_payload, error = _read_json(run_dir / "report.json")
        if error:
            errors.append(error)
    if "review.json" not in missing_files:
        review_payload, error = _read_json(run_dir / "review.json")
        if error:
            errors.append(error)
    if (run_dir / "action_model.json").is_file():
        action_payload, error = _read_json(run_dir / "action_model.json")
        if error:
            errors.append(error)

    outcome = _first_existing_dict(report_payload.get("outcome_report"), review_payload.get("outcome_report"))
    review = _first_existing_dict(review_payload.get("review"), report_payload.get("review"))

    command = command_payload.get("command")
    apply_requested = command_payload.get("apply_requested")
    mode = None
    if isinstance(apply_requested, bool):
        mode = "apply" if apply_requested else "preview"

    candidate_count = review.get("candidate_count", 0)
    if not isinstance(candidate_count, int):
        candidate_count = 0

    exit_code = command_payload.get("exit_code")
    if not isinstance(exit_code, int):
        exit_code = None

    return RunArtifactRecord(
        run_dir=run_dir,
        command=str(command) if command is not None else None,
        mode=mode,
        created_at_utc=str(command_payload.get("created_at_utc")) if command_payload.get("created_at_utc") is not None else None,
        exit_code=exit_code,
        status=str(outcome.get("status")) if outcome.get("status") is not None else None,
        next_action=str(outcome.get("next_action")) if outcome.get("next_action") is not None else None,
        review_candidate_count=candidate_count,
        has_ui_state=(run_dir / "ui_state.json").is_file(),
        has_plan_snapshot=(run_dir / "plan_snapshot.json").is_file(),
        has_action_model=(run_dir / "action_model.json").is_file(),
        action_count=_as_int(action_payload.get("action_count")),
        recommended_action_count=_as_int(action_payload.get("recommended_action_count")),
        has_journal=(run_dir / "journal.json").is_file(),
        missing_files=tuple(missing_files),
        errors=tuple(errors),
    )


def discover_run_artifact_dirs(root_dir: str | Path) -> list[Path]:
    root = Path(root_dir)
    if not root.exists() or not root.is_dir():
        return []
    run_dirs = [path for path in root.iterdir() if path.is_dir() and (path / "command.json").exists()]
    run_dirs.sort(key=lambda item: item.name, reverse=True)
    return run_dirs


def list_run_artifacts(root_dir: str | Path, *, limit: int | None = None) -> list[RunArtifactRecord]:
    run_dirs = discover_run_artifact_dirs(root_dir)
    if limit is not None:
        run_dirs = run_dirs[: max(0, limit)]
    return [_extract_record(path) for path in run_dirs]


def validate_run_artifacts(root_dir: str | Path, *, limit: int | None = None) -> RunArtifactValidation:
    root = Path(root_dir)
    errors: list[str] = []
    if not root.exists():
        errors.append("run root does not exist")
        return RunArtifactValidation(root_dir=root, records=(), errors=tuple(errors))
    if not root.is_dir():
        errors.append("run root is not a directory")
        return RunArtifactValidation(root_dir=root, records=(), errors=tuple(errors))
    return RunArtifactValidation(root_dir=root, records=tuple(list_run_artifacts(root, limit=limit)))


def find_run_artifact(root_dir: str | Path, run_id: str) -> RunArtifactRecord | None:
    root = Path(root_dir)
    candidate = root / run_id
    if candidate.is_dir():
        return _extract_record(candidate)
    matches = [path for path in discover_run_artifact_dirs(root) if path.name.startswith(run_id)]
    if len(matches) == 1:
        return _extract_record(matches[0])
    return None


def load_run_artifact_payload(run_dir: str | Path, artifact_name: str) -> dict[str, Any] | str:
    path = Path(run_dir) / artifact_name
    if artifact_name == "summary.txt":
        return path.read_text(encoding="utf-8")
    payload, error = _read_json(path)
    if error:
        raise ValueError(error)
    return payload


def build_run_artifacts_payload(records: Iterable[RunArtifactRecord], *, root_dir: str | Path) -> dict[str, Any]:
    rows = []
    for item in records:
        rows.append(
            {
                "run_id": item.run_dir.name,
                "run_dir": str(item.run_dir),
                "command": item.command,
                "mode": item.mode,
                "created_at_utc": item.created_at_utc,
                "exit_code": item.exit_code,
                "status": item.status,
                "next_action": item.next_action,
                "review_candidate_count": item.review_candidate_count,
                "has_ui_state": item.has_ui_state,
                "has_plan_snapshot": item.has_plan_snapshot,
                "has_action_model": item.has_action_model,
                "action_count": item.action_count,
                "recommended_action_count": item.recommended_action_count,
                "has_journal": item.has_journal,
                "valid": item.valid,
                "missing_files": list(item.missing_files),
                "errors": list(item.errors),
            }
        )
    return {
        "root_dir": str(Path(root_dir)),
        "run_count": len(rows),
        "valid_count": sum(1 for row in rows if row["valid"]),
        "invalid_count": sum(1 for row in rows if not row["valid"]),
        "runs": rows,
    }


__all__ = [
    "RUN_ARTIFACT_FILENAMES",
    "OPTIONAL_RUN_ARTIFACT_FILENAMES",
    "RunArtifactRecord",
    "RunArtifactValidation",
    "build_run_artifacts_payload",
    "discover_run_artifact_dirs",
    "find_run_artifact",
    "list_run_artifacts",
    "load_run_artifact_payload",
    "validate_run_artifacts",
]
