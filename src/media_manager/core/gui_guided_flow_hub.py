from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_empty_states import build_empty_state
from .gui_guided_flow import build_guided_flow, build_guided_step
from .gui_i18n import translate
from .gui_modern_components import build_action_button, build_card

GUIDED_FLOW_HUB_SCHEMA_VERSION = "1.0"

FLOW_DEFINITIONS: tuple[dict[str, object], ...] = (
    {
        "flow_id": "organize-media",
        "title": "Organize media files",
        "problem": "My photos and videos are scattered across folders. I want them organized by date.",
        "icon": "folder-tree",
        "risk_level": "safe",
        "command": "organize",
        "steps": ("choose_sources", "choose_target", "choose_pattern", "preview", "apply"),
        "required_inputs": ("source_dirs", "target_dir"),
    },
    {
        "flow_id": "rename-media",
        "title": "Rename media files",
        "problem": "My files have cryptic names like IMG_0001. I want meaningful names with dates and locations.",
        "icon": "pencil",
        "risk_level": "safe",
        "command": "rename",
        "steps": ("choose_sources", "choose_template", "preview", "apply"),
        "required_inputs": ("source_dirs",),
    },
    {
        "flow_id": "find-duplicates",
        "title": "Find and remove duplicates",
        "problem": "I have duplicate photos taking up space. I want to find exact copies and similar images.",
        "icon": "files",
        "risk_level": "medium",
        "command": "duplicates",
        "steps": ("choose_sources", "choose_mode", "preview", "review_decisions", "apply"),
        "required_inputs": ("source_dirs",),
    },
    {
        "flow_id": "cleanup-leftovers",
        "title": "Clean up leftover files",
        "problem": "After organizing, empty folders and leftover files remain. I want to clean them up safely.",
        "icon": "broom",
        "risk_level": "medium",
        "command": "cleanup",
        "steps": ("choose_sources", "choose_target", "preview", "apply"),
        "required_inputs": ("source_dirs", "target_dir"),
    },
    {
        "flow_id": "create-trip",
        "title": "Create a trip album",
        "problem": "I want to group photos from a vacation into a named trip I can browse later.",
        "icon": "map-pin",
        "risk_level": "safe",
        "command": "trip",
        "steps": ("choose_sources", "choose_target", "name_trip", "choose_dates", "preview", "apply"),
        "required_inputs": ("source_dirs", "target_dir", "label", "start_date", "end_date"),
    },
    {
        "flow_id": "find-people",
        "title": "Find people in photos",
        "problem": "I want to find all photos of specific people using local face recognition.",
        "icon": "users",
        "risk_level": "sensitive",
        "command": "people",
        "steps": ("setup_backend", "create_catalog", "choose_sources", "scan", "review_faces", "apply_catalog"),
        "required_inputs": ("source_dirs",),
    },
)


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _text(value: object, fallback: str = "") -> str:
    if value is None:
        return fallback
    return str(value).strip() or fallback


def build_flow_step_for_command(
    flow_id: str,
    step_id: str,
    *,
    flow_state: Mapping[str, Any],
    language: str = "en",
) -> dict[str, object]:
    """Build a single guided step for a specific command flow."""
    state = _as_mapping(flow_state)
    step_keys: dict[str, str] = {
        "choose_sources": "source_dirs",
        "choose_target": "target_dir",
        "choose_pattern": "pattern",
        "choose_template": "template",
        "choose_mode": "mode",
        "name_trip": "label",
        "choose_dates": "dates",
        "setup_backend": "backend_checked",
        "create_catalog": "catalog_created",
        "scan": "scan_complete",
        "review_faces": "review_complete",
        "preview": "preview_done",
        "review_decisions": "decisions_reviewed",
        "apply": "apply_done",
        "apply_catalog": "catalog_updated",
    }
    state_key = step_keys.get(step_id, step_id)
    is_complete = bool(state.get(state_key))

    step_titles: dict[str, str] = {
        "choose_sources": translate("wizard.step.sources", language=language, fallback="Choose source folders"),
        "choose_target": translate("wizard.step.target", language=language, fallback="Choose target folder"),
        "choose_pattern": translate("wizard.step.pattern", language=language, fallback="Choose organization pattern"),
        "choose_template": translate("wizard.step.template", language=language, fallback="Choose naming template"),
        "choose_mode": translate("wizard.step.mode", language=language, fallback="Choose scan mode"),
        "name_trip": translate("wizard.step.trip_name", language=language, fallback="Name your trip"),
        "choose_dates": translate("wizard.step.dates", language=language, fallback="Set trip dates"),
        "setup_backend": translate("wizard.step.backend", language=language, fallback="Set up face recognition"),
        "create_catalog": translate("wizard.step.catalog", language=language, fallback="Create people catalog"),
        "scan": translate("wizard.step.scan", language=language, fallback="Scan for faces"),
        "review_faces": translate("wizard.step.review", language=language, fallback="Review detected faces"),
        "preview": translate("wizard.step.preview", language=language, fallback="Preview changes"),
        "review_decisions": translate("wizard.step.review_decisions", language=language, fallback="Review decisions"),
        "apply": translate("wizard.step.apply", language=language, fallback="Apply changes"),
        "apply_catalog": translate("wizard.step.apply_catalog", language=language, fallback="Apply to catalog"),
    }

    return build_guided_step(
        step_id,
        step_titles.get(step_id, step_id.replace("_", " ").title()),
        complete=is_complete,
        details=_text(state.get(f"{state_key}_detail")),
    )


