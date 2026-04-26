from media_manager.core.gui_qt_resource_policy import build_qt_resource_policy, apply_resource_policy_to_page, summarize_resource_pressure


def test_resource_policy_truncates_assets_and_rows():
    page = {"asset_refs": [{"id": str(i)} for i in range(5)], "rows": [{"id": str(i)} for i in range(4)]}
    policy = build_qt_resource_policy(max_visible_faces=2, max_table_rows=3)
    updated = apply_resource_policy_to_page(page, policy)
    assert len(updated["asset_refs"]) == 2
    assert updated["asset_refs_truncated_by_policy"] is True
    pressure = summarize_resource_pressure(page, policy)
    assert pressure["warning_count"] == 2
