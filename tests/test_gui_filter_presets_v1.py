from media_manager.core.gui_filter_presets import apply_filter_preset, default_people_review_filter_presets, default_run_filter_presets, mark_active_preset


def test_people_filter_presets_are_localized() -> None:
    presets = default_people_review_filter_presets(language="de")
    assert presets[0]["label"] == "Alle"
    assert {item["status"] for item in presets if item.get("status")} >= {"needs_name", "needs_review", "ready_to_apply"}


def test_apply_status_filter_preset() -> None:
    rows = [{"group_id": "g1", "status": "needs_review"}, {"group_id": "g2", "status": "ready_to_apply"}]
    preset = next(item for item in default_people_review_filter_presets() if item["id"] == "ready")
    assert apply_filter_preset(rows, preset) == [{"group_id": "g2", "status": "ready_to_apply"}]


def test_apply_error_run_preset() -> None:
    rows = [{"run_id": "r1", "exit_code": 0}, {"run_id": "r2", "exit_code": 1}]
    preset = next(item for item in default_run_filter_presets() if item["id"] == "errors")
    assert [item["run_id"] for item in apply_filter_preset(rows, preset)] == ["r2"]


def test_mark_active_preset() -> None:
    marked = mark_active_preset(default_people_review_filter_presets(), "needs-name")
    assert next(item for item in marked if item["id"] == "needs-name")["active"] is True
