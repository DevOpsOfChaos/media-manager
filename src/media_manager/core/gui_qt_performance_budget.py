from __future__ import annotations

from collections.abc import Mapping
from typing import Any

PERFORMANCE_BUDGET_SCHEMA_VERSION = "1.0"
DEFAULT_BUDGETS = {
    "widgets": 800,
    "visible_faces": 120,
    "table_rows": 500,
    "image_requests": 200,
    "diagnostics": 50,
}


def _count_widgets(node: Any) -> int:
    if not isinstance(node, Mapping):
        return 0
    children = node.get("children")
    child_list = children if isinstance(children, list) else []
    return 1 + sum(_count_widgets(child) for child in child_list)


def build_qt_performance_budget(*, overrides: Mapping[str, Any] | None = None) -> dict[str, object]:
    budgets = dict(DEFAULT_BUDGETS)
    for key, value in dict(overrides or {}).items():
        if key in budgets:
            try:
                budgets[key] = max(0, int(value))
            except (TypeError, ValueError):
                pass
    return {"schema_version": PERFORMANCE_BUDGET_SCHEMA_VERSION, "kind": "qt_performance_budget", "budgets": budgets}


def evaluate_qt_performance_budget(*, widget_tree: Mapping[str, Any] | None = None, metrics: Mapping[str, Any] | None = None, budget: Mapping[str, Any] | None = None) -> dict[str, object]:
    limits = dict((budget or build_qt_performance_budget()).get("budgets", DEFAULT_BUDGETS))
    actual = {"widgets": _count_widgets(widget_tree or {})}
    for key, value in dict(metrics or {}).items():
        try:
            actual[str(key)] = int(value)
        except (TypeError, ValueError):
            continue
    violations = []
    for key, limit in limits.items():
        value = actual.get(key, 0)
        if value > int(limit):
            violations.append({"metric": key, "value": value, "limit": int(limit), "over_by": value - int(limit)})
    return {
        "schema_version": PERFORMANCE_BUDGET_SCHEMA_VERSION,
        "kind": "qt_performance_evaluation",
        "ok": not violations,
        "actual": actual,
        "budgets": limits,
        "violations": violations,
        "violation_count": len(violations),
    }


__all__ = ["DEFAULT_BUDGETS", "PERFORMANCE_BUDGET_SCHEMA_VERSION", "build_qt_performance_budget", "evaluate_qt_performance_budget"]
