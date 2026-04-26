from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable

SCHEMA_VERSION = "1.0"


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(slots=True, frozen=True)
class GuiPageContract:
    page_id: str
    title: str
    description: str
    route: str
    primary_command: str | None = None
    risk_level: str = "safe"
    status: str = "ready"
    required_artifacts: tuple[str, ...] = ()
    optional_artifacts: tuple[str, ...] = ()
    recommended_actions: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "page_id": self.page_id,
            "title": self.title,
            "description": self.description,
            "route": self.route,
            "primary_command": self.primary_command,
            "risk_level": self.risk_level,
            "status": self.status,
            "required_artifacts": list(self.required_artifacts),
            "optional_artifacts": list(self.optional_artifacts),
            "recommended_actions": list(self.recommended_actions),
        }


_PAGE_CONTRACTS: tuple[GuiPageContract, ...] = (
    GuiPageContract(
        page_id="dashboard",
        title="Dashboard",
        description="Entry point for recent runs, saved profiles, and next actions.",
        route="/",
        optional_artifacts=("service_home_state.json", "app_manifest.json"),
        recommended_actions=("open_recent_run", "start_profile", "run_doctor"),
    ),
    GuiPageContract(
        page_id="new-run",
        title="New Run",
        description="Create organize, rename, duplicate, cleanup, or people workflows from profiles.",
        route="/new-run",
        primary_command="app profiles",
        risk_level="medium",
        optional_artifacts=("profile.json", "app_manifest.json"),
        recommended_actions=("create_profile", "render_profile", "run_preview"),
    ),
    GuiPageContract(
        page_id="run-history",
        title="Run History",
        description="Browse and validate structured run artifact folders.",
        route="/runs",
        primary_command="runs",
        optional_artifacts=("command.json", "report.json", "summary.txt"),
        recommended_actions=("open_report", "validate_run_artifacts"),
    ),
    GuiPageContract(
        page_id="people-review",
        title="People Review",
        description="Review detected people groups, accept or reject faces, and prepare catalog updates.",
        route="/people/review",
        primary_command="people review-bundle",
        risk_level="sensitive",
        required_artifacts=("bundle_manifest.json", "people_review_workflow.json", "people_review_workspace.json"),
        optional_artifacts=("assets/people_review_assets.json", "assets/faces/*.jpg", "people_report.json"),
        recommended_actions=("review_groups", "apply_review", "rerun_scan_after_apply"),
    ),
    GuiPageContract(
        page_id="people-catalog",
        title="People Catalog",
        description="Inspect local named-person catalog metadata and privacy-sensitive face embeddings.",
        route="/people/catalog",
        primary_command="people catalog-list",
        risk_level="sensitive",
        optional_artifacts=("people.json",),
        recommended_actions=("open_catalog", "run_people_scan"),
    ),
    GuiPageContract(
        page_id="profiles",
        title="Saved Profiles",
        description="Manage GUI-friendly preset JSON files.",
        route="/profiles",
        primary_command="app profiles",
        optional_artifacts=("*.json",),
        recommended_actions=("create_profile", "validate_profile", "render_profile"),
    ),
    GuiPageContract(
        page_id="settings-doctor",
        title="Settings & Doctor",
        description="Validate paths, filters, output locations, and environment assumptions.",
        route="/settings/doctor",
        primary_command="doctor",
        optional_artifacts=("doctor_report.json",),
        recommended_actions=("run_doctor", "fix_diagnostics"),
    ),
)


def list_gui_page_contracts() -> list[GuiPageContract]:
    return list(_PAGE_CONTRACTS)


def build_gui_page_catalog() -> dict[str, object]:
    pages = [page.to_dict() for page in _PAGE_CONTRACTS]
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": _now_utc(),
        "kind": "gui_page_catalog",
        "page_count": len(pages),
        "pages": pages,
        "privacy_notice": "Pages that expose people recognition data should treat local catalogs, reports, and face crops as sensitive biometric metadata.",
    }


def validate_gui_page_id(page_id: str) -> bool:
    return any(page.page_id == page_id for page in _PAGE_CONTRACTS)


def build_gui_navigation_state(active_page_id: str = "dashboard") -> dict[str, object]:
    active = active_page_id if validate_gui_page_id(active_page_id) else "dashboard"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": _now_utc(),
        "kind": "gui_navigation_state",
        "active_page_id": active,
        "items": [
            {
                "page_id": page.page_id,
                "title": page.title,
                "route": page.route,
                "risk_level": page.risk_level,
                "active": page.page_id == active,
            }
            for page in _PAGE_CONTRACTS
        ],
    }


def page_ids_for_commands(commands: Iterable[str]) -> list[str]:
    command_set = {str(command).strip().lower() for command in commands if str(command).strip()}
    page_ids: list[str] = []
    for page in _PAGE_CONTRACTS:
        primary = (page.primary_command or "").split(" ", 1)[0]
        if primary and primary in command_set:
            page_ids.append(page.page_id)
    return page_ids


__all__ = [
    "GuiPageContract",
    "SCHEMA_VERSION",
    "build_gui_navigation_state",
    "build_gui_page_catalog",
    "list_gui_page_contracts",
    "page_ids_for_commands",
    "validate_gui_page_id",
]
