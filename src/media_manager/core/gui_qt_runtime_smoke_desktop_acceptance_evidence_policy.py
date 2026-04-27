from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_EVIDENCE_POLICY_SCHEMA_VERSION = "1.0"


def build_qt_runtime_smoke_desktop_acceptance_evidence_policy(*, allow_paths: bool = True) -> dict[str, object]:
    rules = [
        {"id": "metadata-only-export", "label": "Exports are metadata-only", "required": True, "passed": True},
        {"id": "no-face-crops", "label": "Do not include face crops", "required": True, "passed": True},
        {"id": "no-embeddings", "label": "Do not include embeddings", "required": True, "passed": True},
        {"id": "local-paths-only", "label": "Evidence paths stay local", "required": True, "passed": bool(allow_paths)},
    ]
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_EVIDENCE_POLICY_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_acceptance_evidence_policy",
        "allow_paths": bool(allow_paths),
        "rules": rules,
        "summary": {
            "rule_count": len(rules),
            "failed_required_count": sum(1 for rule in rules if rule["required"] and not rule["passed"]),
            "metadata_only": True,
            "opens_window": False,
            "executes_commands": False,
            "local_only": True,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_EVIDENCE_POLICY_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_acceptance_evidence_policy"]
