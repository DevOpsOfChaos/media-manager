from __future__ import annotations

from collections.abc import Mapping
import hashlib
from typing import Any

from .people_review_workflow import build_people_review_workflow

WORKSPACE_SCHEMA_VERSION = 1
WORKSPACE_KIND = "people_review_workspace"
PAGE_ID = "people-review"


def _as_text(value: object) -> str:
    return value if isinstance(value, str) else ""


def _as_bool(value: object, *, default: bool = False) -> bool:
    return value if isinstance(value, bool) else default


def _as_int(value: object, *, default: int = 0) -> int:
    return value if isinstance(value, int) else default


def _as_mapping(value: object) -> Mapping[str, object]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def _face_id(path: object, face_index: object) -> str:
    token = f"{_as_text(path)}::{int(face_index) if isinstance(face_index, int) else face_index}"
    digest = hashlib.sha1(token.encode("utf-8")).hexdigest()[:16]
    return f"face-{digest}"


def _detections_by_face_id(report_payload: Mapping[str, object]) -> dict[str, Mapping[str, object]]:
    result: dict[str, Mapping[str, object]] = {}
    for raw_item in _as_list(report_payload.get("detections")):
        if not isinstance(raw_item, Mapping):
            continue
        face_id = _face_id(raw_item.get("path"), raw_item.get("face_index"))
        result[face_id] = raw_item
    return result


def _face_sort_key(face: Mapping[str, object]) -> tuple[str, int]:
    return _as_text(face.get("path")).casefold(), _as_int(face.get("face_index"))


def _group_sort_key(group: Mapping[str, object]) -> tuple[int, str]:
    faces = _as_list(group.get("faces"))
    ready_rank = 0 if _as_bool(group.get("apply_group")) else 1
    return ready_rank, -len(faces), _as_text(group.get("review_group_id")).casefold()


def _encoding_stats(detection: Mapping[str, object]) -> tuple[bool, int]:
    encoding = detection.get("encoding")
    if not isinstance(encoding, list) or not encoding:
        return False, 0
    return True, len(encoding)


def _group_status(group: Mapping[str, object], *, included_count: int) -> str:
    apply_group = _as_bool(group.get("apply_group"), default=False)
    selected_name = _as_text(group.get("selected_name"))
    selected_person_id = _as_text(group.get("selected_person_id"))
    if apply_group and not (selected_name or selected_person_id):
        return "needs_name"
    if apply_group and included_count == 0:
        return "needs_included_faces"
    if apply_group:
        return "ready_to_apply"
    if selected_name or selected_person_id:
        return "named_not_applied"
    if included_count == 0:
        return "all_faces_rejected"
    return "needs_review"


def _face_decision_status(*, include: bool, group_status: str, detection: Mapping[str, object]) -> str:
    if not include:
        return "rejected"
    if group_status == "ready_to_apply":
        return "accepted"
    if _as_text(detection.get("matched_person_id")):
        return "matched_existing"
    return "pending_review"


def _build_face_card(
    face: Mapping[str, object],
    *,
    detection: Mapping[str, object],
    group_status: str,
    include_encodings: bool,
) -> dict[str, object]:
    face_id = _as_text(face.get("face_id")) or _face_id(face.get("path"), face.get("face_index"))
    path = _as_text(face.get("path")) or _as_text(detection.get("path"))
    include = _as_bool(face.get("include"), default=True)
    has_encoding, encoding_dim = _encoding_stats(detection)
    payload: dict[str, object] = {
        "face_id": face_id,
        "path": path,
        "image_uri": {"type": "local_path", "value": path},
        "face_index": face.get("face_index", detection.get("face_index")),
        "box": face.get("box", detection.get("box")),
        "backend": face.get("backend", detection.get("backend")),
        "include": include,
        "decision_status": _face_decision_status(include=include, group_status=group_status, detection=detection),
        "matched_person_id": detection.get("matched_person_id"),
        "matched_name": detection.get("matched_name"),
        "match_distance": detection.get("match_distance"),
        "unknown_cluster_id": detection.get("unknown_cluster_id"),
        "has_encoding": has_encoding,
        "encoding_dim": encoding_dim,
        "note": face.get("note", ""),
    }
    if include_encodings and has_encoding:
        payload["encoding"] = list(detection.get("encoding", []))
    return payload


