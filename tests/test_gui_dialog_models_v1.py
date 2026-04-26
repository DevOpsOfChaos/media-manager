from __future__ import annotations

from media_manager.core.gui_dialog_models import build_apply_confirmation_dialog, build_dialog_model, build_people_privacy_dialog


def test_privacy_dialog_requires_ack_and_is_bilingual() -> None:
    dialog = build_people_privacy_dialog(language="de")

    assert dialog["type"] == "privacy"
    assert dialog["requires_explicit_ack"] is True
    assert "Personendaten" in dialog["title"]


def test_apply_confirmation_is_danger_for_high_risk() -> None:
    dialog = build_apply_confirmation_dialog(action_label="Apply people review", affected_count=4)

    assert dialog["type"] == "danger"
    assert dialog["metadata"]["affected_count"] == 4
    assert dialog["cancel_label"] == "Cancel"


def test_unknown_dialog_type_falls_back_to_info() -> None:
    dialog = build_dialog_model("x", title="T", message="M", dialog_type="nonsense")
    assert dialog["type"] == "info"
