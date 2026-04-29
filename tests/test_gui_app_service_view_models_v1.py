from __future__ import annotations

import json
import sys
from pathlib import Path

from media_manager.core.gui_app_service_view_models import (
    build_ui_app_service_view_models,
    summarize_ui_app_service_view_models,
    write_ui_app_service_view_models,
)


def _home_state() -> dict[str, object]:
    return {
        "profiles": {"summary": {"profile_count": 2, "valid_count": 1}},
        "runs": {
            "summary": {"run_count": 2, "error_count": 1},
            "items": [
                {"run_id": "20260429-duplicates-preview", "command": "duplicates", "mode": "preview", "status": "needs_review", "exit_code": 0, "review_candidate_count": 3, "path": "C:/runs/duplicates"},
                {"run_id": "20260429-similar-images-preview", "command": "similar-images", "mode": "preview", "status": "ready", "exit_code": 0, "review_candidate_count": 1, "path": "C:/runs/similar"},
            ],
        },
        "people_review": {"summary": {"group_count": 4, "face_count": 12}},
        "manifest_summary": {"entrypoints": {"duplicates": "media-manager duplicates", "organize": "media-manager organize", "people": "media-manager people"}},
        "suggested_next_step": "Review the latest duplicate run.",
    }


def test_ui_app_service_view_models_are_product_ui_contracts_without_qt() -> None:
    sys.modules.pop("PySide6", None)
    payload = build_ui_app_service_view_models(_home_state(), language="en")
    assert payload["kind"] == "ui_app_service_view_models"
    assert payload["summary"]["view_model_count"] == 7
    assert payload["view_models"]["scan_setup"]["preview_first"] is True
    assert payload["view_models"]["duplicate_review"]["review_candidate_count"] == 3
    assert payload["view_models"]["similar_images"]["run_count"] == 1
    assert payload["view_models"]["decision_summary"]["apply_enabled"] is False
    assert payload["view_models"]["review_workbench"]["summary"]["lane_count"] == 4
    assert payload["view_models"]["review_workbench"]["capabilities"]["apply_enabled"] is False
    assert payload["capabilities"]["executes_commands"] is False
    assert "PySide6" not in sys.modules


def test_ui_app_service_view_models_summary_and_writer(tmp_path: Path) -> None:
    payload = write_ui_app_service_view_models(tmp_path / "ui-models", home_state_json=None, language="de")
    assert payload["written_file_count"] == 9
    assert (tmp_path / "ui-models" / "ui_app_service_view_models.json").exists()
    assert (tmp_path / "ui-models" / "duplicate-review.json").exists()
    assert (tmp_path / "ui-models" / "review-workbench.json").exists()
    written = json.loads((tmp_path / "ui-models" / "ui_app_service_view_models.json").read_text(encoding="utf-8"))
    assert written["kind"] == "ui_app_service_view_models"
    text = summarize_ui_app_service_view_models(written)
    assert "Media Manager UI app-service view models" in text
    assert "Executes commands: False" in text
