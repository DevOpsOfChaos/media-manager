from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from media_manager.cleanup_plan import build_exact_group_id
from media_manager.duplicate_session_store import build_duplicate_group_signature
from media_manager.duplicates import ExactDuplicateGroup


@dataclass(slots=True)
class DuplicateDecisionImportResult:
    status: str
    reason: str
    decisions: dict[str, str] = field(default_factory=dict)
    file_group_count: int = 0
    file_decision_count: int = 0
    matched_decision_count: int = 0
    ignored_decision_count: int = 0
    missing_group_count: int = 0
    invalid_keep_count: int = 0
    signature_matched: bool = False

    @property
    def ok(self) -> bool:
        return self.status in {"matched", "partial", "empty"}


def _path_strings(paths: Iterable[Path]) -> list[str]:
    return [str(path) for path in paths]


def _group_lookup(exact_groups: list[ExactDuplicateGroup]) -> dict[str, ExactDuplicateGroup]:
    return {build_exact_group_id(group): group for group in exact_groups}


def _candidate_set(group: ExactDuplicateGroup) -> set[str]:
    return {str(path) for path in group.files}


def build_duplicate_decision_template(
    *,
    exact_groups: list[ExactDuplicateGroup],
    decisions: dict[str, str] | None = None,
    decision_origins: dict[str, str] | None = None,
    mode: str = "copy",
    policy: str | None = None,
    include_patterns: tuple[str, ...] = (),
    exclude_patterns: tuple[str, ...] = (),
    media_kinds: tuple[str, ...] = (),
    media_extensions: frozenset[str] | None = None,
) -> dict[str, object]:
    """Build an editable duplicate decision file.

    The file is intentionally redundant: it contains a compact ``decisions`` map for
    machines and a ``groups`` list for humans. Users can either edit the map or set
    ``selected_keep_path`` on individual groups. Import validates every keep path
    against the current scan before it is used.
    """
    decisions = dict(decisions or {})
    decision_origins = dict(decision_origins or {})
    groups: list[dict[str, object]] = []
    normalized_decisions: dict[str, str] = {}

    for group in exact_groups:
        group_id = build_exact_group_id(group)
        candidate_paths = _path_strings(group.files)
        selected_keep_path = decisions.get(group_id)
        if selected_keep_path in set(candidate_paths):
            normalized_decisions[group_id] = selected_keep_path
        else:
            selected_keep_path = None

        groups.append(
            {
                "group_id": group_id,
                "file_size": int(group.file_size),
                "candidate_count": len(group.files),
                "selected_keep_path": selected_keep_path,
                "suggested_keep_path": selected_keep_path,
                "suggestion_origin": None if selected_keep_path is None else decision_origins.get(group_id, "provided"),
                "status": "decided" if selected_keep_path is not None else "unresolved",
                "same_name": bool(group.same_name),
                "same_suffix": bool(group.same_suffix),
                "extension_summary": dict(sorted(getattr(group, "extension_summary", {}).items())),
                "media_kind_summary": dict(sorted(getattr(group, "media_kind_summary", {}).items())),
                "candidate_paths": candidate_paths,
            }
        )

    return {
        "schema_version": 1,
        "type": "duplicate_decisions",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "policy": policy,
        "include_patterns": list(include_patterns),
        "exclude_patterns": list(exclude_patterns),
        "media_kinds": list(media_kinds),
        "media_extensions": None if media_extensions is None else sorted(media_extensions),
        "instructions": [
            "Review each group and set selected_keep_path to the file that should be kept.",
            "selected_keep_path must exactly match one of the candidate_paths for that group.",
            "The import step validates every decision against the current duplicate scan before planning apply actions.",
            "Leaving selected_keep_path empty keeps the group unresolved and blocks destructive duplicate cleanup for that group.",
        ],
        "group_signature": build_duplicate_group_signature(exact_groups),
        "exact_group_count": len(exact_groups),
        "decision_count": len(normalized_decisions),
        "unresolved_group_count": max(0, len(exact_groups) - len(normalized_decisions)),
        "decisions": normalized_decisions,
        "groups": groups,
    }


