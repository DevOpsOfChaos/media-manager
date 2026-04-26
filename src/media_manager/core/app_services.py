from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .action_model import build_action_model_from_report
from .app_manifest import build_app_manifest
from .app_profiles import scan_app_profiles, summarize_app_profiles
from .gui_page_contracts import build_gui_navigation_state, build_gui_page_catalog
from .plan_snapshot import build_plan_snapshot_from_report
from .app_manifest import build_ui_state_from_report

SERVICE_SCHEMA_VERSION = "1.0"


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json_object(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def write_json_object(path: str | Path, payload: Mapping[str, Any]) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(dict(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_int(value: Any) -> int:
    return value if isinstance(value, int) else 0


def discover_run_summaries(run_dir: str | Path | None, *, limit: int = 20) -> list[dict[str, object]]:
    if run_dir is None:
        return []
    root = Path(run_dir)
    if not root.exists() or not root.is_dir():
        return []
    records: list[dict[str, object]] = []
    for item in sorted((path for path in root.iterdir() if path.is_dir()), key=lambda path: path.name.lower(), reverse=True):
        command_path = item / "command.json"
        report_path = item / "report.json"
        summary_path = item / "summary.txt"
        command_payload: Mapping[str, Any] = {}
        report_payload: Mapping[str, Any] = {}
        try:
            if command_path.exists():
                command_payload = read_json_object(command_path)
            if report_path.exists():
                report_payload = read_json_object(report_path)
        except (OSError, ValueError, json.JSONDecodeError):
            command_payload = {}
            report_payload = {}
        outcome = _as_mapping(report_payload.get("outcome_report"))
        review = _as_mapping(report_payload.get("review"))
        records.append(
            {
                "run_id": item.name,
                "path": str(item),
                "command": command_payload.get("command") or report_payload.get("command"),
                "mode": "apply" if command_payload.get("apply_requested") is True else "preview" if command_payload.get("apply_requested") is False else None,
                "exit_code": command_payload.get("exit_code"),
                "created_at_utc": command_payload.get("created_at_utc"),
                "status": outcome.get("status"),
                "next_action": outcome.get("next_action"),
                "review_candidate_count": _as_int(review.get("candidate_count")),
                "has_summary": summary_path.exists(),
                "has_ui_state": (item / "ui_state.json").exists(),
                "has_plan_snapshot": (item / "plan_snapshot.json").exists(),
                "has_action_model": (item / "action_model.json").exists(),
            }
        )
        if len(records) >= max(0, limit):
            break
    return records


def build_report_service_bundle(
    *,
    command_name: str,
    report_payload: Mapping[str, Any],
    command_payload: Mapping[str, Any] | None = None,
    run_id: str | None = None,
    entry_limit: int = 200,
) -> dict[str, object]:
    """Build all GUI-facing derived artifacts for a report in one service call."""
    ui_state = build_ui_state_from_report(
        command_name=command_name,
        report_payload=report_payload,
        command_payload=command_payload,
        run_id=run_id,
    )
    plan_snapshot = build_plan_snapshot_from_report(
        command_name=command_name,
        report_payload=report_payload,
        run_id=run_id,
        entry_limit=entry_limit,
    )
    action_model = build_action_model_from_report(
        command_name=command_name,
        report_payload=report_payload,
        command_payload=command_payload,
        run_id=run_id,
    )
    return {
        "schema_version": SERVICE_SCHEMA_VERSION,
        "generated_at_utc": _now_utc(),
        "kind": "report_service_bundle",
        "command": command_name,
        "run_id": run_id,
        "ui_state": ui_state,
        "plan_snapshot": plan_snapshot,
        "action_model": action_model,
        "artifact_names": ["ui_state.json", "plan_snapshot.json", "action_model.json", "service_bundle.json"],
    }


def write_report_service_bundle(
    out_dir: str | Path,
    *,
    command_name: str,
    report_payload: Mapping[str, Any],
    command_payload: Mapping[str, Any] | None = None,
    run_id: str | None = None,
    entry_limit: int = 200,
) -> dict[str, object]:
    bundle = build_report_service_bundle(
        command_name=command_name,
        report_payload=report_payload,
        command_payload=command_payload,
        run_id=run_id,
        entry_limit=entry_limit,
    )
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    write_json_object(root / "ui_state.json", _as_mapping(bundle.get("ui_state")))
    write_json_object(root / "plan_snapshot.json", _as_mapping(bundle.get("plan_snapshot")))
    write_json_object(root / "action_model.json", _as_mapping(bundle.get("action_model")))
    write_json_object(root / "service_bundle.json", bundle)
    return {
        **bundle,
        "service_dir": str(root),
        "written_files": [
            str(root / "ui_state.json"),
            str(root / "plan_snapshot.json"),
            str(root / "action_model.json"),
            str(root / "service_bundle.json"),
        ],
    }


def load_people_review_bundle_summary(bundle_dir: str | Path | None) -> dict[str, object] | None:
    if bundle_dir is None:
        return None
    root = Path(bundle_dir)
    manifest_path = root / "bundle_manifest.json"
    if not manifest_path.exists():
        return None
    try:
        manifest = read_json_object(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    summary = _as_mapping(manifest.get("summary"))
    artifacts = _as_mapping(manifest.get("artifacts"))
    return {
        "bundle_dir": str(root),
        "manifest_path": str(manifest_path),
        "status": manifest.get("status"),
        "summary": dict(summary),
        "artifacts": dict(artifacts),
        "ready_for_gui": bool((root / "people_review_workspace.json").exists()),
        "has_assets": (root / "assets" / "people_review_assets.json").exists(),
    }


def build_app_home_state(
    *,
    profile_dir: str | Path | None = None,
    run_dir: str | Path | None = None,
    people_bundle_dir: str | Path | None = None,
    active_page_id: str = "dashboard",
    run_limit: int = 10,
) -> dict[str, object]:
    profile_records = scan_app_profiles(profile_dir) if profile_dir is not None else []
    run_summaries = discover_run_summaries(run_dir, limit=run_limit)
    people_bundle = load_people_review_bundle_summary(people_bundle_dir)
    manifest = build_app_manifest()
    return {
        "schema_version": SERVICE_SCHEMA_VERSION,
        "generated_at_utc": _now_utc(),
        "kind": "app_home_state",
        "active_page_id": active_page_id,
        "manifest_summary": {
            "schema_version": manifest.get("schema_version"),
            "command_count": len(manifest.get("commands", [])) if isinstance(manifest.get("commands"), list) else 0,
            "entrypoints": manifest.get("entrypoints", {}),
        },
        "navigation": build_gui_navigation_state(active_page_id),
        "pages": build_gui_page_catalog(),
        "profiles": {
            "profile_dir": str(profile_dir) if profile_dir is not None else None,
            "summary": summarize_app_profiles(profile_records),
            "items": [record.to_dict() for record in profile_records[:25]],
        },
        "runs": {
            "run_dir": str(run_dir) if run_dir is not None else None,
            "summary": {
                "run_count": len(run_summaries),
                "error_count": sum(1 for run in run_summaries if run.get("exit_code") not in (None, 0)),
            },
            "items": run_summaries,
        },
        "people_review": people_bundle,
        "suggested_next_step": (
            "Open the people review page."
            if people_bundle is not None and people_bundle.get("ready_for_gui")
            else "Create or open a profile, then run a preview."
        ),
    }


__all__ = [
    "SERVICE_SCHEMA_VERSION",
    "build_app_home_state",
    "build_report_service_bundle",
    "discover_run_summaries",
    "load_people_review_bundle_summary",
    "read_json_object",
    "write_json_object",
    "write_report_service_bundle",
]
