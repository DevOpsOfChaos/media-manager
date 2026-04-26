from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .people_review_bundle import (
    DEFAULT_ASSET_DIR,
    DEFAULT_ASSET_MANIFEST_FILE,
    DEFAULT_MANIFEST_FILE,
    DEFAULT_REPORT_FILE,
    DEFAULT_WORKFLOW_FILE,
    DEFAULT_WORKSPACE_FILE,
    write_people_review_bundle,
)
from .people_review_session import (
    build_people_review_session_state,
    load_people_review_workflow,
    merge_people_groups,
    set_people_face_decision,
    set_people_group_decision,
    split_people_group,
    summarize_people_review_workflow,
    write_people_review_workflow_session,
)
from .people_review_ui import build_people_review_workspace
from .report_export import write_json_report

SERVICE_SCHEMA_VERSION = 1
SERVICE_KIND = "people_review_service"


@dataclass(slots=True, frozen=True)
class PeopleReviewBundlePaths:
    bundle_dir: Path
    manifest_path: Path
    report_path: Path
    workflow_path: Path
    workspace_path: Path
    asset_manifest_path: Path
    summary_path: Path

    def to_dict(self) -> dict[str, str]:
        return {
            "bundle_dir": str(self.bundle_dir),
            "manifest_path": str(self.manifest_path),
            "report_path": str(self.report_path),
            "workflow_path": str(self.workflow_path),
            "workspace_path": str(self.workspace_path),
            "asset_manifest_path": str(self.asset_manifest_path),
            "summary_path": str(self.summary_path),
        }


