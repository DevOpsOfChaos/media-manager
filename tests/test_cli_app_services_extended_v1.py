from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_app_services import main as services_main


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_minimal_bundle(bundle: Path) -> None:
    _write_json(bundle / "bundle_manifest.json", {"status": "ok", "summary": {"ready_group_count": 0}})
    _write_json(bundle / "people_report.json", {"schema_version": 1})
    _write_json(bundle / "people_review_workflow.json", {"workflow": "people_review"})
    _write_json(bundle / "people_review_workspace.json", {"workspace": "people_review_workspace"})
    (bundle / "summary.txt").write_text("summary", encoding="utf-8")
    _write_json(bundle / "assets" / "people_review_assets.json", {"assets": []})


def test_cli_workspace_register_people_bundle(tmp_path: Path, capsys) -> None:
    state_path = tmp_path / "gui_state.json"
    bundle = tmp_path / "bundle"
    _write_minimal_bundle(bundle)

    assert services_main(["workspace", "init", "--state-json", str(state_path), "--json"]) == 0
    capsys.readouterr()
    assert services_main([
        "workspace",
        "register-people-bundle",
        "--state-json",
        str(state_path),
        "--bundle-dir",
        str(bundle),
        "--json",
    ]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["active_page_id"] == "people-review"
    assert payload["people_review"]["last_bundle_dir"] == str(bundle)


def test_cli_validate_people_bundle(tmp_path: Path, capsys) -> None:
    bundle = tmp_path / "bundle"
    _write_minimal_bundle(bundle)

    assert services_main(["validate-people-bundle", "--bundle-dir", str(bundle), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "ok"
    assert payload["ready_for_gui"] is True


def test_cli_command_plan_people_review_apply(tmp_path: Path, capsys) -> None:
    assert services_main([
        "command-plan",
        "people-review-apply",
        "--catalog",
        str(tmp_path / "people.json"),
        "--workflow-json",
        str(tmp_path / "workflow.json"),
        "--report-json",
        str(tmp_path / "report.json"),
        "--json",
    ]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["plan_id"] == "people:review-apply"
    assert payload["requires_confirmation"] is True


def test_cli_startup_state_uses_state_file(tmp_path: Path, capsys) -> None:
    state_path = tmp_path / "gui_state.json"

    assert services_main(["workspace", "init", "--state-json", str(state_path), "--json"]) == 0
    capsys.readouterr()
    assert services_main(["startup-state", "--gui-state", str(state_path), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["kind"] == "app_startup_state"
    assert payload["gui_state_loaded"] is True
