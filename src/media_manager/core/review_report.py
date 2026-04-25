from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
from pathlib import Path


def _string_or_none(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _path_or_none(value: object) -> str | None:
    if value is None:
        return None
    try:
        return str(value)
    except TypeError:
        return None


def _warning_payloads(entry: object) -> list[dict[str, object]]:
    warnings = getattr(entry, "association_warnings", ()) or ()
    if not warnings:
        media_group = getattr(entry, "media_group", None)
        warnings = getattr(media_group, "association_warnings", ()) or ()

    payloads: list[dict[str, object]] = []
    for warning in warnings:
        payloads.append(
            {
                "path": _path_or_none(getattr(warning, "path", None)),
                "warning_code": _string_or_none(getattr(warning, "warning_code", None)),
                "message": _string_or_none(getattr(warning, "message", None)),
            }
        )
    return payloads


def _entry_review_reasons(entry: object) -> tuple[str, ...]:
    reasons: list[str] = []

    warning_count = 0
    try:
        warning_count = int(getattr(entry, "association_warning_count", 0))
    except (TypeError, ValueError):
        warning_count = 0
    if warning_count > 0 or _warning_payloads(entry):
        reasons.append("association_warning")

    markers = {
        getattr(entry, "status", None),
        getattr(entry, "outcome", None),
        getattr(entry, "action", None),
    }
    if "conflict" in markers:
        reasons.append("conflict")
    if "error" in markers:
        reasons.append("error")

    return tuple(reasons)


def build_review_candidate_payload(section: str, entry: object, reasons: Iterable[str]) -> dict[str, object]:
    plan_entry = getattr(entry, "plan_entry", None)
    source_path = getattr(entry, "source_path", None)
    target_path = getattr(entry, "target_path", None)
    if source_path is None and plan_entry is not None:
        source_path = getattr(plan_entry, "source_path", None)
    if target_path is None and plan_entry is not None:
        target_path = getattr(plan_entry, "target_path", None)

    source_root = getattr(entry, "source_root", None)
    if source_root is None and plan_entry is not None:
        source_root = getattr(plan_entry, "source_root", None)

    associated_paths = getattr(entry, "associated_paths", None)
    if associated_paths is None and plan_entry is not None:
        associated_paths = getattr(plan_entry, "associated_paths", ())

    return {
        "section": section,
        "source_root": _path_or_none(source_root),
        "source_path": _path_or_none(source_path),
        "target_path": _path_or_none(target_path),
        "status": _string_or_none(getattr(entry, "status", None)),
        "outcome": _string_or_none(getattr(entry, "outcome", None)),
        "action": _string_or_none(getattr(entry, "action", None)),
        "reason": _string_or_none(getattr(entry, "reason", None)),
        "review_reasons": list(reasons),
        "group_id": _string_or_none(getattr(entry, "group_id", getattr(plan_entry, "group_id", None))),
        "group_kind": _string_or_none(getattr(entry, "group_kind", getattr(plan_entry, "group_kind", None))),
        "main_file": _path_or_none(getattr(plan_entry, "source_path", source_path)),
        "associated_files": [str(path) for path in (associated_paths or ())],
        "associated_file_count": int(getattr(entry, "associated_file_count", getattr(plan_entry, "associated_file_count", 0)) or 0),
        "association_warnings": _warning_payloads(entry if _warning_payloads(entry) else plan_entry),
    }


def build_review_export(
    sections: Mapping[str, Iterable[object]],
    *,
    candidate_limit: int = 50,
) -> dict[str, object]:
    candidates: list[dict[str, object]] = []
    section_counter: Counter[str] = Counter()
    reason_counter: Counter[str] = Counter()

    for section, entries in sections.items():
        for entry in entries:
            reasons = _entry_review_reasons(entry)
            if not reasons:
                continue
            section_counter[section] += 1
            for reason in reasons:
                reason_counter[reason] += 1
            if len(candidates) < candidate_limit:
                candidates.append(build_review_candidate_payload(section, entry, reasons))

    candidate_count = sum(section_counter.values())
    return {
        "candidate_count": candidate_count,
        "candidate_limit": candidate_limit,
        "truncated": candidate_count > len(candidates),
        "section_summary": dict(sorted(section_counter.items())),
        "reason_summary": dict(sorted(reason_counter.items())),
        "candidates": candidates,
    }


__all__ = [
    "build_review_candidate_payload",
    "build_review_export",
]
