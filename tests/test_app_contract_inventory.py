from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_app_services import main as app_services_main
from media_manager.core.app_contract_inventory import (
    build_app_contract_inventory,
    list_app_service_contracts,
    write_app_contract_inventory,
)
from media_manager.core.app_services import build_app_contract_inventory as build_via_app_services


def test_contract_inventory_defines_gui_boundary_rules() -> None:
    payload = build_app_contract_inventory()

    assert payload["kind"] == "app_contract_inventory"
    assert payload["contract_count"] >= 8
    assert payload["summary"]["destructive_contract_count"] == 0
    assert payload["summary"]["sensitive_contract_count"] >= 1
    assert payload["summary"]["headless_testable_count"] == payload["contract_count"]
    assert any("must not parse human console output" in rule for rule in payload["boundary_rules"])

    contract_ids = {contract["contract_id"] for contract in payload["contracts"]}
    assert {"app_manifest", "report_service_bundle", "command_plan", "people_review_bundle", "review_workbench_apply_preview", "review_workbench_confirmation_dialog"} <= contract_ids


def test_contract_inventory_is_exposed_through_app_services_module() -> None:
    payload = build_via_app_services()
    assert payload["kind"] == "app_contract_inventory"
    assert payload["summary"]["stable_contract_count"] >= 1


def test_contract_records_are_plain_serializable_payloads() -> None:
    records = [contract.to_dict() for contract in list_app_service_contracts()]
    encoded = json.dumps(records, sort_keys=True)

    assert "report_service_bundle" in encoded
    assert all(record["executes_media_operations"] is False for record in records)


def test_write_app_contract_inventory_writes_json_file(tmp_path: Path) -> None:
    output_path = tmp_path / "contracts" / "app_contract_inventory.json"
    payload = write_app_contract_inventory(output_path)

    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded["kind"] == "app_contract_inventory"
    assert payload["written_file"] == str(output_path)


def test_cli_app_services_contracts_prints_text(capsys) -> None:
    exit_code = app_services_main(["contracts"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "GUI app-service contracts" in captured.out
    assert "report_service_bundle" in captured.out


def test_cli_app_services_contracts_writes_json(tmp_path: Path, capsys) -> None:
    out = tmp_path / "contracts.json"

    exit_code = app_services_main(["contracts", "--json", "--out", str(out)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert '"kind": "app_contract_inventory"' in captured.out
    assert json.loads(out.read_text(encoding="utf-8"))["contract_count"] >= 8
