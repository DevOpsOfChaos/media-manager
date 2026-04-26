from media_manager.core.gui_render_snapshot import build_render_snapshot, compare_render_snapshots, stable_json_digest


def test_render_snapshot_digest_is_stable() -> None:
    payload = {"kind": "x", "page_id": "dashboard", "summary": {"widget_count": 2}}
    first = build_render_snapshot(payload, label="a")
    second = build_render_snapshot({"summary": {"widget_count": 2}, "page_id": "dashboard", "kind": "x"}, label="b")

    assert first["digest"] == second["digest"]
    assert compare_render_snapshots(first, second)["changed"] is False
    assert len(stable_json_digest(payload)) == 16
