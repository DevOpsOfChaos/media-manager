from media_manager.core.gui_model_diff import build_model_diff, diff_has_changes, diff_mapping


def test_diff_mapping_detects_nested_changes() -> None:
    changes = diff_mapping({"a": 1, "b": {"x": 1}}, {"b": {"x": 2}, "c": 3})
    assert {item["path"] for item in changes} == {"a", "b.x", "c"}


def test_build_model_diff_summarizes_changes() -> None:
    diff = build_model_diff({"a": 1}, {"a": 2, "b": 3})
    assert diff["change_count"] == 2
    assert diff["change_summary"] == {"added": 1, "changed": 1}
    assert diff_has_changes(diff) is True


def test_build_model_diff_can_truncate() -> None:
    diff = build_model_diff({}, {str(i): i for i in range(5)}, max_changes=2)
    assert diff["truncated"] is True
    assert diff["returned_change_count"] == 2