def _read_json_object(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return payload


def _as_mapping(value: object) -> Mapping[str, object]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def _as_text(value: object) -> str:
    return value if isinstance(value, str) else ""


def resolve_people_review_bundle_paths(bundle_dir: str | Path) -> PeopleReviewBundlePaths:
    root = Path(bundle_dir)
    return PeopleReviewBundlePaths(
        bundle_dir=root,
        manifest_path=root / DEFAULT_MANIFEST_FILE,
        report_path=root / DEFAULT_REPORT_FILE,
        workflow_path=root / DEFAULT_WORKFLOW_FILE,
        workspace_path=root / DEFAULT_WORKSPACE_FILE,
        asset_manifest_path=root / DEFAULT_ASSET_DIR / DEFAULT_ASSET_MANIFEST_FILE,
        summary_path=root / "summary.txt",
    )


def load_people_review_bundle(bundle_dir: str | Path) -> dict[str, object]:
    """Load the GUI-facing people review bundle into one service payload."""
    paths = resolve_people_review_bundle_paths(bundle_dir)
    manifest = _read_json_object(paths.manifest_path) if paths.manifest_path.exists() else {}
    report = _read_json_object(paths.report_path) if paths.report_path.exists() else {}
    workflow = load_people_review_workflow(paths.workflow_path) if paths.workflow_path.exists() else {"groups": []}
    workspace = _read_json_object(paths.workspace_path) if paths.workspace_path.exists() else build_people_review_workspace(report_payload=report, workflow_payload=workflow)
    assets = _read_json_object(paths.asset_manifest_path) if paths.asset_manifest_path.exists() else {}
    session = build_people_review_session_state(workflow)
    return {
        "schema_version": SERVICE_SCHEMA_VERSION,
        "service": SERVICE_KIND,
        "bundle_paths": paths.to_dict(),
        "manifest": manifest,
        "report": report,
        "workflow": workflow,
        "workspace": workspace,
        "assets": assets,
        "session": session,
        "privacy_notice": "People review service payloads can contain local face metadata and sensitive biometric references. Keep them local/private.",
    }


def build_people_review_service_state(bundle_dir: str | Path) -> dict[str, object]:
    """Build a compact state payload suitable for a future GUI controller."""
    bundle = load_people_review_bundle(bundle_dir)
    manifest = _as_mapping(bundle.get("manifest"))
    workflow = _as_mapping(bundle.get("workflow"))
    workspace = _as_mapping(bundle.get("workspace"))
    assets = _as_mapping(bundle.get("assets"))
    session = _as_mapping(bundle.get("session"))
    workspace_overview = _as_mapping(workspace.get("overview"))
    asset_summary = _as_mapping(assets.get("summary"))
    session_summary = _as_mapping(session.get("summary"))
    return {
        "schema_version": SERVICE_SCHEMA_VERSION,
        "service": SERVICE_KIND,
        "bundle_dir": str(bundle_dir),
        "status": "ok",
        "summary": {
            "group_count": session_summary.get("group_count", workspace_overview.get("group_count", 0)),
            "face_count": session_summary.get("face_count", workspace_overview.get("face_count", 0)),
            "ready_group_count": session_summary.get("ready_group_count", workspace_overview.get("ready_group_count", 0)),
            "needs_name_group_count": session_summary.get("needs_name_group_count", workspace_overview.get("needs_name_group_count", 0)),
            "rejected_faces": session_summary.get("rejected_faces", workspace_overview.get("excluded_faces", 0)),
            "asset_count": asset_summary.get("asset_count", 0),
            "asset_error_count": asset_summary.get("error_count", 0),
            "contains_sensitive_biometric_metadata": bool(manifest.get("contains_sensitive_biometric_metadata")),
        },
        "suggested_actions": [
            {
                "id": "continue_review",
                "label": "Continue people review",
                "enabled": True,
            },
            {
                "id": "apply_ready_groups",
                "label": "Apply ready groups to catalog",
                "enabled": int(session_summary.get("ready_group_count", 0) or 0) > 0,
            },
            {
                "id": "rebuild_workspace",
                "label": "Rebuild GUI workspace from workflow",
                "enabled": True,
            },
        ],
        "workflow_summary": summarize_people_review_workflow(workflow),
        "paths": bundle.get("bundle_paths", {}),
    }


def save_people_review_workflow_for_bundle(bundle_dir: str | Path, workflow_payload: Mapping[str, object]) -> dict[str, object]:
    paths = resolve_people_review_bundle_paths(bundle_dir)
    write_people_review_workflow_session(paths.workflow_path, workflow_payload)
    return rebuild_people_review_workspace_for_bundle(bundle_dir)


def rebuild_people_review_workspace_for_bundle(
    bundle_dir: str | Path,
    *,
    include_encodings: bool = False,
) -> dict[str, object]:
    """Rebuild people_review_workspace.json after workflow edits."""
    paths = resolve_people_review_bundle_paths(bundle_dir)
    report = _read_json_object(paths.report_path)
    workflow = load_people_review_workflow(paths.workflow_path)
    workspace = build_people_review_workspace(
        report_payload=report,
        workflow_payload=workflow,
        include_encodings=include_encodings,
    )
    write_json_report(paths.workspace_path, workspace)
    return {
        "schema_version": SERVICE_SCHEMA_VERSION,
        "service": SERVICE_KIND,
        "operation": "rebuild-workspace",
        "status": "ok",
        "workspace": workspace,
        "session": build_people_review_session_state(workflow),
        "paths": paths.to_dict(),
    }


def update_people_review_group(
    bundle_dir: str | Path,
    *,
    group_id: str,
    apply_group: bool | None = None,
    selected_name: str | None = None,
    selected_person_id: str | None = None,
    review_note: str | None = None,
    rebuild_workspace: bool = True,
) -> dict[str, object]:
    paths = resolve_people_review_bundle_paths(bundle_dir)
    workflow = load_people_review_workflow(paths.workflow_path)
    result = set_people_group_decision(
        workflow,
        group_id=group_id,
        apply_group=apply_group,
        selected_name=selected_name,
        selected_person_id=selected_person_id,
        review_note=review_note,
    )
    if result.changed:
        write_people_review_workflow_session(paths.workflow_path, result.workflow_payload)
    payload = result.to_dict()
    payload["paths"] = paths.to_dict()
    if rebuild_workspace and result.changed:
        payload["rebuild"] = rebuild_people_review_workspace_for_bundle(bundle_dir)
    return payload


def update_people_review_face(
    bundle_dir: str | Path,
    *,
    face_id: str,
    include: bool | None = None,
    note: str | None = None,
    rebuild_workspace: bool = True,
) -> dict[str, object]:
    paths = resolve_people_review_bundle_paths(bundle_dir)
    workflow = load_people_review_workflow(paths.workflow_path)
    result = set_people_face_decision(workflow, face_id=face_id, include=include, note=note)
    if result.changed:
        write_people_review_workflow_session(paths.workflow_path, result.workflow_payload)
    payload = result.to_dict()
    payload["paths"] = paths.to_dict()
    if rebuild_workspace and result.changed:
        payload["rebuild"] = rebuild_people_review_workspace_for_bundle(bundle_dir)
    return payload


def split_people_review_group(
    bundle_dir: str | Path,
    *,
    group_id: str,
    face_ids: Iterable[str],
    new_group_id: str | None = None,
    selected_name: str = "",
    rebuild_workspace: bool = True,
) -> dict[str, object]:
    paths = resolve_people_review_bundle_paths(bundle_dir)
    workflow = load_people_review_workflow(paths.workflow_path)
    result = split_people_group(
        workflow,
        group_id=group_id,
        face_ids=face_ids,
        new_group_id=new_group_id,
        selected_name=selected_name,
    )
    if result.changed:
        write_people_review_workflow_session(paths.workflow_path, result.workflow_payload)
    payload = result.to_dict()
    payload["paths"] = paths.to_dict()
    if rebuild_workspace and result.changed:
        payload["rebuild"] = rebuild_people_review_workspace_for_bundle(bundle_dir)
    return payload


def merge_people_review_groups(
    bundle_dir: str | Path,
    *,
    group_ids: Iterable[str],
    target_group_id: str | None = None,
    selected_name: str | None = None,
    rebuild_workspace: bool = True,
) -> dict[str, object]:
    paths = resolve_people_review_bundle_paths(bundle_dir)
    workflow = load_people_review_workflow(paths.workflow_path)
    result = merge_people_groups(
        workflow,
        group_ids=group_ids,
        target_group_id=target_group_id,
        selected_name=selected_name,
    )
    if result.changed:
        write_people_review_workflow_session(paths.workflow_path, result.workflow_payload)
    payload = result.to_dict()
    payload["paths"] = paths.to_dict()
    if rebuild_workspace and result.changed:
        payload["rebuild"] = rebuild_people_review_workspace_for_bundle(bundle_dir)
    return payload


def create_people_review_bundle_from_report(
    *,
    report_payload: Mapping[str, object],
    bundle_dir: str | Path,
    workflow_payload: Mapping[str, object] | None = None,
    catalog_path: str | Path | None = None,
    include_assets: bool = True,
) -> dict[str, object]:
    """Service-layer wrapper used by future GUI code to create a review bundle."""
    manifest = write_people_review_bundle(
        report_payload=report_payload,
        workflow_payload=workflow_payload,
        bundle_dir=bundle_dir,
        catalog_path=catalog_path,
        include_assets=include_assets,
    )
    return {
        "schema_version": SERVICE_SCHEMA_VERSION,
        "service": SERVICE_KIND,
        "operation": "create-bundle",
        "status": "ok",
        "manifest": manifest,
        "state": build_people_review_service_state(bundle_dir),
    }


__all__ = [
    "SERVICE_KIND",
    "SERVICE_SCHEMA_VERSION",
    "PeopleReviewBundlePaths",
    "build_people_review_service_state",
    "create_people_review_bundle_from_report",
    "load_people_review_bundle",
    "merge_people_review_groups",
    "rebuild_people_review_workspace_for_bundle",
    "resolve_people_review_bundle_paths",
    "save_people_review_workflow_for_bundle",
    "split_people_review_group",
    "update_people_review_face",
    "update_people_review_group",
]
