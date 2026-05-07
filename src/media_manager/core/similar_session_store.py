from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from media_manager.similar_images import SimilarImageGroup

from .similar_assets import build_similar_group_id
from .similar_decisions import build_similar_group_signature


@dataclass(slots=True)
class SimilarSessionSnapshot:
    status: str
    reason: str
    decisions: dict[str, dict[str, str]] = field(default_factory=dict)
    group_count: int = 0
    decision_count: int = 0
    signature_matched: bool = False


def _member_path_set(group: SimilarImageGroup) -> set[str]:
    return {str(member.path) for member in group.members}


def normalize_similar_decisions(
    groups: list[SimilarImageGroup],
    decisions: dict[str, dict[str, str]],
) -> dict[str, dict[str, str]]:
    group_by_id = {build_similar_group_id(g): g for g in groups}
    normalized: dict[str, dict[str, str]] = {}
    for group_id, group_decisions in decisions.items():
        group = group_by_id.get(group_id)
        if group is None:
            continue
        valid: dict[str, str] = {}
        paths = _member_path_set(group)
        for member_path, decision in group_decisions.items():
            if member_path in paths:
                valid[member_path] = decision
        if valid:
            normalized[group_id] = valid
    return normalized


def save_similar_session_snapshot(
    file_path: str | Path,
    groups: list[SimilarImageGroup],
    decisions: dict[str, dict[str, str]],
) -> Path:
    path = Path(file_path)
    normalized = normalize_similar_decisions(groups, decisions)
    payload = {
        "schema_version": 1,
        "type": "similar_session_snapshot",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "group_signature": build_similar_group_signature(groups),
        "group_count": len(groups),
        "decision_count": sum(len(d) for d in normalized.values()),
        "decisions": normalized,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def restore_similar_session(
    file_path: str | Path,
    groups: list[SimilarImageGroup],
) -> SimilarSessionSnapshot:
    path = Path(file_path)
    if not path.exists():
        return SimilarSessionSnapshot(status="missing", reason="session file does not exist")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return SimilarSessionSnapshot(status="error", reason=f"failed to load session file: {exc}")

    if not isinstance(payload, dict):
        return SimilarSessionSnapshot(status="error", reason="session file must contain a JSON object")

    current_signature = build_similar_group_signature(groups)
    file_signature = str(payload.get("group_signature", ""))
    signature_matched = bool(file_signature) and file_signature == current_signature

    raw_decisions = payload.get("decisions", {})
    if not isinstance(raw_decisions, dict) or not raw_decisions:
        return SimilarSessionSnapshot(
            status="empty",
            reason="session file contains no decisions",
            signature_matched=signature_matched,
        )

    normalized = normalize_similar_decisions(groups, raw_decisions)
    if not signature_matched:
        return SimilarSessionSnapshot(
            status="mismatch",
            reason="group signatures do not match",
            decisions=normalized,
            group_count=int(payload.get("group_count", len(groups))),
            decision_count=sum(len(d) for d in normalized.values()),
            signature_matched=False,
        )

    return SimilarSessionSnapshot(
        status="matched",
        reason="session matched the current similar image groups",
        decisions=normalized,
        group_count=int(payload.get("group_count", len(groups))),
        decision_count=sum(len(d) for d in normalized.values()),
        signature_matched=True,
    )


__all__ = [
    "SimilarSessionSnapshot",
    "normalize_similar_decisions",
    "restore_similar_session",
    "save_similar_session_snapshot",
]
