from __future__ import annotations

DEMO_WORKSPACE_SCHEMA_VERSION = "1.0"


def build_demo_home_state(*, language: str = "en") -> dict[str, object]:
    return {
        "schema_version": DEMO_WORKSPACE_SCHEMA_VERSION,
        "kind": "demo_home_state",
        "language": language,
        "profiles": {"summary": {"profile_count": 2, "valid_count": 2, "favorite_count": 1}, "items": []},
        "runs": {"summary": {"run_count": 3, "error_count": 0}, "items": []},
        "people_review": {
            "ready_for_gui": True,
            "bundle_dir": "demo/people-review-bundle",
            "summary": {"group_count": 3, "face_count": 24, "ready_group_count": 1},
        },
        "suggested_next_step": "Open the people review page.",
    }


def build_demo_people_page() -> dict[str, object]:
    groups = [
        {"group_id": "unknown-1", "display_label": "Unknown person", "status": "needs_name", "face_count": 8, "included_faces": 8, "excluded_faces": 0},
        {"group_id": "max", "display_label": "Max Example", "status": "ready_to_apply", "face_count": 11, "included_faces": 10, "excluded_faces": 1},
        {"group_id": "unknown-2", "display_label": "Unknown person", "status": "needs_review", "face_count": 5, "included_faces": 3, "excluded_faces": 2},
    ]
    return {
        "schema_version": DEMO_WORKSPACE_SCHEMA_VERSION,
        "page_id": "people-review",
        "title": "People review",
        "description": "Review detected people groups.",
        "kind": "people_review_page",
        "layout": "review_queue_master_detail",
        "overview": {"groups": len(groups), "faces": 24, "ready": 1},
        "groups": groups,
        "selected_group_id": "unknown-1",
        "detail": {"title": "Unknown person", "faces": [{"face_id": "face-1", "decision_status": "included"}]},
        "actions": [{"id": "apply_ready_groups", "label": "Apply ready groups", "risk_level": "high", "requires_confirmation": True}],
    }


def build_demo_shell_model() -> dict[str, object]:
    page = build_demo_people_page()
    return {
        "schema_version": DEMO_WORKSPACE_SCHEMA_VERSION,
        "application": {"title": "Media Manager", "subtitle": "Demo workspace"},
        "active_page_id": "people-review",
        "language": "en",
        "theme": {"theme": "modern-dark", "tokens": {"background": "#0f172a"}},
        "navigation": [
            {"id": "dashboard", "label": "Dashboard", "active": False, "enabled": True},
            {"id": "people-review", "label": "People review", "active": True, "enabled": True},
        ],
        "page": page,
        "home_state": build_demo_home_state(),
        "status_bar": {"text": "Demo ready."},
        "capabilities": {"executes_commands": False, "demo": True},
    }


def build_demo_workspace_bundle() -> dict[str, object]:
    return {
        "schema_version": DEMO_WORKSPACE_SCHEMA_VERSION,
        "kind": "demo_workspace_bundle",
        "home_state": build_demo_home_state(),
        "people_page": build_demo_people_page(),
        "shell_model": build_demo_shell_model(),
    }


__all__ = [
    "DEMO_WORKSPACE_SCHEMA_VERSION",
    "build_demo_home_state",
    "build_demo_people_page",
    "build_demo_shell_model",
    "build_demo_workspace_bundle",
]
