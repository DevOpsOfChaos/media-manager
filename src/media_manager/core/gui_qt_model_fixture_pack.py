from __future__ import annotations

from .gui_qt_demo_workspace import build_demo_people_page, build_demo_shell_model

MODEL_FIXTURE_PACK_SCHEMA_VERSION = "1.0"


def build_model_fixture_pack() -> dict[str, object]:
    shell = build_demo_shell_model()
    people = build_demo_people_page()
    dashboard = {
        "schema_version": MODEL_FIXTURE_PACK_SCHEMA_VERSION,
        "page_id": "dashboard",
        "title": "Dashboard",
        "description": "Demo dashboard",
        "kind": "dashboard_page",
        "cards": [{"id": "people", "title": "People review", "metrics": {"groups": 3}}],
        "hero": {"title": "Welcome back", "subtitle": "Demo"},
    }
    return {
        "schema_version": MODEL_FIXTURE_PACK_SCHEMA_VERSION,
        "kind": "model_fixture_pack",
        "fixtures": {"shell": shell, "people_page": people, "dashboard_page": dashboard},
        "fixture_count": 3,
    }


def get_fixture(name: str) -> dict[str, object]:
    pack = build_model_fixture_pack()
    fixtures = pack["fixtures"]
    if isinstance(fixtures, dict) and name in fixtures:
        return dict(fixtures[name])
    raise KeyError(name)


__all__ = ["MODEL_FIXTURE_PACK_SCHEMA_VERSION", "build_model_fixture_pack", "get_fixture"]
