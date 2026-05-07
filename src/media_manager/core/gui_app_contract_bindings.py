from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Any

from .app_contract_inventory import AppServiceContract, list_app_service_contracts
from .gui_page_contracts import list_gui_page_contracts

GUI_APP_CONTRACT_BINDINGS_SCHEMA_VERSION = "1.0"
GUI_APP_CONTRACT_BINDINGS_KIND = "gui_app_contract_bindings"


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True, slots=True)
class GuiSurfaceBinding:
    surface_id: str
    title: str
    surface_type: str
    page_id: str | None = None
    owner: str = "core"
    headless_testable: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "surface_id": self.surface_id,
            "title": self.title,
            "surface_type": self.surface_type,
            "page_id": self.page_id,
            "owner": self.owner,
            "headless_testable": self.headless_testable,
        }


_SURFACE_BINDINGS: tuple[GuiSurfaceBinding, ...] = (
    GuiSurfaceBinding("dashboard", "Dashboard", "page", page_id="dashboard"),
    GuiSurfaceBinding("new-run", "New Run", "page", page_id="new-run"),
    GuiSurfaceBinding("profiles", "Saved Profiles", "page", page_id="profiles"),
    GuiSurfaceBinding("settings-doctor", "Settings & Doctor", "page", page_id="settings-doctor"),
    GuiSurfaceBinding("run-history", "Run History", "page", page_id="run-history"),
    GuiSurfaceBinding("people-review", "People Review", "page", page_id="people-review"),
    GuiSurfaceBinding("people-catalog", "People Catalog", "page", page_id="people-catalog"),
    GuiSurfaceBinding("desktop-shell", "Desktop Shell", "shell", page_id=None),
    GuiSurfaceBinding("review-workbench", "Review Workbench", "page", page_id="review-workbench"),
    GuiSurfaceBinding("decision-summary", "Decision Summary", "panel", page_id="run-history"),
)


def list_gui_surface_bindings() -> list[GuiSurfaceBinding]:
    return list(_SURFACE_BINDINGS)


def _surface_by_id(surfaces: Iterable[GuiSurfaceBinding]) -> dict[str, GuiSurfaceBinding]:
    return {surface.surface_id: surface for surface in surfaces}


def _page_ids() -> set[str]:
    return {page.page_id for page in list_gui_page_contracts()}


def _contract_binding_record(contract: AppServiceContract, surface_map: Mapping[str, GuiSurfaceBinding], page_ids: set[str]) -> dict[str, object]:
    bound_surfaces: list[dict[str, object]] = []
    unresolved_surfaces: list[str] = []
    invalid_page_bindings: list[dict[str, object]] = []

    for surface_id in contract.consumer_surfaces:
        surface = surface_map.get(surface_id)
        if surface is None:
            unresolved_surfaces.append(surface_id)
            continue
        surface_payload = surface.to_dict()
        bound_surfaces.append(surface_payload)
        page_id = surface.page_id
        if page_id is not None and page_id not in page_ids:
            invalid_page_bindings.append({"surface_id": surface_id, "page_id": page_id})

    producer_commands = [command for command in contract.producer_commands if str(command).strip()]
    fully_bound = bool(producer_commands) and not unresolved_surfaces and not invalid_page_bindings
    return {
        "contract_id": contract.contract_id,
        "title": contract.title,
        "safety_level": contract.safety_level,
        "gui_stability": contract.gui_stability,
        "producer_command_count": len(producer_commands),
        "consumer_surface_count": len(contract.consumer_surfaces),
        "bound_surface_count": len(bound_surfaces),
        "bound_surfaces": bound_surfaces,
        "unresolved_surfaces": unresolved_surfaces,
        "invalid_page_bindings": invalid_page_bindings,
        "fully_bound": fully_bound,
        "headless_testable": contract.headless_testable and all(surface.get("headless_testable") for surface in bound_surfaces),
        "requires_user_confirmation": contract.requires_user_confirmation,
        "writes_app_state": contract.writes_app_state,
        "executes_media_operations": contract.executes_media_operations,
    }


