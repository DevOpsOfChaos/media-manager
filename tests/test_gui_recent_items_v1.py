from __future__ import annotations

from pathlib import Path

from media_manager.core.gui_recent_items import add_recent_item, build_recent_items_state


def test_recent_items_dedupe_and_limit(tmp_path: Path) -> None:
    first = tmp_path / "bundle"
    first.mkdir()
    items = [
        {"kind": "people_bundle", "path": str(first), "label": "Old"},
        {"kind": "people_bundle", "path": str(first), "label": "Duplicate"},
        {"kind": "run_dir", "path": str(tmp_path / "runs")},
    ]

    state = build_recent_items_state(recent_items=items, limit=2)

    assert state["item_count"] == 2
    assert state["summary"] == {"people_bundle": 1, "run_dir": 1}
    assert state["items"][0]["label"] == "Old"
    assert state["items"][0]["exists"] is True


def test_add_recent_item_moves_new_item_to_front(tmp_path: Path) -> None:
    old = tmp_path / "old"
    new = tmp_path / "new"

    items = add_recent_item(
        [{"kind": "people_bundle", "path": str(old), "label": "Old"}],
        path=new,
        kind="people_bundle",
        label="New",
        limit=3,
    )

    assert [item["label"] for item in items] == ["New", "Old"]
