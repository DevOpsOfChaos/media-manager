from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Any

from .people_recognition import (
    PeopleCatalog,
    add_embedding_to_person,
    add_person_to_catalog,
    load_people_catalog,
    write_people_catalog,
)

WORKFLOW_SCHEMA_VERSION = 1
WORKFLOW_KIND = "people_review"


@dataclass(slots=True)
class PeopleReviewApplyResult:
    catalog_path: str
    dry_run: bool = False
    groups_seen: int = 0
    groups_applied: int = 0
    groups_skipped: int = 0
    persons_created: int = 0
    persons_updated: int = 0
    embeddings_added: int = 0
    faces_included: int = 0
    faces_rejected: int = 0
    problems: list[dict[str, str]] = field(default_factory=list)

    @property
    def status(self) -> str:
        return "ok" if not self.problems else "completed_with_problems"

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": WORKFLOW_SCHEMA_VERSION,
            "workflow": WORKFLOW_KIND,
            "status": self.status,
            "catalog_path": self.catalog_path,
            "dry_run": self.dry_run,
            "summary": {
                "groups_seen": self.groups_seen,
                "groups_applied": self.groups_applied,
                "groups_skipped": self.groups_skipped,
                "persons_created": self.persons_created,
                "persons_updated": self.persons_updated,
                "embeddings_added": self.embeddings_added,
                "faces_included": self.faces_included,
                "faces_rejected": self.faces_rejected,
                "problem_count": len(self.problems),
            },
            "problems": list(self.problems),
            "next_action": (
                "Review problems and rerun review-apply."
                if self.problems
                else "Run another people scan with the updated catalog to verify named-person matching."
            ),
            "privacy_notice": (
                "People review workflows and reports can contain sensitive biometric metadata. "
                "Keep them local/private."
            ),
        }


def _as_text(value: object) -> str:
    return value if isinstance(value, str) else ""


def _as_bool(value: object, *, default: bool = False) -> bool:
    return value if isinstance(value, bool) else default


def _face_id(path: object, face_index: object) -> str:
    token = f"{_as_text(path)}::{int(face_index) if isinstance(face_index, int) else face_index}"
    digest = hashlib.sha1(token.encode("utf-8")).hexdigest()[:16]
    return f"face-{digest}"


def _face_sort_key(face: Mapping[str, object]) -> tuple[str, int]:
    path = _as_text(face.get("path")).casefold()
    index = face.get("face_index")
    return path, index if isinstance(index, int) else 0


def _group_sort_key(group: Mapping[str, object]) -> tuple[int, str]:
    faces = group.get("faces")
    size = len(faces) if isinstance(faces, list) else 0
    return (-size, _as_text(group.get("review_group_id")).casefold())


def _build_face_reference(item: Mapping[str, object]) -> dict[str, object]:
    path = item.get("path")
    face_index = item.get("face_index")
    face_id = _face_id(path, face_index)
    return {
        "face_id": face_id,
        "path": path,
        "face_index": face_index,
        "box": item.get("box"),
        "backend": item.get("backend"),
        "include": True,
        "note": "",
    }


