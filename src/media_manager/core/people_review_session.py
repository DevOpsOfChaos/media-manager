from __future__ import annotations

from collections.abc import Iterable, Mapping
from copy import deepcopy
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Any

SESSION_SCHEMA_VERSION = 1
SESSION_KIND = "people_review_session"


@dataclass(slots=True)
class PeopleReviewSessionResult:
    operation: str
    changed: bool = False
    problems: list[dict[str, str]] = field(default_factory=list)
    workflow_payload: dict[str, object] = field(default_factory=dict)

    @property
    def status(self) -> str:
        return "ok" if not self.problems else "completed_with_problems"

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": SESSION_SCHEMA_VERSION,
            "session": SESSION_KIND,
            "operation": self.operation,
            "status": self.status,
            "changed": self.changed,
            "problem_count": len(self.problems),
            "problems": list(self.problems),
            "summary": summarize_people_review_workflow(self.workflow_payload),
            "workflow": self.workflow_payload,
            "next_action": "Continue reviewing people groups, then run people review-apply when ready.",
        }


def _as_text(value: object) -> str:
    return value if isinstance(value, str) else ""


def _as_bool(value: object, *, default: bool = False) -> bool:
    return value if isinstance(value, bool) else default


def _as_list(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def _as_mapping(value: object) -> Mapping[str, object]:
    return value if isinstance(value, Mapping) else {}


def _face_id(path: object, face_index: object) -> str:
    token = f"{_as_text(path)}::{int(face_index) if isinstance(face_index, int) else face_index}"
    digest = hashlib.sha1(token.encode("utf-8")).hexdigest()[:16]
    return f"face-{digest}"


def _ensure_workflow(payload: Mapping[str, object]) -> dict[str, object]:
    workflow = deepcopy(dict(payload))
    groups = workflow.get("groups")
    if not isinstance(groups, list):
        workflow["groups"] = []
    workflow.setdefault("schema_version", 1)
    workflow.setdefault("workflow", "people_review")
    workflow.setdefault("review_status", "needs_user_review")
    return workflow


def load_people_review_workflow(path: str | Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a people review workflow JSON object in {path}")
    return _ensure_workflow(payload)


def write_people_review_workflow_session(path: str | Path, workflow_payload: Mapping[str, object]) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(_ensure_workflow(workflow_payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


def _groups(workflow: Mapping[str, object]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for item in _as_list(workflow.get("groups")):
        if isinstance(item, dict):
            result.append(item)
    return result


def _find_group(workflow: Mapping[str, object], group_id: str) -> dict[str, object] | None:
    for group in _groups(workflow):
        if _as_text(group.get("review_group_id")) == group_id:
            return group
    return None


def _find_face(group: Mapping[str, object], face_id: str) -> dict[str, object] | None:
    for face in _as_list(group.get("faces")):
        if not isinstance(face, dict):
            continue
        resolved_face_id = _as_text(face.get("face_id")) or _face_id(face.get("path"), face.get("face_index"))
        if resolved_face_id == face_id:
            if not face.get("face_id"):
                face["face_id"] = resolved_face_id
            return face
    return None


def _iter_faces(workflow: Mapping[str, object]) -> Iterable[tuple[dict[str, object], dict[str, object]]]:
    for group in _groups(workflow):
        for face in _as_list(group.get("faces")):
            if isinstance(face, dict):
                resolved_face_id = _as_text(face.get("face_id")) or _face_id(face.get("path"), face.get("face_index"))
                if not face.get("face_id"):
                    face["face_id"] = resolved_face_id
                yield group, face


def summarize_people_review_workflow(workflow_payload: Mapping[str, object]) -> dict[str, object]:
    workflow = _ensure_workflow(workflow_payload)
    groups = _groups(workflow)
    face_count = 0
    included_faces = 0
    rejected_faces = 0
    ready_groups = 0
    named_groups = 0
    needs_name_groups = 0
    group_type_summary: dict[str, int] = {}
    status_summary: dict[str, int] = {}

    for group in groups:
        faces = [face for face in _as_list(group.get("faces")) if isinstance(face, Mapping)]
        included = sum(1 for face in faces if _as_bool(face.get("include"), default=True))
        rejected = len(faces) - included
        selected_name = _as_text(group.get("selected_name"))
        selected_person_id = _as_text(group.get("selected_person_id"))
        apply_group = _as_bool(group.get("apply_group"), default=False)
        group_type = _as_text(group.get("group_type")) or "unknown"
        group_type_summary[group_type] = group_type_summary.get(group_type, 0) + 1

        if apply_group and (selected_name or selected_person_id) and included > 0:
            status = "ready_to_apply"
            ready_groups += 1
        elif apply_group and not (selected_name or selected_person_id):
            status = "needs_name"
            needs_name_groups += 1
        elif selected_name or selected_person_id:
            status = "named_not_applied"
            named_groups += 1
        elif included == 0 and faces:
            status = "all_faces_rejected"
        else:
            status = "needs_review"
        status_summary[status] = status_summary.get(status, 0) + 1
        group["session_status"] = status

        face_count += len(faces)
        included_faces += included
        rejected_faces += rejected

    return {
        "group_count": len(groups),
        "face_count": face_count,
        "included_faces": included_faces,
        "rejected_faces": rejected_faces,
        "ready_group_count": ready_groups,
        "named_group_count": named_groups,
        "needs_name_group_count": needs_name_groups,
        "group_type_summary": dict(sorted(group_type_summary.items())),
        "status_summary": dict(sorted(status_summary.items())),
    }


def build_people_review_session_state(workflow_payload: Mapping[str, object]) -> dict[str, object]:
    workflow = _ensure_workflow(workflow_payload)
    summary = summarize_people_review_workflow(workflow)
    return {
        "schema_version": SESSION_SCHEMA_VERSION,
        "session": SESSION_KIND,
        "workflow": "people_review",
        "review_status": workflow.get("review_status", "needs_user_review"),
        "summary": summary,
        "groups": workflow.get("groups", []),
        "suggested_actions": [
            {
                "id": "continue_review",
                "label": "Continue reviewing people groups",
                "enabled": summary["group_count"] > 0,
            },
            {
                "id": "apply_ready_groups",
                "label": "Apply ready groups to catalog",
                "enabled": summary["ready_group_count"] > 0,
            },
            {
                "id": "name_groups",
                "label": "Name groups marked for apply",
                "enabled": summary["needs_name_group_count"] > 0,
            },
        ],
        "privacy_notice": "People review session files can reveal who appears in which local files. Keep them local/private.",
    }


def set_people_group_decision(
    workflow_payload: Mapping[str, object],
    *,
    group_id: str,
    apply_group: bool | None = None,
    selected_name: str | None = None,
    selected_person_id: str | None = None,
    review_note: str | None = None,
) -> PeopleReviewSessionResult:
    workflow = _ensure_workflow(workflow_payload)
    result = PeopleReviewSessionResult(operation="group-set", workflow_payload=workflow)
    group = _find_group(workflow, group_id)
    if group is None:
        result.problems.append({"code": "group_not_found", "message": f"Group not found: {group_id}"})
        return result

    if apply_group is not None:
        group["apply_group"] = bool(apply_group)
        result.changed = True
    if selected_name is not None:
        group["selected_name"] = selected_name
        result.changed = True
    if selected_person_id is not None:
        group["selected_person_id"] = selected_person_id
        result.changed = True
    if review_note is not None:
        group["review_note"] = review_note
        result.changed = True
    summarize_people_review_workflow(workflow)
    return result


def set_people_face_decision(
    workflow_payload: Mapping[str, object],
    *,
    face_id: str,
    include: bool | None = None,
    note: str | None = None,
) -> PeopleReviewSessionResult:
    workflow = _ensure_workflow(workflow_payload)
    result = PeopleReviewSessionResult(operation="face-set", workflow_payload=workflow)
    target_face: dict[str, object] | None = None
    for _group, face in _iter_faces(workflow):
        if _as_text(face.get("face_id")) == face_id:
            target_face = face
            break
    if target_face is None:
        result.problems.append({"code": "face_not_found", "message": f"Face not found: {face_id}"})
        return result

    if include is not None:
        target_face["include"] = bool(include)
        result.changed = True
    if note is not None:
        target_face["note"] = note
        result.changed = True
    summarize_people_review_workflow(workflow)
    return result


def _unique_group_id(workflow: Mapping[str, object], preferred: str) -> str:
    existing = {_as_text(group.get("review_group_id")) for group in _groups(workflow)}
    candidate = preferred or "manual-group"
    counter = 2
    while candidate in existing:
        candidate = f"{preferred}-{counter}"
        counter += 1
    return candidate


def split_people_group(
    workflow_payload: Mapping[str, object],
    *,
    group_id: str,
    face_ids: Iterable[str],
    new_group_id: str | None = None,
    selected_name: str = "",
) -> PeopleReviewSessionResult:
    workflow = _ensure_workflow(workflow_payload)
    result = PeopleReviewSessionResult(operation="group-split", workflow_payload=workflow)
    group = _find_group(workflow, group_id)
    if group is None:
        result.problems.append({"code": "group_not_found", "message": f"Group not found: {group_id}"})
        return result

    requested = {str(item) for item in face_ids if str(item)}
    if not requested:
        result.problems.append({"code": "no_faces_selected", "message": "At least one face_id is required for a split."})
        return result

    original_faces = [face for face in _as_list(group.get("faces")) if isinstance(face, dict)]
    moving: list[dict[str, object]] = []
    remaining: list[dict[str, object]] = []
    for face in original_faces:
        resolved_face_id = _as_text(face.get("face_id")) or _face_id(face.get("path"), face.get("face_index"))
        face["face_id"] = resolved_face_id
        if resolved_face_id in requested:
            moving.append(face)
        else:
            remaining.append(face)

    missing = requested - {_as_text(face.get("face_id")) for face in moving}
    for face_id in sorted(missing):
        result.problems.append({"code": "face_not_found", "message": f"Face not found in group {group_id}: {face_id}"})
    if not moving:
        return result

    group["faces"] = remaining
    resolved_new_group_id = _unique_group_id(workflow, new_group_id or f"{group_id}-split")
    new_group = {
        "review_group_id": resolved_new_group_id,
        "group_type": "manual_split",
        "apply_group": False,
        "selected_person_id": "",
        "selected_name": selected_name,
        "suggested_person_id": "",
        "suggested_name": selected_name,
        "faces": moving,
        "review_note": f"Split from {group_id}",
    }
    workflow["groups"] = [*_groups(workflow), new_group]
    result.changed = True
    summarize_people_review_workflow(workflow)
    return result


def merge_people_groups(
    workflow_payload: Mapping[str, object],
    *,
    group_ids: Iterable[str],
    target_group_id: str | None = None,
    selected_name: str | None = None,
) -> PeopleReviewSessionResult:
    workflow = _ensure_workflow(workflow_payload)
    result = PeopleReviewSessionResult(operation="group-merge", workflow_payload=workflow)
    requested = [str(item) for item in group_ids if str(item)]
    if len(requested) < 2:
        result.problems.append({"code": "not_enough_groups", "message": "At least two group IDs are required for a merge."})
        return result

    groups = _groups(workflow)
    found = [group for group in groups if _as_text(group.get("review_group_id")) in set(requested)]
    found_ids = {_as_text(group.get("review_group_id")) for group in found}
    for group_id in sorted(set(requested) - found_ids):
        result.problems.append({"code": "group_not_found", "message": f"Group not found: {group_id}"})
    if len(found) < 2:
        return result

    resolved_target_id = _unique_group_id(workflow, target_group_id or "manual-merge")
    merged_faces: list[object] = []
    for group in found:
        merged_faces.extend(_as_list(group.get("faces")))
    remaining_groups = [group for group in groups if _as_text(group.get("review_group_id")) not in found_ids]
    names = [name for group in found if (name := _as_text(group.get("selected_name") or group.get("suggested_name")))]
    resolved_name = selected_name if selected_name is not None else (names[0] if names and len(set(names)) == 1 else "")
    merged_group = {
        "review_group_id": resolved_target_id,
        "group_type": "manual_merge",
        "apply_group": False,
        "selected_person_id": "",
        "selected_name": resolved_name,
        "suggested_person_id": "",
        "suggested_name": resolved_name,
        "faces": merged_faces,
        "review_note": "Merged from " + ", ".join(requested),
    }
    workflow["groups"] = [*remaining_groups, merged_group]
    result.changed = True
    summarize_people_review_workflow(workflow)
    return result


__all__ = [
    "SESSION_KIND",
    "SESSION_SCHEMA_VERSION",
    "PeopleReviewSessionResult",
    "build_people_review_session_state",
    "load_people_review_workflow",
    "merge_people_groups",
    "set_people_face_decision",
    "set_people_group_decision",
    "split_people_group",
    "summarize_people_review_workflow",
    "write_people_review_workflow_session",
]