def build_gui_app_contract_bindings() -> dict[str, object]:
    """Validate how app-service contracts are bound to GUI surfaces.

    This is deliberately still a headless data contract. It proves that a future
    Qt shell has explicit, named surfaces for each app-service contract instead
    of parsing CLI console text or duplicating core business logic.
    """

    contracts = list_app_service_contracts()
    surfaces = list_gui_surface_bindings()
    surface_map = _surface_by_id(surfaces)
    page_ids = _page_ids()
    records = [_contract_binding_record(contract, surface_map, page_ids) for contract in contracts]
    unresolved = [record for record in records if record["unresolved_surfaces"]]
    invalid_pages = [record for record in records if record["invalid_page_bindings"]]
    stable_unbound = [record for record in records if record["gui_stability"] == "stable" and not record["fully_bound"]]
    ready = not unresolved and not invalid_pages and not stable_unbound
    return {
        "schema_version": GUI_APP_CONTRACT_BINDINGS_SCHEMA_VERSION,
        "kind": GUI_APP_CONTRACT_BINDINGS_KIND,
        "generated_at_utc": _now_utc(),
        "contract_count": len(records),
        "surface_count": len(surfaces),
        "bindings": records,
        "surface_registry": [surface.to_dict() for surface in surfaces],
        "summary": {
            "fully_bound_contract_count": sum(1 for record in records if record["fully_bound"]),
            "unresolved_contract_count": len(unresolved),
            "invalid_page_binding_count": len(invalid_pages),
            "stable_unbound_contract_count": len(stable_unbound),
            "sensitive_contract_count": sum(1 for record in records if record["safety_level"] == "sensitive"),
            "requires_confirmation_count": sum(1 for record in records if record["requires_user_confirmation"]),
            "writes_app_state_count": sum(1 for record in records if record["writes_app_state"]),
            "executes_media_operations_count": sum(1 for record in records if record["executes_media_operations"]),
        },
        "readiness": {
            "ready": ready,
            "status": "ready" if ready else "blocked",
            "next_action": (
                "Bind the first real Qt page to these app-service surfaces without adding GUI-only business logic."
                if ready
                else "Fix unresolved or invalid GUI surface bindings before adding more desktop UI behavior."
            ),
        },
        "boundary_rules": [
            "GUI surfaces must resolve through this binding matrix before a real Qt widget consumes an app-service contract.",
            "Panels may share page containers, but they still need explicit surface ids.",
            "Sensitive surfaces must keep command execution disabled until a reviewed command plan exists.",
        ],
    }


def summarize_gui_app_contract_bindings(payload: Mapping[str, Any]) -> str:
    summary = payload.get("summary") if isinstance(payload.get("summary"), Mapping) else {}
    readiness = payload.get("readiness") if isinstance(payload.get("readiness"), Mapping) else {}
    return "\n".join(
        [
            "GUI app-service contract bindings",
            f"  Contracts: {payload.get('contract_count')}",
            f"  Surfaces: {payload.get('surface_count')}",
            f"  Fully bound: {summary.get('fully_bound_contract_count')}",
            f"  Stable unbound: {summary.get('stable_unbound_contract_count')}",
            f"  Unresolved contracts: {summary.get('unresolved_contract_count')}",
            f"  Ready: {readiness.get('ready')}",
            f"  Status: {readiness.get('status')}",
            f"  Next action: {readiness.get('next_action')}",
        ]
    )


def write_gui_app_contract_bindings(path: str | Path) -> dict[str, object]:
    payload = build_gui_app_contract_bindings()
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {**payload, "written_file": str(output_path)}


__all__ = [
    "GUI_APP_CONTRACT_BINDINGS_KIND",
    "GUI_APP_CONTRACT_BINDINGS_SCHEMA_VERSION",
    "GuiSurfaceBinding",
    "build_gui_app_contract_bindings",
    "list_gui_surface_bindings",
    "summarize_gui_app_contract_bindings",
    "write_gui_app_contract_bindings",
]
