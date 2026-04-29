from __future__ import annotations

import sys

from media_manager.core.gui_qt_guarded_runtime_smoke_integration import build_guarded_qt_runtime_smoke_integration
from media_manager.core.gui_qt_runtime_smoke_guarded_snapshot import build_qt_runtime_smoke_guarded_snapshot
from media_manager.core.gui_qt_runtime_smoke_qt_backend_probe import build_qt_runtime_smoke_qt_backend_probe
from media_manager.core.gui_shell_model import build_gui_shell_model


def test_backend_probe_does_not_import_pyside6() -> None:
    sys.modules.pop("PySide6", None)

    probe = build_qt_runtime_smoke_qt_backend_probe()

    assert probe["imports_backend"] is False
    assert probe["opens_window"] is False
    assert "PySide6" not in sys.modules


def test_guardrails_and_snapshot_are_stable_metadata_only() -> None:
    bundle = build_guarded_qt_runtime_smoke_integration(build_gui_shell_model())

    guardrails = bundle["guardrails"]
    snapshot_a = build_qt_runtime_smoke_guarded_snapshot(bundle)
    snapshot_b = build_qt_runtime_smoke_guarded_snapshot(bundle)

    assert guardrails["valid"] is True
    assert guardrails["summary"]["opens_window"] is False
    assert snapshot_a["payload_hash"] == snapshot_b["payload_hash"]
    assert len(snapshot_a["payload_hash"]) == 64