def build_people_review_workflow(
    scan_payload: Mapping[str, object],
    *,
    group_limit: int | None = None,
    face_limit_per_group: int | None = None,
) -> dict[str, object]:
    """Build an editable review workflow from a people scan report.

    The workflow is intentionally indirect: the scan groups faces first, then a
    human reviewer names groups and excludes wrong faces before the catalog is
    updated.
    """

    detections = scan_payload.get("detections", [])
    if not isinstance(detections, list):
        detections = []

    groups_by_id: dict[str, dict[str, object]] = {}
    for raw_item in detections:
        if not isinstance(raw_item, Mapping):
            continue

        matched_person_id = _as_text(raw_item.get("matched_person_id"))
        matched_name = _as_text(raw_item.get("matched_name"))
        unknown_cluster_id = _as_text(raw_item.get("unknown_cluster_id"))
        face_ref = _build_face_reference(raw_item)

        if matched_person_id:
            review_group_id = f"matched-{matched_person_id}"
            group = groups_by_id.setdefault(
                review_group_id,
                {
                    "review_group_id": review_group_id,
                    "group_type": "matched_person",
                    "apply_group": False,
                    "selected_person_id": matched_person_id,
                    "selected_name": matched_name,
                    "suggested_person_id": matched_person_id,
                    "suggested_name": matched_name,
                    "faces": [],
                    "review_note": "",
                },
            )
        else:
            review_group_id = unknown_cluster_id or f"unknown-single-{face_ref['face_id']}"
            group = groups_by_id.setdefault(
                review_group_id,
                {
                    "review_group_id": review_group_id,
                    "group_type": "unknown_cluster" if unknown_cluster_id else "unknown_single",
                    "apply_group": False,
                    "selected_person_id": "",
                    "selected_name": "",
                    "suggested_person_id": "",
                    "suggested_name": "",
                    "faces": [],
                    "review_note": "",
                },
            )

        faces = group.setdefault("faces", [])
        if isinstance(faces, list):
            faces.append(face_ref)

    groups = list(groups_by_id.values())
    for group in groups:
        faces = group.get("faces")
        if isinstance(faces, list):
            faces.sort(key=lambda item: _face_sort_key(item) if isinstance(item, Mapping) else ("", 0))
            if face_limit_per_group is not None and face_limit_per_group >= 0:
                group["faces_truncated"] = len(faces) > face_limit_per_group
                group["faces"] = faces[:face_limit_per_group]
            else:
                group["faces_truncated"] = False

    groups.sort(key=_group_sort_key)
    if group_limit is not None and group_limit >= 0:
        truncated = len(groups) > group_limit
        groups = groups[:group_limit]
    else:
        truncated = False

    encoding_count = 0
    for raw_item in detections:
        if isinstance(raw_item, Mapping) and isinstance(raw_item.get("encoding"), list):
            encoding_count += 1

    return {
        "schema_version": WORKFLOW_SCHEMA_VERSION,
        "workflow": WORKFLOW_KIND,
        "review_status": "needs_user_review",
        "source_report_summary": scan_payload.get("summary", {}),
        "requires_report_with_encodings_for_apply": True,
        "encoding_count_in_source_report": encoding_count,
        "group_count": len(groups),
        "truncated": truncated,
        "instructions": [
            "Run people scan with --include-encodings when you want to apply this workflow to the catalog.",
            "For each group that should teach the catalog, set apply_group to true.",
            "Set selected_name for a new person, or selected_person_id for an existing person.",
            "Set include to false on faces that do not belong to the selected person.",
            "Keep workflow files and reports private because they can contain sensitive biometric metadata.",
        ],
        "groups": groups,
        "privacy_notice": (
            "This workflow can reveal who appears in which local files. "
            "When paired with a report that includes encodings, it references sensitive biometric metadata."
        ),
    }