def build_guided_flow_for_command(
    flow_id: str,
    *,
    flow_state: Mapping[str, Any] | None = None,
    language: str = "en",
) -> dict[str, object]:
    """Build a full guided flow for a specific command."""
    state = _as_mapping(flow_state or {})
    definition = next((f for f in FLOW_DEFINITIONS if f.get("flow_id") == flow_id), None)
    if definition is None:
        return build_guided_flow(flow_id, [], title=flow_id.replace("-", " ").title())

    step_ids = definition.get("steps", ())
    if isinstance(step_ids, tuple):
        step_ids = list(step_ids)
    steps = [build_flow_step_for_command(flow_id, str(sid), flow_state=state, language=language) for sid in step_ids]
    return build_guided_flow(flow_id, steps, title=str(definition.get("title", flow_id)))


def build_guided_flow_hub_page_model(
    home_state: Mapping[str, Any],
    *,
    language: str = "en",
    selected_flow_id: str | None = None,
) -> dict[str, object]:
    """Build the guided-flow hub: a problem-first entry page.

    Users pick their problem and are guided step-by-step through the solution.
    """
    home = _as_mapping(home_state)
    flow_state = _as_mapping(home.get("flow_state") or {})
    selected = selected_flow_id or _text(home.get("selected_flow_id"))

    # Build flow cards
    flows: list[dict[str, object]] = []
    for definition in FLOW_DEFINITIONS:
        fid = str(definition.get("flow_id", ""))
        flows.append(
            build_card(
                fid,
                str(definition.get("title", fid)),
                subtitle=str(definition.get("problem", "")),
                icon=str(definition.get("icon", "circle")),
                tone={
                    "safe": "success",
                    "medium": "warning",
                    "sensitive": "warning",
                }.get(str(definition.get("risk_level", "")), "info"),
            )
        )

    # Build active flow if one is selected
    active_flow = None
    if selected:
        definition = next((f for f in FLOW_DEFINITIONS if f.get("flow_id") == selected), None)
        if definition:
            active_flow = build_guided_flow_for_command(selected, flow_state=flow_state, language=language)
            active_flow = {
                **active_flow,
                "command": str(definition.get("command", "")),
                "risk_level": str(definition.get("risk_level", "safe")),
                "required_inputs": list(definition.get("required_inputs", ()) or ()),
            }

    return {
        "schema_version": GUIDED_FLOW_HUB_SCHEMA_VERSION,
        "page_id": "guided-flows",
        "title": translate("guided.hub.title", language=language, fallback="What would you like to do?"),
        "description": translate("guided.hub.description", language=language, fallback="Pick your goal and follow the steps. No need to remember CLI flags."),
        "kind": "guided_flow_hub_page",
        "flows": flows,
        "flow_count": len(flows),
        "selected_flow_id": selected,
        "active_flow": active_flow,
        "quick_start": [
            build_action_button("organize-media", translate("guided.quick.organize", language=language, fallback="Organize files"), variant="primary", icon="folder-tree"),
            build_action_button("find-duplicates", translate("guided.quick.duplicates", language=language, fallback="Find duplicates"), variant="secondary", icon="files"),
            build_action_button("find-people", translate("guided.quick.people", language=language, fallback="Find people"), variant="secondary", icon="users"),
        ],
        "empty_state": build_empty_state("guided-flows", language=language) if not flows else None,
        "capabilities": {
            "headless_testable": True,
            "requires_pyside6": False,
            "opens_window": False,
            "executes_commands": False,
        },
    }
