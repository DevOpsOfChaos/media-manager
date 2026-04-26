from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .app_profiles import load_app_profile, render_app_profile_command, validate_app_profile

COMMAND_PLAN_SCHEMA_VERSION = 1


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _quote_if_needed(value: str) -> str:
    return f'"{value}"' if any(ch.isspace() for ch in value) else value


def _preview(argv: list[str]) -> str:
    return " ".join(_quote_if_needed(part) for part in argv)


def build_command_plan(
    *,
    plan_id: str,
    title: str,
    argv: list[str],
    risk_level: str = "safe",
    requires_confirmation: bool = False,
    enabled: bool = True,
    blocked_reason: str | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    return {
        "schema_version": COMMAND_PLAN_SCHEMA_VERSION,
        "generated_at_utc": _now_utc(),
        "kind": "gui_command_plan",
        "plan_id": plan_id,
        "title": title,
        "enabled": enabled,
        "risk_level": risk_level,
        "requires_confirmation": requires_confirmation,
        "argv": list(argv),
        "command_preview": _preview(list(argv)),
        "blocked_reason": blocked_reason,
        "metadata": dict(metadata or {}),
        "execution_policy": {
            "execute_in_service_layer": False,
            "reason": "The GUI should show this plan and request confirmation; this helper never executes commands.",
        },
    }


def build_profile_command_plan(profile_path: str | Path) -> dict[str, object]:
    profile = load_app_profile(profile_path)
    validation = validate_app_profile(profile)
    argv = list(validation.command_argv)
    return build_command_plan(
        plan_id=f"profile:{validation.profile_id}",
        title=f"Run profile: {profile.get('title', validation.profile_id)}",
        argv=argv,
        risk_level="medium" if validation.command in {"organize", "rename"} else "high" if validation.command in {"duplicates", "cleanup", "people"} else "safe",
        requires_confirmation=validation.command in {"organize", "rename", "duplicates", "cleanup", "people"},
        enabled=validation.valid,
        blocked_reason=None if validation.valid else "; ".join(validation.problems),
        metadata={
            "profile_id": validation.profile_id,
            "command": validation.command,
            "warnings": list(validation.warnings),
            "source": str(profile_path),
            "profile_preview": render_app_profile_command(profile) if validation.valid else None,
        },
    )


def build_people_review_apply_command_plan(
    *,
    catalog_path: str | Path,
    workflow_json: str | Path,
    report_json: str | Path,
    out_catalog: str | Path | None = None,
    dry_run: bool = False,
) -> dict[str, object]:
    argv = [
        "media-manager",
        "people",
        "review-apply",
        "--catalog",
        str(catalog_path),
        "--workflow-json",
        str(workflow_json),
        "--report-json",
        str(report_json),
    ]
    if out_catalog is not None:
        argv.extend(["--out-catalog", str(out_catalog)])
    if dry_run:
        argv.append("--dry-run")
    return build_command_plan(
        plan_id="people:review-apply",
        title="Apply reviewed people to catalog",
        argv=argv,
        risk_level="high",
        requires_confirmation=not dry_run,
        metadata={
            "catalog_path": str(catalog_path),
            "workflow_json": str(workflow_json),
            "report_json": str(report_json),
            "out_catalog": str(out_catalog) if out_catalog is not None else None,
            "dry_run": dry_run,
        },
    )


def build_open_people_bundle_plan(bundle_dir: str | Path) -> dict[str, object]:
    bundle_path = Path(bundle_dir)
    argv = ["media-manager-app-services", "validate-people-bundle", "--bundle-dir", str(bundle_path)]
    return build_command_plan(
        plan_id="people:open-review-bundle",
        title="Open people review bundle",
        argv=argv,
        risk_level="safe",
        requires_confirmation=False,
        metadata={
            "bundle_dir": str(bundle_path),
            "manifest_path": str(bundle_path / "bundle_manifest.json"),
            "workspace_path": str(bundle_path / "people_review_workspace.json"),
            "asset_manifest_path": str(bundle_path / "assets" / "people_review_assets.json"),
        },
    )


def write_command_plan(path: str | Path, payload: Mapping[str, Any]) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(dict(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


__all__ = [
    "COMMAND_PLAN_SCHEMA_VERSION",
    "build_command_plan",
    "build_open_people_bundle_plan",
    "build_people_review_apply_command_plan",
    "build_profile_command_plan",
    "write_command_plan",
]
