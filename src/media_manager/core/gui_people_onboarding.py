from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_guided_flow import build_guided_step, build_guided_flow
from .gui_i18n import translate
from .gui_modern_components import build_action_button, build_card

PEOPLE_ONBOARDING_SCHEMA_VERSION = "1.0"


def _as_bool(value: object, default: bool = False) -> bool:
    return value if isinstance(value, bool) else default


def _as_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


def _text(value: object, fallback: str = "") -> str:
    if value is None:
        return fallback
    return str(value).strip() or fallback


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_people_onboarding_page_model(
    home_state: Mapping[str, Any],
    *,
    language: str = "en",
) -> dict[str, object]:
    """Build the guided face recognition onboarding page model.

    Walks users through: install backend → create catalog → first scan → review faces.
    Headless, no PySide6, non-executing.
    """

    home = _mapping(home_state)
    backend_status = _mapping(home.get("people_backend_status") or {})
    people_summary = _mapping(_mapping(home.get("people_review")).get("summary") or {})
    catalog_info = _mapping(home.get("people_catalog_info") or {})

    backend_available = _as_bool(backend_status.get("available"))
    dlib_available = _as_bool(backend_status.get("dlib_available"))
    strong_available = _as_bool(backend_status.get("strong_backend_available"))
    catalog_exists = _as_bool(catalog_info.get("exists"))
    catalog_person_count = _as_int(catalog_info.get("person_count"))
    has_scan = _as_int(people_summary.get("face_count", people_summary.get("group_count", 0))) > 0
    has_review = _as_bool(people_summary.get("has_review_decisions"))

    steps = [
        build_guided_step(
            "install_backend",
            translate("people.onboarding.step.backend", language=language, fallback="Install face recognition backend"),
            complete=backend_available,
            details="dlib available" if dlib_available else "strong backend available" if strong_available else "Install: pip install -e .[people]",
        ),
        build_guided_step(
            "create_catalog",
            translate("people.onboarding.step.catalog", language=language, fallback="Create people catalog"),
            complete=catalog_exists and catalog_person_count >= 0,
            blocked=not backend_available,
            details=f"{catalog_person_count} persons in catalog" if catalog_exists else "Run: media-manager people catalog-init",
        ),
        build_guided_step(
            "first_scan",
            translate("people.onboarding.step.scan", language=language, fallback="Run first face scan"),
            complete=has_scan,
            blocked=not backend_available,
            details="Run: media-manager people scan --source <dir> --catalog <path>",
        ),
        build_guided_step(
            "review_faces",
            translate("people.onboarding.step.review", language=language, fallback="Review detected faces"),
            complete=has_review,
            blocked=not has_scan,
            details="Review and name detected faces in the People Review page.",
        ),
        build_guided_step(
            "rescan_improve",
            translate("people.onboarding.step.rescan", language=language, fallback="Rescan to improve matches"),
            complete=False,
            optional=True,
            blocked=not has_review,
            details="After naming people, rescan to let the system match more faces automatically.",
        ),
    ]

    flow = build_guided_flow("people_onboarding", steps, title="Face recognition setup")

    return {
        "schema_version": PEOPLE_ONBOARDING_SCHEMA_VERSION,
        "page_id": "people-setup",
        "title": translate("people.onboarding.title", language=language, fallback="Face Recognition Setup"),
        "description": translate("people.onboarding.description", language=language, fallback="Set up local face recognition to automatically find and name people in your photos."),
        "kind": "people_setup_page",
        "guided_flow": flow,
        "backend_status": {
            "available": backend_available,
            "dlib_available": dlib_available,
            "strong_backend_available": strong_available,
            "selected_backend": _text(backend_status.get("selected_backend")),
            "matching_available": _as_bool(_mapping(backend_status.get("capabilities")).get("named_person_matching")),
            "detection_available": _as_bool(_mapping(backend_status.get("capabilities")).get("face_detection")),
            "install_guidance": _mapping(backend_status.get("install_guidance")),
            "next_action": _text(backend_status.get("next_action")),
        },
        "catalog": {
            "exists": catalog_exists,
            "person_count": catalog_person_count,
            "path": _text(catalog_info.get("path")),
        },
        "scan_summary": {
            "has_scan": has_scan,
            "face_count": _as_int(people_summary.get("face_count", people_summary.get("faces", 0))),
            "matched_faces": _as_int(people_summary.get("matched_faces", 0)),
            "unknown_faces": _as_int(people_summary.get("unknown_faces", 0)),
        },
        "quick_actions": [
            build_action_button("check_backend", translate("people.action.check_backend", language=language, fallback="Check backend"), variant="primary", icon="cpu"),
            build_action_button("init_catalog", translate("people.action.init_catalog", language=language, fallback="Create catalog"), variant="secondary", icon="file-plus"),
            build_action_button("open_people_review", translate("people.action.review", language=language, fallback="Review faces"), variant="secondary" if has_scan else "disabled", icon="users"),
        ],
        "privacy_notice": translate("privacy.people", language=language, fallback="Face recognition runs entirely on your computer. No face data is uploaded anywhere."),
        "capabilities": {
            "headless_testable": True,
            "requires_pyside6": False,
            "opens_window": False,
            "executes_commands": False,
            "apply_enabled": False,
        },
    }
