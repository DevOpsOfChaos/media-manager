from __future__ import annotations

from collections.abc import Mapping
from typing import Any

UI_CONTRACT_VALIDATOR_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def validate_qt_page_contract(page_model: Mapping[str, Any]) -> dict[str, object]:
    problems: list[str] = []
    warnings: list[str] = []
    for key in ("page_id", "kind", "title", "layout"):
        if key not in page_model or page_model.get(key) in (None, ""):
            problems.append(f"Missing page field: {key}")
    if page_model.get("page_id") == "people-review":
        for key in ("queue", "editor", "card_grid", "detail"):
            if key not in page_model:
                problems.append(f"People review page is missing {key}.")
    if page_model.get("empty_state") and (page_model.get("rows") or page_model.get("groups")):
        warnings.append("Page has both empty_state and visible rows/groups.")
    return _result("qt_page_contract_validation", problems, warnings)


def validate_qt_shell_contract(shell_model: Mapping[str, Any]) -> dict[str, object]:
    problems: list[str] = []
    warnings: list[str] = []
    for key in ("application", "window", "navigation", "page", "theme", "status_bar"):
        if key not in shell_model:
            problems.append(f"Missing shell field: {key}")
    nav = _list(shell_model.get("navigation"))
    active_page_id = shell_model.get("active_page_id")
    if nav and not any(_mapping(item).get("id") == active_page_id for item in nav):
        warnings.append("Active page is not present in navigation.")
    page_validation = validate_qt_page_contract(_mapping(shell_model.get("page")))
    problems.extend(str(item) for item in _list(page_validation.get("problems")))
    warnings.extend(str(item) for item in _list(page_validation.get("warnings")))
    return _result("qt_shell_contract_validation", problems, warnings)


def _result(kind: str, problems: list[str], warnings: list[str]) -> dict[str, object]:
    return {
        "schema_version": UI_CONTRACT_VALIDATOR_SCHEMA_VERSION,
        "kind": kind,
        "valid": not problems,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "problems": problems,
        "warnings": warnings,
    }


__all__ = ["UI_CONTRACT_VALIDATOR_SCHEMA_VERSION", "validate_qt_page_contract", "validate_qt_shell_contract"]
