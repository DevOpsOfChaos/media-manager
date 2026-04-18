from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .cleanup_plan import build_exact_group_id
from .duplicates import ExactDuplicateGroup


@dataclass(slots=True)
class DuplicateSessionSnapshot:
    schema_version: int = 1
    created_at_utc: str = ""
    group_signature: str = ""
    exact_group_count: int = 0
    decision_count: int = 0
    decisions: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class DuplicateSessionRestoreResult:
    status: str
    reason: str
    decisions: dict[str, str] = field(default_factory=dict)
    snapshot: DuplicateSessionSnapshot | None = None


def build_duplicate_group_signature(exact_groups: list[ExactDuplicateGroup]) -> str:
    if not exact_groups:
        return "empty"

    parts: list[str] = []
    for group in exact_groups:
        group_id = build_exact_group_id(group)
        candidates = "|".join(str(path) for path in group.files)
        parts.append(f"{group_id}:{candidates}")
    return "\n".join(parts)


def normalize_duplicate_decisions(
    exact_groups: list[ExactDuplicateGroup],
    decisions: dict[str, str],
) -> dict[str, str]:
    normalized: dict[str, str] = {}

    valid_candidates: dict[str, set[str]] = {}
    for group in exact_groups:
        group_id = build_exact_group_id(group)
        valid_candidates[group_id] = {str(path) for path in group.files}

    for group_id, keep_path in decisions.items():
        if group_id not in valid_candidates:
            continue
        if keep_path not in valid_candidates[group_id]:
            continue
        normalized[group_id] = keep_path

    return normalized


def save_duplicate_session_snapshot(
    file_path: str | Path,
    exact_groups: list[ExactDuplicateGroup],
    decisions: dict[str, str],
) -> DuplicateSessionSnapshot:
    normalized_decisions = normalize_duplicate_decisions(exact_groups, decisions)
    snapshot = DuplicateSessionSnapshot(
        schema_version=1,
        created_at_utc=datetime.now(timezone.utc).isoformat(),
        group_signature=build_duplicate_group_signature(exact_groups),
        exact_group_count=len(exact_groups),
        decision_count=len(normalized_decisions),
        decisions=normalized_decisions,
    )

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": snapshot.schema_version,
                "created_at_utc": snapshot.created_at_utc,
                "group_signature": snapshot.group_signature,
                "exact_group_count": snapshot.exact_group_count,
                "decision_count": snapshot.decision_count,
                "decisions": snapshot.decisions,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return snapshot


def load_duplicate_session_snapshot(file_path: str | Path) -> DuplicateSessionSnapshot:
    path = Path(file_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    decisions = {str(key): str(value) for key, value in dict(payload.get("decisions", {})).items()}
    return DuplicateSessionSnapshot(
        schema_version=int(payload.get("schema_version", 1)),
        created_at_utc=str(payload.get("created_at_utc", "")),
        group_signature=str(payload.get("group_signature", "")),
        exact_group_count=int(payload.get("exact_group_count", 0)),
        decision_count=int(payload.get("decision_count", len(decisions))),
        decisions=decisions,
    )


def restore_duplicate_session(
    file_path: str | Path,
    exact_groups: list[ExactDuplicateGroup],
) -> DuplicateSessionRestoreResult:
    path = Path(file_path)
    if not path.exists():
        return DuplicateSessionRestoreResult(
            status="missing",
            reason="session snapshot file does not exist",
            decisions={},
            snapshot=None,
        )

    try:
        snapshot = load_duplicate_session_snapshot(path)
    except Exception as exc:
        return DuplicateSessionRestoreResult(
            status="error",
            reason=f"failed to load duplicate session snapshot: {exc}",
            decisions={},
            snapshot=None,
        )

    current_signature = build_duplicate_group_signature(exact_groups)
    if snapshot.group_signature != current_signature:
        return DuplicateSessionRestoreResult(
            status="mismatch",
            reason="saved duplicate session does not match the current exact duplicate groups",
            decisions={},
            snapshot=snapshot,
        )

    normalized = normalize_duplicate_decisions(exact_groups, snapshot.decisions)
    return DuplicateSessionRestoreResult(
        status="matched",
        reason="saved duplicate session matched the current exact duplicate groups",
        decisions=normalized,
        snapshot=snapshot,
    )


def restore_duplicate_decisions(
    file_path: str | Path,
    exact_groups: list[ExactDuplicateGroup],
) -> dict[str, str]:
    return restore_duplicate_session(file_path, exact_groups).decisions