def write_people_review_workflow(path: str | Path, workflow_payload: Mapping[str, object]) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(dict(workflow_payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


def _detections_by_face_id(report_payload: Mapping[str, object]) -> dict[str, Mapping[str, object]]:
    detections = report_payload.get("detections", [])
    if not isinstance(detections, list):
        return {}
    result: dict[str, Mapping[str, object]] = {}
    for raw_item in detections:
        if not isinstance(raw_item, Mapping):
            continue
        result[_face_id(raw_item.get("path"), raw_item.get("face_index"))] = raw_item
    return result


def _iter_included_faces(group: Mapping[str, object]) -> Iterable[Mapping[str, object]]:
    faces = group.get("faces", [])
    if not isinstance(faces, list):
        return ()
    return tuple(
        face
        for face in faces
        if isinstance(face, Mapping) and _as_bool(face.get("include"), default=True)
    )


def _count_rejected_faces(group: Mapping[str, object]) -> int:
    faces = group.get("faces", [])
    if not isinstance(faces, list):
        return 0
    return sum(
        1
        for face in faces
        if isinstance(face, Mapping) and not _as_bool(face.get("include"), default=True)
    )


def _resolve_or_create_person(
    catalog: PeopleCatalog,
    *,
    selected_person_id: str,
    selected_name: str,
    result: PeopleReviewApplyResult,
) -> str | None:
    if selected_person_id and selected_person_id in catalog.persons:
        result.persons_updated += 1
        return selected_person_id

    if selected_name:
        person = add_person_to_catalog(
            catalog,
            name=selected_name,
            person_id=selected_person_id or None,
        )
        result.persons_created += 1
        return person.person_id

    if selected_person_id:
        result.problems.append(
            {
                "code": "unknown_person_id",
                "message": f"selected_person_id does not exist and selected_name is empty: {selected_person_id}",
            }
        )
    else:
        result.problems.append(
            {
                "code": "missing_person_selection",
                "message": "Group is marked for apply but neither selected_name nor selected_person_id is set.",
            }
        )
    return None


def apply_people_review_workflow(
    *,
    catalog_path: str | Path,
    workflow_payload: Mapping[str, object],
    report_payload: Mapping[str, object],
    output_catalog_path: str | Path | None = None,
    dry_run: bool = False,
) -> PeopleReviewApplyResult:
    """Apply reviewed people groups to a local people catalog.

    The workflow file contains reviewer choices; the report supplies the actual
    face encodings. This keeps the editable workflow relatively readable while
    still allowing the apply step to add embeddings to the catalog.
    """

    destination = Path(output_catalog_path or catalog_path)
    result = PeopleReviewApplyResult(catalog_path=str(destination), dry_run=dry_run)
    catalog = load_people_catalog(catalog_path)
    detections_by_id = _detections_by_face_id(report_payload)

    groups = workflow_payload.get("groups", [])
    if not isinstance(groups, list):
        result.problems.append({"code": "invalid_workflow", "message": "Expected groups list in workflow payload."})
        return result

    result.groups_seen = len(groups)

    for raw_group in groups:
        if not isinstance(raw_group, Mapping):
            result.groups_skipped += 1
            result.problems.append({"code": "invalid_group", "message": "Skipping non-object group entry."})
            continue

        if not _as_bool(raw_group.get("apply_group"), default=False):
            result.groups_skipped += 1
            result.faces_rejected += _count_rejected_faces(raw_group)
            continue

        selected_person_id = _as_text(raw_group.get("selected_person_id"))
        selected_name = _as_text(raw_group.get("selected_name"))
        person_id = _resolve_or_create_person(
            catalog,
            selected_person_id=selected_person_id,
            selected_name=selected_name,
            result=result,
        )
        if person_id is None:
            result.groups_skipped += 1
            continue

        included_faces = tuple(_iter_included_faces(raw_group))
        added_for_group = 0
        for face in included_faces:
            face_id = _as_text(face.get("face_id"))
            detection = detections_by_id.get(face_id)
            if detection is None:
                result.problems.append(
                    {
                        "code": "face_not_found",
                        "message": f"Face reference was not found in report: {face_id}",
                    }
                )
                continue

            encoding = detection.get("encoding")
            if not isinstance(encoding, list) or not encoding:
                result.problems.append(
                    {
                        "code": "missing_encoding",
                        "message": (
                            f"Face {face_id} has no encoding in the report. "
                            "Rerun scan with --include-encodings before review-apply."
                        ),
                    }
                )
                continue

            box = detection.get("box") if isinstance(detection.get("box"), Mapping) else None
            source_path = _as_text(detection.get("path")) or None
            if not dry_run:
                add_embedding_to_person(
                    catalog,
                    person_id=person_id,
                    encoding=[float(value) for value in encoding],
                    source_path=source_path,
                    box=box,
                )
            result.embeddings_added += 1
            result.faces_included += 1
            added_for_group += 1

        result.faces_rejected += _count_rejected_faces(raw_group)
        if added_for_group:
            result.groups_applied += 1
        else:
            result.groups_skipped += 1

    if not dry_run:
        write_people_catalog(destination, catalog)

    return result


__all__ = [
    "WORKFLOW_KIND",
    "WORKFLOW_SCHEMA_VERSION",
    "PeopleReviewApplyResult",
    "apply_people_review_workflow",
    "build_people_review_workflow",
    "write_people_review_workflow",
]
