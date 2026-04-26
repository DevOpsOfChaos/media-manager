from __future__ import annotations

from collections.abc import Mapping
import json
from pathlib import Path
from typing import Any

VALIDATOR_SCHEMA_VERSION = 1
REQUIRED_BUNDLE_FILES = (
    "bundle_manifest.json",
    "people_report.json",
    "people_review_workflow.json",
    "people_review_workspace.json",
    "summary.txt",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _diag(severity: str, code: str, message: str, *, path: str | None = None) -> dict[str, object]:
    payload: dict[str, object] = {"severity": severity, "code": code, "message": message}
    if path is not None:
        payload["path"] = path
    return payload


def _read_json(path: Path) -> dict[str, Any] | None:
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else None


def validate_people_review_bundle(bundle_dir: str | Path) -> dict[str, object]:
    """Validate a GUI-ready people review bundle directory without modifying it."""
    root = Path(bundle_dir)
    diagnostics: list[dict[str, object]] = []
    if not root.exists():
        diagnostics.append(_diag("error", "bundle_dir_missing", "Bundle directory does not exist.", path=str(root)))
        return _result(root, diagnostics, manifest=None, asset_manifest=None)
    if not root.is_dir():
        diagnostics.append(_diag("error", "bundle_dir_not_directory", "Bundle path is not a directory.", path=str(root)))
        return _result(root, diagnostics, manifest=None, asset_manifest=None)

    for relative in REQUIRED_BUNDLE_FILES:
        path = root / relative
        if not path.exists():
            diagnostics.append(_diag("error", "required_file_missing", f"Required bundle file is missing: {relative}", path=str(path)))

    manifest: dict[str, Any] | None = None
    manifest_path = root / "bundle_manifest.json"
    if manifest_path.exists():
        try:
            manifest = _read_json(manifest_path)
            if manifest is None:
                diagnostics.append(_diag("error", "invalid_manifest_json", "Bundle manifest must be a JSON object.", path=str(manifest_path)))
        except (OSError, json.JSONDecodeError) as exc:
            diagnostics.append(_diag("error", "manifest_read_error", str(exc), path=str(manifest_path)))

    asset_manifest: dict[str, Any] | None = None
    asset_manifest_path = root / "assets" / "people_review_assets.json"
    if asset_manifest_path.exists():
        try:
            asset_manifest = _read_json(asset_manifest_path)
            if asset_manifest is None:
                diagnostics.append(_diag("error", "invalid_asset_manifest_json", "Asset manifest must be a JSON object.", path=str(asset_manifest_path)))
        except (OSError, json.JSONDecodeError) as exc:
            diagnostics.append(_diag("error", "asset_manifest_read_error", str(exc), path=str(asset_manifest_path)))
    else:
        diagnostics.append(_diag("warning", "asset_manifest_missing", "Face crop asset manifest is missing.", path=str(asset_manifest_path)))

    workspace_path = root / "people_review_workspace.json"
    if workspace_path.exists():
        try:
            workspace = _read_json(workspace_path) or {}
            if workspace.get("workspace") != "people_review_workspace":
                diagnostics.append(_diag("warning", "unexpected_workspace_kind", "Workspace kind is not people_review_workspace.", path=str(workspace_path)))
        except (OSError, json.JSONDecodeError) as exc:
            diagnostics.append(_diag("error", "workspace_read_error", str(exc), path=str(workspace_path)))

    if asset_manifest is not None:
        for asset in _as_list(asset_manifest.get("assets")):
            if not isinstance(asset, Mapping):
                continue
            if asset.get("status") not in {"ok", "exists"}:
                continue
            asset_path = asset.get("asset_path")
            if isinstance(asset_path, str) and asset_path:
                path = Path(asset_path)
                if not path.is_absolute():
                    path = root / asset_path
                if not path.exists():
                    diagnostics.append(_diag("error", "asset_file_missing", "Listed face crop asset is missing.", path=str(path)))

    return _result(root, diagnostics, manifest=manifest, asset_manifest=asset_manifest)


def _result(
    root: Path,
    diagnostics: list[dict[str, object]],
    *,
    manifest: Mapping[str, Any] | None,
    asset_manifest: Mapping[str, Any] | None,
) -> dict[str, object]:
    error_count = sum(1 for item in diagnostics if item.get("severity") == "error")
    warning_count = sum(1 for item in diagnostics if item.get("severity") == "warning")
    assets = _as_list(_as_mapping(asset_manifest).get("assets"))
    summary = _as_mapping(_as_mapping(manifest).get("summary"))
    return {
        "schema_version": VALIDATOR_SCHEMA_VERSION,
        "kind": "people_review_bundle_validation",
        "bundle_dir": str(root),
        "status": "ok" if error_count == 0 else "error",
        "ready_for_gui": error_count == 0 and (root / "people_review_workspace.json").exists(),
        "summary": {
            "error_count": error_count,
            "warning_count": warning_count,
            "diagnostic_count": len(diagnostics),
            "asset_count": len(assets),
            "manifest_status": manifest.get("status") if isinstance(manifest, Mapping) else None,
            "ready_group_count": summary.get("ready_group_count"),
        },
        "diagnostics": diagnostics,
        "next_action": "Open the people review bundle in the GUI." if error_count == 0 else "Fix missing or invalid bundle files before opening it in the GUI.",
    }


def write_people_review_bundle_validation(path: str | Path, payload: Mapping[str, Any]) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(dict(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


__all__ = [
    "REQUIRED_BUNDLE_FILES",
    "VALIDATOR_SCHEMA_VERSION",
    "validate_people_review_bundle",
    "write_people_review_bundle_validation",
]
