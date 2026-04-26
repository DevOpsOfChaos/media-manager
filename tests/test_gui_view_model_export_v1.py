import json
from pathlib import Path

from media_manager.core.gui_view_model_export import build_view_model_export, write_view_model_export


def test_view_model_export_writes_expected_files(tmp_path: Path) -> None:
    page = {"page_id": "people-review", "kind": "people_review_page", "groups": []}
    manifest = build_view_model_export(page_model=page, out_dir=tmp_path)
    assert manifest["sensitive"] is True

    written = write_view_model_export(page_model=page, out_dir=tmp_path)
    assert len(written["written_files"]) == 4
    assert (tmp_path / "render_contract.json").exists()
    assert json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))["page_id"] == "people-review"