def write_duplicate_decision_template(file_path: str | Path, payload: dict[str, object]) -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _decisions_from_payload(payload: dict[str, object]) -> dict[str, str]:
    decisions: dict[str, str] = {}

    raw_decisions = payload.get("decisions", {})
    if isinstance(raw_decisions, dict):
        for group_id, keep_path in raw_decisions.items():
            text = str(keep_path).strip()
            if text:
                decisions[str(group_id)] = text

    raw_groups = payload.get("groups", [])
    if isinstance(raw_groups, list):
        for item in raw_groups:
            if not isinstance(item, dict):
                continue
            group_id = item.get("group_id")
            keep_path = item.get("selected_keep_path")
            if group_id is None or keep_path is None:
                continue
            text = str(keep_path).strip()
            if text:
                decisions[str(group_id)] = text

    return decisions


def load_duplicate_decision_file(
    file_path: str | Path,
    exact_groups: list[ExactDuplicateGroup],
) -> DuplicateDecisionImportResult:
    path = Path(file_path)
    if not path.exists():
        return DuplicateDecisionImportResult(
            status="missing",
            reason="duplicate decision file does not exist",
        )

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return DuplicateDecisionImportResult(
            status="error",
            reason=f"failed to load duplicate decision file: {exc}",
        )

    if not isinstance(payload, dict):
        return DuplicateDecisionImportResult(
            status="error",
            reason="duplicate decision file must contain a JSON object",
        )

    group_by_id = _group_lookup(exact_groups)
    raw_decisions = _decisions_from_payload(payload)
    normalized: dict[str, str] = {}
    missing_group_count = 0
    invalid_keep_count = 0

    for group_id, keep_path in raw_decisions.items():
        group = group_by_id.get(group_id)
        if group is None:
            missing_group_count += 1
            continue
        if keep_path not in _candidate_set(group):
            invalid_keep_count += 1
            continue
        normalized[group_id] = keep_path

    file_group_count = int(payload.get("exact_group_count", len(payload.get("groups", []) or [])) or 0)
    file_decision_count = len(raw_decisions)
    ignored_count = max(0, file_decision_count - len(normalized))
    current_signature = build_duplicate_group_signature(exact_groups)
    file_signature = str(payload.get("group_signature", ""))
    signature_matched = bool(file_signature) and file_signature == current_signature

    if not raw_decisions:
        status = "empty"
        reason = "duplicate decision file did not contain any selected keep decisions"
    elif normalized and ignored_count == 0 and (signature_matched or not file_signature):
        status = "matched"
        reason = "duplicate decision file matched the current exact duplicate groups"
    elif normalized:
        status = "partial"
        reason = "duplicate decision file partially matched the current exact duplicate groups"
    else:
        status = "mismatch"
        reason = "duplicate decision file did not contain usable decisions for the current exact duplicate groups"

    return DuplicateDecisionImportResult(
        status=status,
        reason=reason,
        decisions=normalized,
        file_group_count=file_group_count,
        file_decision_count=file_decision_count,
        matched_decision_count=len(normalized),
        ignored_decision_count=ignored_count,
        missing_group_count=missing_group_count,
        invalid_keep_count=invalid_keep_count,
        signature_matched=signature_matched,
    )


def duplicate_decision_import_payload(result: DuplicateDecisionImportResult | None) -> dict[str, object] | None:
    if result is None:
        return None
    return {
        "status": result.status,
        "reason": result.reason,
        "file_group_count": result.file_group_count,
        "file_decision_count": result.file_decision_count,
        "matched_decision_count": result.matched_decision_count,
        "ignored_decision_count": result.ignored_decision_count,
        "missing_group_count": result.missing_group_count,
        "invalid_keep_count": result.invalid_keep_count,
        "signature_matched": result.signature_matched,
    }


__all__ = [
    "DuplicateDecisionImportResult",
    "build_duplicate_decision_template",
    "duplicate_decision_import_payload",
    "load_duplicate_decision_file",
    "write_duplicate_decision_template",
]
