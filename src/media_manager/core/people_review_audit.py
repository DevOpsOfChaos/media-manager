from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .people_review_workflow import apply_people_review_workflow

AUDIT_SCHEMA_VERSION = 1
AUDIT_KIND = "people_review_apply_preview"


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _as_bool(value: Any, *, default: bool = False) -> bool:
    return value if isinstance(value, bool) else default


def _group_preview(group: Mapping[str, Any]) -> dict[str, object]:
    faces = [face for face in _as_list(group.get("faces")) if isinstance(face, Mapping)]
    included = [face for face in faces if _as_bool(face.get("include"), default=True)]
    rejected = [face for face in faces if not _as_bool(face.get("include"), default=True)]
    selected_name = _as_text(group.get("selected_name"))
    selected_person_id = _as_text(group.get("selected_person_id"))
    apply_group = _as_bool(group.get("apply_group"), default=False)
    if not apply_group:
        status = "skipped"
    elif not (selected_name or selected_person_id):
        status = "blocked_missing_person"
    elif not included:
        status = "blocked_no_faces"
    else:
        status = "ready"
    return {
        "review_group_id": group.get("review_group_id"),
        "group_type": group.get("group_type"),
        "status": status,
        "apply_group": apply_group,
        "selected_person_id": selected_person_id,
        "selected_name": selected_name,
        "face_count": len(faces),
        "included_face_count": len(included),
        "rejected_face_count": len(rejected),
        "included_face_ids": [_as_text(face.get("face_id")) for face in included],
        "rejected_face_ids": [_as_text(face.get("face_id")) for face in rejected],
    }


def build_people_review_apply_preview(
    *,
    catalog_path: str | Path,
    workflow_payload: Mapping[str, Any],
    report_payload: Mapping[str, Any],
    output_catalog_path: str | Path | None = None,
) -> dict[str, object]:
    """Validate and summarize what review-apply would do without writing the catalog."""
    dry_result = apply_people_review_workflow(
        catalog_path=catalog_path,
        workflow_payload=workflow_payload,
        report_payload=report_payload,
        output_catalog_path=output_catalog_path,
        dry_run=True,
    )
    groups = [item for item in _as_list(workflow_payload.get("groups")) if isinstance(item, Mapping)]
    group_previews = [_group_preview(group) for group in groups]
    ready_count = sum(1 for group in group_previews if group.get("status") == "ready")
    blocked_count = sum(1 for group in group_previews if str(group.get("status", "")).startswith("blocked"))
    skipped_count = sum(1 for group in group_previews if group.get("status") == "skipped")
    result_payload = dry_result.to_dict()
    summary = _as_mapping(result_payload.get("summary"))
    return {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "kind": AUDIT_KIND,
        "generated_at_utc": _now_utc(),
        "catalog_path": str(catalog_path),
        "output_catalog_path": str(output_catalog_path or catalog_path),
        "safe_to_apply": dry_result.status == "ok" and blocked_count == 0 and ready_count > 0,
        "status": dry_result.status,
        "summary": {
            **dict(summary),
            "ready_group_count": ready_count,
            "blocked_group_count": blocked_count,
            "skipped_group_count": skipped_count,
        },
        "groups": group_previews,
        "problems": result_payload.get("problems", []),
        "next_action": (
            "Apply the reviewed people workflow."
            if dry_result.status == "ok" and blocked_count == 0 and ready_count > 0
            else "Fix blocked groups or missing encodings before applying the people workflow."
        ),
        "privacy_notice": "This preview can reveal who appears in local files and may reference sensitive biometric metadata.",
    }


def write_people_review_apply_preview(path: str | Path, payload: Mapping[str, Any]) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(dict(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


__all__ = [
    "AUDIT_KIND",
    "AUDIT_SCHEMA_VERSION",
    "build_people_review_apply_preview",
    "write_people_review_apply_preview",
]
