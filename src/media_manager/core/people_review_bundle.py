from __future__ import annotations

from collections.abc import Mapping
import json
from pathlib import Path
from typing import Any

from .people_review_assets import build_people_review_assets, write_people_review_asset_manifest
from .people_review_ui import build_people_review_workspace, build_people_review_workspace_summary_text
from .people_review_workflow import build_people_review_workflow, write_people_review_workflow

BUNDLE_SCHEMA_VERSION = 1
BUNDLE_KIND = "people_review_bundle"
DEFAULT_REPORT_FILE = "people_report.json"
DEFAULT_WORKFLOW_FILE = "people_review_workflow.json"
DEFAULT_WORKSPACE_FILE = "people_review_workspace.json"
DEFAULT_ASSET_DIR = "assets"
DEFAULT_ASSET_MANIFEST_FILE = "people_review_assets.json"
DEFAULT_SUMMARY_FILE = "summary.txt"
DEFAULT_MANIFEST_FILE = "bundle_manifest.json"


def _as_mapping(value: object) -> Mapping[str, object]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def _as_text(value: object) -> str:
    return value if isinstance(value, str) else ""


def _write_json(path: Path, payload: Mapping[str, object]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def _write_text(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _relative_path(root: Path, path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _asset_by_face_id(asset_payload: Mapping[str, object] | None) -> dict[str, Mapping[str, object]]:
    if asset_payload is None:
        return {}
    result: dict[str, Mapping[str, object]] = {}
    for item in _as_list(asset_payload.get("assets")):
        if not isinstance(item, Mapping):
            continue
        face_id = _as_text(item.get("face_id"))
        if face_id:
            result[face_id] = item
    return result


def _attach_assets_to_workspace(
    workspace_payload: Mapping[str, object],
    *,
    asset_payload: Mapping[str, object] | None,
    bundle_dir: Path,
) -> dict[str, object]:
    """Return a workspace copy with asset metadata attached to face cards."""
    workspace = json.loads(json.dumps(dict(workspace_payload), ensure_ascii=False))
    assets_by_face = _asset_by_face_id(asset_payload)
    attached_count = 0
    missing_count = 0

    for group in _as_list(workspace.get("groups")):
        if not isinstance(group, dict):
            continue
        for face in _as_list(group.get("faces")):
            if not isinstance(face, dict):
                continue
            face_id = _as_text(face.get("face_id"))
            asset = assets_by_face.get(face_id)
            if asset is None:
                missing_count += 1
                face["asset_status"] = "missing"
                continue
            asset_path = Path(_as_text(asset.get("asset_path"))) if _as_text(asset.get("asset_path")) else None
            face["asset_status"] = asset.get("status")
            face["asset_error"] = asset.get("error")
            face["asset_path"] = asset.get("asset_path")
            face["asset_relative_path"] = _relative_path(bundle_dir, asset_path) if asset_path else asset.get("asset_relative_path")
            face["asset_uri"] = asset.get("image_uri")
            face["crop_box"] = asset.get("crop_box")
            face["asset_size"] = asset.get("asset_size")
            if asset.get("status") in {"ok", "exists"}:
                attached_count += 1

    overview = workspace.setdefault("overview", {})
    if isinstance(overview, dict):
        overview["face_assets_attached"] = attached_count
        overview["face_assets_missing"] = missing_count
        overview["has_face_assets"] = attached_count > 0
    workspace["asset_manifest"] = {
        "kind": asset_payload.get("kind") if isinstance(asset_payload, Mapping) else None,
        "asset_dir": asset_payload.get("asset_dir") if isinstance(asset_payload, Mapping) else None,
        "summary": asset_payload.get("summary") if isinstance(asset_payload, Mapping) else {},
    }
    return workspace


def _copy_report_for_bundle(report_payload: Mapping[str, object]) -> dict[str, object]:
    # Keep the report exact enough for review-apply. Encodings may be present;
    # the bundle manifest marks this as sensitive biometric metadata.
    return json.loads(json.dumps(dict(report_payload), ensure_ascii=False))


def build_people_review_bundle_manifest(
    *,
    bundle_dir: Path,
    report_payload: Mapping[str, object],
    workflow_payload: Mapping[str, object],
    workspace_payload: Mapping[str, object],
    asset_payload: Mapping[str, object] | None,
    paths: Mapping[str, Path | None],
    source_report_path: str | Path | None = None,
    source_workflow_path: str | Path | None = None,
    catalog_path: str | Path | None = None,
) -> dict[str, object]:
    report_summary = _as_mapping(report_payload.get("summary"))
    workspace_overview = _as_mapping(workspace_payload.get("overview"))
    asset_summary = _as_mapping(asset_payload.get("summary")) if asset_payload is not None else {}
    has_encodings = any(
        isinstance(item, Mapping) and isinstance(item.get("encoding"), list) and bool(item.get("encoding"))
        for item in _as_list(report_payload.get("detections"))
    )

    return {
        "schema_version": BUNDLE_SCHEMA_VERSION,
        "kind": BUNDLE_KIND,
        "bundle_dir": bundle_dir.as_posix(),
        "source_report_path": str(source_report_path) if source_report_path is not None else None,
        "source_workflow_path": str(source_workflow_path) if source_workflow_path is not None else None,
        "catalog_path": str(catalog_path) if catalog_path is not None else None,
        "contains_sensitive_biometric_metadata": bool(has_encodings),
        "files": {
            key: _relative_path(bundle_dir, path) if isinstance(path, Path) else None
            for key, path in paths.items()
        },
        "summary": {
            "backend": report_payload.get("backend"),
            "source_face_count": report_summary.get("face_count", 0),
            "source_unknown_faces": report_summary.get("unknown_faces", 0),
            "group_count": workspace_overview.get("group_count", 0),
            "workspace_face_count": workspace_overview.get("face_count", 0),
            "ready_group_count": workspace_overview.get("ready_group_count", 0),
            "needs_name_group_count": workspace_overview.get("needs_name_group_count", 0),
            "needs_review_group_count": workspace_overview.get("needs_review_group_count", 0),
            "asset_count": asset_summary.get("asset_count", 0),
            "asset_error_count": asset_summary.get("error_count", 0),
            "has_report_encodings": has_encodings,
        },
        "suggested_actions": [
            {
                "id": "open_people_review_page",
                "label": "Open people review page",
                "enabled": True,
                "target_file": _relative_path(bundle_dir, paths.get("workspace")),
            },
            {
                "id": "edit_workflow",
                "label": "Edit/curate people review decisions",
                "enabled": True,
                "target_file": _relative_path(bundle_dir, paths.get("workflow")),
            },
            {
                "id": "apply_review",
                "label": "Apply reviewed people to catalog",
                "enabled": has_encodings,
                "target_file": _relative_path(bundle_dir, paths.get("workflow")),
            },
            {
                "id": "rerun_scan_with_encodings",
                "label": "Rerun scan with encodings",
                "enabled": not has_encodings,
                "reason": "review-apply needs a report created with --include-encodings.",
            },
        ],
        "gui_contract": {
            "default_page": "people-review",
            "workspace_file": _relative_path(bundle_dir, paths.get("workspace")),
            "asset_manifest_file": _relative_path(bundle_dir, paths.get("assets")),
            "workflow_file": _relative_path(bundle_dir, paths.get("workflow")),
            "summary_file": _relative_path(bundle_dir, paths.get("summary")),
            "review_fields": ["groups[].apply_group", "groups[].selected_name", "groups[].selected_person_id", "groups[].faces[].include", "groups[].faces[].note"],
        },
        "privacy_notice": (
            "This bundle can reveal who appears in which local files. Reports with encodings and catalogs contain "
            "sensitive biometric metadata. Keep the bundle local/private."
        ),
    }


def build_people_review_bundle_summary_text(manifest_payload: Mapping[str, object]) -> str:
    summary = _as_mapping(manifest_payload.get("summary"))
    files = _as_mapping(manifest_payload.get("files"))
    return "\n".join(
        [
            "People review bundle",
            f"  Bundle dir: {manifest_payload.get('bundle_dir')}",
            f"  Groups: {summary.get('group_count', 0)}",
            f"  Faces: {summary.get('workspace_face_count', 0)}",
            f"  Ready groups: {summary.get('ready_group_count', 0)}",
            f"  Needs name: {summary.get('needs_name_group_count', 0)}",
            f"  Needs review: {summary.get('needs_review_group_count', 0)}",
            f"  Assets: {summary.get('asset_count', 0)}",
            f"  Asset errors: {summary.get('asset_error_count', 0)}",
            f"  Has report encodings: {summary.get('has_report_encodings', False)}",
            "",
            "Files",
            f"  Manifest: {files.get('manifest')}",
            f"  Workspace: {files.get('workspace')}",
            f"  Workflow: {files.get('workflow')}",
            f"  Assets: {files.get('assets')}",
            f"  Report: {files.get('report')}",
        ]
    ) + "\n"


def write_people_review_bundle(
    *,
    report_payload: Mapping[str, object],
    bundle_dir: str | Path,
    workflow_payload: Mapping[str, object] | None = None,
    source_report_path: str | Path | None = None,
    source_workflow_path: str | Path | None = None,
    catalog_path: str | Path | None = None,
    include_assets: bool = True,
    include_encodings_in_workspace: bool = False,
    crop_padding_ratio: float = 0.25,
    thumbnail_size: int = 256,
    quality: int = 90,
    overwrite_assets: bool = True,
) -> dict[str, object]:
    """Write a complete GUI-ready people review bundle directory."""

    resolved_bundle_dir = Path(bundle_dir)
    resolved_bundle_dir.mkdir(parents=True, exist_ok=True)

    workflow = dict(workflow_payload) if workflow_payload is not None else build_people_review_workflow(report_payload)
    asset_payload: dict[str, object] | None = None
    asset_manifest_path: Path | None = None

    if include_assets:
        asset_manifest_path = resolved_bundle_dir / DEFAULT_ASSET_DIR / DEFAULT_ASSET_MANIFEST_FILE
        asset_payload = build_people_review_assets(
            report_payload=report_payload,
            workflow_payload=workflow,
            asset_dir=resolved_bundle_dir / DEFAULT_ASSET_DIR,
            crop_padding_ratio=crop_padding_ratio,
            thumbnail_size=thumbnail_size,
            quality=quality,
            overwrite=overwrite_assets,
        )
        write_people_review_asset_manifest(asset_manifest_path, asset_payload)

    workspace = build_people_review_workspace(
        report_payload=report_payload,
        workflow_payload=workflow,
        include_encodings=include_encodings_in_workspace,
    )
    if asset_payload is not None:
        workspace = _attach_assets_to_workspace(workspace, asset_payload=asset_payload, bundle_dir=resolved_bundle_dir)

    report_path = resolved_bundle_dir / DEFAULT_REPORT_FILE
    workflow_path = resolved_bundle_dir / DEFAULT_WORKFLOW_FILE
    workspace_path = resolved_bundle_dir / DEFAULT_WORKSPACE_FILE
    summary_path = resolved_bundle_dir / DEFAULT_SUMMARY_FILE
    manifest_path = resolved_bundle_dir / DEFAULT_MANIFEST_FILE

    _write_json(report_path, _copy_report_for_bundle(report_payload))
    write_people_review_workflow(workflow_path, workflow)
    _write_json(workspace_path, workspace)

    paths: dict[str, Path | None] = {
        "manifest": manifest_path,
        "report": report_path,
        "workflow": workflow_path,
        "workspace": workspace_path,
        "assets": asset_manifest_path,
        "summary": summary_path,
    }
    manifest = build_people_review_bundle_manifest(
        bundle_dir=resolved_bundle_dir,
        report_payload=report_payload,
        workflow_payload=workflow,
        workspace_payload=workspace,
        asset_payload=asset_payload,
        paths=paths,
        source_report_path=source_report_path,
        source_workflow_path=source_workflow_path,
        catalog_path=catalog_path,
    )
    _write_json(manifest_path, manifest)
    _write_text(summary_path, build_people_review_bundle_summary_text(manifest))
    return manifest


__all__ = [
    "BUNDLE_KIND",
    "BUNDLE_SCHEMA_VERSION",
    "DEFAULT_MANIFEST_FILE",
    "build_people_review_bundle_manifest",
    "build_people_review_bundle_summary_text",
    "write_people_review_bundle",
]
