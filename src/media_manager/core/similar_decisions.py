from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from media_manager.similar_images import SimilarImageGroup

from .similar_assets import build_similar_group_id


@dataclass(slots=True)
class SimilarDecisionImportResult:
    status: str
    reason: str
    decisions: dict[str, dict[str, str]] = field(default_factory=dict)
    file_group_count: int = 0
    file_decision_count: int = 0
    matched_decision_count: int = 0
    ignored_decision_count: int = 0
    missing_group_count: int = 0
    invalid_path_count: int = 0
    signature_matched: bool = False

    @property
    def ok(self) -> bool:
        return self.status in {"matched", "partial", "empty"}


def _path_strings(paths: Iterable[Path]) -> list[str]:
    return [str(path) for path in paths]


def _group_lookup(groups: list[SimilarImageGroup]) -> dict[str, SimilarImageGroup]:
    return {build_similar_group_id(group): group for group in groups}


def _member_path_set(group: SimilarImageGroup) -> set[str]:
    return {str(member.path) for member in group.members}


def build_similar_group_signature(groups: list[SimilarImageGroup]) -> str:
    lines: list[str] = []
    for group in groups:
        gid = build_similar_group_id(group)
        member_paths = sorted(str(m.path) for m in group.members)
        member_hashes = sorted(m.hash_hex for m in group.members)
        lines.append(f"{gid}:{'|'.join(member_paths)}:{'|'.join(member_hashes)}")
    return "\n".join(lines)


def build_similar_decision_template(
    *,
    similar_groups: list[SimilarImageGroup],
    decisions: dict[str, dict[str, str]] | None = None,
    policy: str | None = None,
) -> dict[str, object]:
    """Build an editable similar-image decision file.

    Per-member decisions: "keep", "remove", "skip". Multiple members per group
    can be kept (unlike exact duplicates where only one survives).
    """

    decisions = dict(decisions or {})
    groups: list[dict[str, object]] = []
    total_members = 0
    unresolved_members = 0
    keep_count = 0

    for group in similar_groups:
        group_id = build_similar_group_id(group)
        group_decisions = decisions.get(group_id, {})
        members: list[dict[str, object]] = []
        group_keep_count = 0
        group_unresolved = 0

        for member in group.members:
            path_str = str(member.path)
            decision = group_decisions.get(path_str)
            is_anchor = member.path == group.anchor_path
            if decision is None and is_anchor:
                decision = "keep"
            members.append(
                {
                    "path": path_str,
                    "hash_hex": member.hash_hex,
                    "distance": member.distance,
                    "width": member.width,
                    "height": member.height,
                    "is_anchor": is_anchor,
                    "decision": decision,
                    "recommended_action": "keep" if is_anchor else "review-candidate",
                }
            )
            total_members += 1
            if decision == "keep":
                group_keep_count += 1
                keep_count += 1
            elif decision is None:
                group_unresolved += 1
                unresolved_members += 1

        groups.append(
            {
                "group_id": group_id,
                "anchor_path": str(group.anchor_path),
                "member_count": len(group.members),
                "keep_count": group_keep_count,
                "remove_count": sum(1 for v in group_decisions.values() if v == "remove"),
                "skip_count": sum(1 for v in group_decisions.values() if v == "skip"),
                "unresolved_count": group_unresolved,
                "members": members,
            }
        )

    return {
        "schema_version": 1,
        "type": "similar_decisions",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "policy": policy,
        "instructions": [
            "For each group member, set decision to one of: keep, remove, skip.",
            "At least one member per group should be marked 'keep'.",
            "The anchor image is auto-marked 'keep' if no decision is provided.",
            "Members marked 'remove' will be deleted when --similar-apply is used with --yes.",
        ],
        "group_signature": build_similar_group_signature(similar_groups),
        "group_count": len(similar_groups),
        "total_member_count": total_members,
        "resolved_member_count": total_members - unresolved_members,
        "unresolved_member_count": unresolved_members,
        "keep_count": keep_count,
        "groups": groups,
    }