def _build_group_card(
    group: Mapping[str, object],
    *,
    detections_by_id: Mapping[str, Mapping[str, object]],
    include_encodings: bool,
    face_limit_per_group: int | None,
) -> dict[str, object]:
    raw_faces = [item for item in _as_list(group.get("faces")) if isinstance(item, Mapping)]
    raw_faces.sort(key=_face_sort_key)
    truncated = False
    if face_limit_per_group is not None and face_limit_per_group >= 0 and len(raw_faces) > face_limit_per_group:
        raw_faces = raw_faces[:face_limit_per_group]
        truncated = True

    included_count = sum(1 for item in raw_faces if _as_bool(item.get("include"), default=True))
    excluded_count = len(raw_faces) - included_count
    status = _group_status(group, included_count=included_count)

    face_cards: list[dict[str, object]] = []
    encoding_count = 0
    for face in raw_faces:
        face_id = _as_text(face.get("face_id")) or _face_id(face.get("path"), face.get("face_index"))
        detection = detections_by_id.get(face_id, {})
        card = _build_face_card(face, detection=detection, group_status=status, include_encodings=include_encodings)
        if card["has_encoding"]:
            encoding_count += 1
        face_cards.append(card)

    selected_name = _as_text(group.get("selected_name"))
    selected_person_id = _as_text(group.get("selected_person_id"))
    suggested_name = _as_text(group.get("suggested_name"))
    suggested_person_id = _as_text(group.get("suggested_person_id"))
    display_label = selected_name or suggested_name or selected_person_id or suggested_person_id or _as_text(group.get("review_group_id"))

    return {
        "group_id": group.get("review_group_id"),
        "group_type": group.get("group_type"),
        "display_label": display_label,
        "status": status,
        "apply_group": _as_bool(group.get("apply_group"), default=False),
        "selected_person_id": selected_person_id,
        "selected_name": selected_name,
        "suggested_person_id": suggested_person_id,
        "suggested_name": suggested_name,
        "review_note": group.get("review_note", ""),
        "primary_face_id": face_cards[0]["face_id"] if face_cards else None,
        "counts": {
            "face_count": len(face_cards),
            "included_faces": included_count,
            "excluded_faces": excluded_count,
            "faces_with_encodings": encoding_count,
        },
        "faces_truncated": truncated or _as_bool(group.get("faces_truncated"), default=False),
        "faces": face_cards,
    }


