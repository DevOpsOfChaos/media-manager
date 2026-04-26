from media_manager.core.gui_qt_image_pipeline import build_qt_image_pipeline, build_qt_image_request
from media_manager.core.gui_qt_incremental_update import build_incremental_update_plan, update_plan_summary
from media_manager.core.gui_qt_theme_adapter import build_qt_theme_adapter_payload, validate_qt_theme_adapter

def test_incremental_update_detects_page_switch() -> None:
    plan = build_incremental_update_plan({"active_page_id": "dashboard"}, {"active_page_id": "people-review", "page": {"page_id": "people-review"}})
    assert plan["requires_full_rebuild"] is True
    assert "switch_page" in update_plan_summary(plan)["kinds"]

def test_theme_adapter_accepts_tokens_alias() -> None:
    payload = build_qt_theme_adapter_payload({"theme": "modern-light", "tokens": {"background": "#fff", "surface": "#eee", "text": "#111", "accent": "#00f"}})
    assert payload["compatible_with_legacy_tokens"] is True
    assert validate_qt_theme_adapter(payload)["valid"] is True

def test_image_pipeline_marks_face_crops_sensitive() -> None:
    request = build_qt_image_request({"face_id": "face-1", "asset_path": "missing.jpg", "role": "face_crop"})
    assert request["sensitive"] is True
    assert request["cache_allowed"] is False
    pipeline = build_qt_image_pipeline([{"asset_id": "a", "path": "a.jpg"}, {"asset_id": "b", "role": "face_crop", "path": "b.jpg"}], limit=1)
    assert pipeline["request_count"] == 1
    assert pipeline["truncated"] is True