def write_similar_decision_template(file_path: str | Path, payload: dict[str, object]) -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _decisions_from_similar_payload(payload: dict[str, object]) -> dict[str, dict[str, str]]:
    decisions: dict[str, dict[str, str]] = {}

    raw_groups = payload.get("groups", [])
    if isinstance(raw_groups, list):
        for item in raw_groups:
            if not isinstance(item, dict):
                continue
            group_id = str(item.get("group_id", ""))
            if not group_id:
                continue
            group_decisions: dict[str, str] = {}
            for member in item.get("members", []) if isinstance(item.get("members"), list) else []:
                if not isinstance(member, dict):
                    continue
                path_str = str(member.get("path", ""))
                decision = member.get("decision")
                if path_str and decision in {"keep", "remove", "skip"}:
                    group_decisions[path_str] = str(decision)
            if group_decisions:
                decisions[group_id] = group_decisions

    return decisions


def load_similar_decision_file(
    file_path: str | Path,
    similar_groups: list[SimilarImageGroup],
) -> SimilarDecisionImportResult:
    path = Path(file_path)
    if not path.exists():
        return SimilarDecisionImportResult(
            status="missing",
            reason="similar decision file does not exist",
        )

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return SimilarDecisionImportResult(
            status="error",
            reason=f"failed to load similar decision file: {exc}",
        )

    if not isinstance(payload, dict):
        return SimilarDecisionImportResult(
            status="error",
            reason="similar decision file must contain a JSON object",
        )

    group_by_id = _group_lookup(similar_groups)
    raw_decisions = _decisions_from_similar_payload(payload)
    normalized: dict[str, dict[str, str]] = {}
    missing_group_count = 0
    invalid_path_count = 0

    for group_id, group_decisions in raw_decisions.items():
        group = group_by_id.get(group_id)
        if group is None:
            missing_group_count += 1
            continue
        member_paths = _member_path_set(group)
        valid: dict[str, str] = {}
        for member_path, decision in group_decisions.items():
            if member_path not in member_paths:
                invalid_path_count += 1
                continue
            valid[member_path] = decision
        if valid:
            normalized[group_id] = valid

    file_group_count = int(payload.get("group_count", len(payload.get("groups", []) or [])) or 0)
    file_decision_count = sum(len(d) for d in raw_decisions.values())
    matched_decision_count = sum(len(d) for d in normalized.values())
    ignored_count = max(0, file_decision_count - matched_decision_count)
    current_signature = build_similar_group_signature(similar_groups)
    file_signature = str(payload.get("group_signature", ""))
    signature_matched = bool(file_signature) and file_signature == current_signature

    if not raw_decisions:
        status = "empty"
        reason = "similar decision file did not contain any decisions"
    elif normalized and ignored_count == 0 and (signature_matched or not file_signature):
        status = "matched"
        reason = "similar decision file matched the current similar image groups"
    elif normalized:
        status = "partial"
        reason = "similar decision file partially matched the current similar image groups"
    else:
        status = "mismatch"
        reason = "similar decision file did not contain usable decisions for the current similar image groups"

    return SimilarDecisionImportResult(
        status=status,
        reason=reason,
        decisions=normalized,
        file_group_count=file_group_count,
        file_decision_count=file_decision_count,
        matched_decision_count=matched_decision_count,
        ignored_decision_count=ignored_count,
        missing_group_count=missing_group_count,
        invalid_path_count=invalid_path_count,
        signature_matched=signature_matched,
    )


def similar_decision_import_payload(result: SimilarDecisionImportResult | None) -> dict[str, object] | None:
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
        "invalid_path_count": result.invalid_path_count,
        "signature_matched": result.signature_matched,
    }


__all__ = [
    "SimilarDecisionImportResult",
    "build_similar_decision_template",
    "build_similar_group_signature",
    "load_similar_decision_file",
    "similar_decision_import_payload",
    "write_similar_decision_template",
]
