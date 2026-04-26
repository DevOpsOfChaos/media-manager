from __future__ import annotations

from collections.abc import Mapping
from typing import Any

DIALOG_MODEL_SCHEMA_VERSION = "1.0"

_DIALOG_TYPES = {"info", "warning", "confirm", "danger", "privacy"}


def normalize_dialog_type(value: str | None) -> str:
    normalized = str(value or "info").strip().lower().replace("_", "-")
    return normalized if normalized in _DIALOG_TYPES else "info"


def build_dialog_model(
    dialog_id: str,
    *,
    title: str,
    message: str,
    dialog_type: str = "info",
    confirm_label: str = "OK",
    cancel_label: str | None = None,
    requires_explicit_ack: bool = False,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    dtype = normalize_dialog_type(dialog_type)
    return {
        "schema_version": DIALOG_MODEL_SCHEMA_VERSION,
        "kind": "dialog_model",
        "dialog_id": dialog_id,
        "type": dtype,
        "title": title,
        "message": message,
        "confirm_label": confirm_label,
        "cancel_label": cancel_label,
        "requires_explicit_ack": bool(requires_explicit_ack or dtype in {"danger", "privacy"}),
        "metadata": dict(metadata or {}),
    }


def build_people_privacy_dialog(*, language: str = "en") -> dict[str, object]:
    if str(language).lower().startswith("de"):
        title = "Lokale Personendaten"
        message = "Face-Crops, Reports und Embeddings sind sensible biometrische Metadaten und sollten lokal/private bleiben."
        confirm = "Verstanden"
    else:
        title = "Local people data"
        message = "Face crops, reports, and embeddings are sensitive biometric metadata and should stay local/private."
        confirm = "I understand"
    return build_dialog_model(
        "people_privacy",
        title=title,
        message=message,
        dialog_type="privacy",
        confirm_label=confirm,
        cancel_label=None,
        requires_explicit_ack=True,
    )


def build_apply_confirmation_dialog(
    *,
    action_label: str,
    affected_count: int,
    risk_level: str = "high",
) -> dict[str, object]:
    count = max(0, int(affected_count))
    return build_dialog_model(
        "apply_confirmation",
        title="Confirm apply",
        message=f"{action_label} will affect {count} item(s). Review the preview before continuing.",
        dialog_type="danger" if risk_level in {"high", "destructive"} else "confirm",
        confirm_label="Apply",
        cancel_label="Cancel",
        requires_explicit_ack=risk_level in {"high", "destructive"},
        metadata={"affected_count": count, "risk_level": risk_level},
    )


__all__ = [
    "DIALOG_MODEL_SCHEMA_VERSION",
    "build_apply_confirmation_dialog",
    "build_dialog_model",
    "build_people_privacy_dialog",
    "normalize_dialog_type",
]
