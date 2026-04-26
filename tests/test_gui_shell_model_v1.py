from __future__ import annotations

from pathlib import Path

from media_manager.core.gui_shell_model import build_gui_shell_model, build_gui_shell_model_from_paths, summarize_gui_shell_model


def test_build_gui_shell_model_uses_active_page() -> None:
    home_state = {
        "active_page_id": "people-review",
        "suggested_next_step": "Review people.",
        "profiles": {"summary": {}, "items": []},
        "runs": {"summary": {}, "items": []},
        "people_review": None,
        "pages": [{"id": "dashboard", "label": "Dashboard"}, {"id": "people-review", "label": "People"}],
    }

    model = build_gui_shell_model(home_state=home_state, active_page_id="people-review")

    assert model["active_page_id"] == "people-review"
    assert model["page"]["page_id"] == "people-review"
    assert any(item["active"] for item in model["navigation"])
    assert model["capabilities"]["executes_commands"] is False


def test_build_gui_shell_model_from_paths_handles_missing_dirs(tmp_path: Path) -> None:
    model = build_gui_shell_model_from_paths(
        profile_dir=tmp_path / "profiles",
        run_dir=tmp_path / "runs",
        people_bundle_dir=tmp_path / "bundle",
        active_page_id="dashboard",
    )

    assert model["active_page_id"] == "dashboard"
    assert model["page"]["kind"] == "dashboard_page"
    assert "Media Manager" in summarize_gui_shell_model(model)
