from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .cleanup_plan import build_exact_group_id
from .duplicates import ExactDuplicateGroup


@dataclass(slots=True)
class DuplicateSessionSnapshot:
    group_signature: str
    decisions: dict[str, str]



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
    snapshot = DuplicateSessionSnapshot(
        group_signature=build_duplicate_group_signature(exact_groups),
        decisions=normalize_duplicate_decisions(exact_groups, decisions),
    )

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "group_signature": snapshot.group_signature,
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
    return DuplicateSessionSnapshot(
        group_signature=str(payload.get("group_signature", "")),
        decisions={str(key): str(value) for key, value in dict(payload.get("decisions", {})).items()},
    )



def restore_duplicate_decisions(
    file_path: str | Path,
    exact_groups: list[ExactDuplicateGroup],
) -> dict[str, str]:
    path = Path(file_path)
    if not path.exists():
        return {}

    snapshot = load_duplicate_session_snapshot(path)
    current_signature = build_duplicate_group_signature(exact_groups)
    if snapshot.group_signature != current_signature:
        return {}

    return normalize_duplicate_decisions(exact_groups, snapshot.decisions)