def build_people_review_workspace(
    *,
    report_payload: Mapping[str, object],
    workflow_payload: Mapping[str, object] | None = None,
    group_limit: int | None = None,
    face_limit_per_group: int | None = None,
    include_encodings: bool = False,
) -> dict[str, object]:
    """Build a GUI-facing people review page model.

    This is intentionally a read/render model: it does not apply catalog changes.
    The future GUI can persist reviewer decisions in the workflow JSON and then
    call review-apply when the user confirms the curated groups.
    """

    workflow = workflow_payload or build_people_review_workflow(report_payload)
    groups = [item for item in _as_list(workflow.get("groups")) if isinstance(item, Mapping)]
    groups.sort(key=_group_sort_key)
    groups_truncated = False
    if group_limit is not None and group_limit >= 0 and len(groups) > group_limit:
        groups = groups[:group_limit]
        groups_truncated = True

    detections_by_id = _detections_by_face_id(report_payload)
    group_cards = [
        _build_group_card(
            group,
            detections_by_id=detections_by_id,
            include_encodings=include_encodings,
            face_limit_per_group=face_limit_per_group,
        )
        for group in groups
    ]

    total_faces = sum(_as_mapping(group.get("counts")).get("face_count", 0) for group in group_cards)
    included_faces = sum(_as_mapping(group.get("counts")).get("included_faces", 0) for group in group_cards)
    excluded_faces = sum(_as_mapping(group.get("counts")).get("excluded_faces", 0) for group in group_cards)
    faces_with_encodings = sum(_as_mapping(group.get("counts")).get("faces_with_encodings", 0) for group in group_cards)
    ready_group_count = sum(1 for group in group_cards if group.get("status") == "ready_to_apply")
    needs_name_group_count = sum(1 for group in group_cards if group.get("status") == "needs_name")
    needs_review_group_count = sum(1 for group in group_cards if group.get("status") == "needs_review")

    backend = report_payload.get("backend")
    capabilities = _as_mapping(report_payload.get("capabilities"))
    source_summary = _as_mapping(report_payload.get("summary"))
    has_report_encodings = faces_with_encodings > 0

    return {
        "schema_version": WORKSPACE_SCHEMA_VERSION,
        "workspace": WORKSPACE_KIND,
        "page_id": PAGE_ID,
        "command": "people",
        "mode": "review",
        "backend": backend,
        "capabilities": dict(capabilities),
        "source_report_summary": dict(source_summary),
        "overview": {
            "group_count": len(group_cards),
            "face_count": total_faces,
            "included_faces": included_faces,
            "excluded_faces": excluded_faces,
            "faces_with_encodings": faces_with_encodings,
            "ready_group_count": ready_group_count,
            "needs_name_group_count": needs_name_group_count,
            "needs_review_group_count": needs_review_group_count,
            "has_report_encodings": has_report_encodings,
            "groups_truncated": groups_truncated or _as_bool(workflow.get("truncated"), default=False),
        },
        "groups": group_cards,
        "suggested_actions": [
            {
                "id": "review_groups",
                "label": "Review detected people groups",
                "enabled": len(group_cards) > 0,
                "reason": "Open each group, confirm the name, and reject faces that belong to another person.",
            },
            {
                "id": "apply_review",
                "label": "Apply reviewed people to catalog",
                "enabled": ready_group_count > 0 and has_report_encodings,
                "reason": "Enabled when at least one group is ready and the report contains face encodings.",
            },
            {
                "id": "rerun_scan_with_encodings",
                "label": "Rerun scan with encodings",
                "enabled": ready_group_count > 0 and not has_report_encodings,
                "reason": "review-apply needs a report produced with --include-encodings.",
            },
            {
                "id": "rerun_scan_after_apply",
                "label": "Rerun scan after applying catalog changes",
                "enabled": ready_group_count > 0,
                "reason": "Verify that named-person matching improves after catalog training.",
            },
        ],
        "ui_contract": {
            "group_list": "Render groups as a sidebar/list ordered by review status and group size.",
            "face_cards": "Render each face as a local image card with crop box metadata and include/reject controls.",
            "review_fields": ["apply_group", "selected_person_id", "selected_name", "faces[].include", "faces[].note"],
            "persistence": "Save reviewer decisions back to the workflow JSON, then call people review-apply.",
        },
        "privacy_notice": (
            "This workspace can reveal who appears in which local files. If encodings are included, "
            "the JSON contains sensitive biometric metadata and should stay local/private."
        ),
    }


def build_people_review_workspace_summary_text(payload: Mapping[str, object]) -> str:
    overview = _as_mapping(payload.get("overview"))
    return "\n".join(
        [
            "People review workspace",
            f"  Groups: {overview.get('group_count', 0)}",
            f"  Faces: {overview.get('face_count', 0)}",
            f"  Ready groups: {overview.get('ready_group_count', 0)}",
            f"  Needs name: {overview.get('needs_name_group_count', 0)}",
            f"  Needs review: {overview.get('needs_review_group_count', 0)}",
            f"  Has report encodings: {overview.get('has_report_encodings', False)}",
        ]
    )


__all__ = [
    "PAGE_ID",
    "WORKSPACE_KIND",
    "WORKSPACE_SCHEMA_VERSION",
    "build_people_review_workspace",
    "build_people_review_workspace_summary_text",
]
