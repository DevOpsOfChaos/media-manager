from __future__ import annotations

from .gui_i18n import translate

ONBOARDING_SCHEMA_VERSION = "1.0"


def build_onboarding_state(*, language: str = "en", dismissed: bool = False) -> dict[str, object]:
    return {
        "schema_version": ONBOARDING_SCHEMA_VERSION,
        "dismissed": bool(dismissed),
        "title": translate("onboarding.title", language=language),
        "steps": [
            {"id": "preview_first", "text": translate("onboarding.step1", language=language), "risk_level": "safe"},
            {"id": "review_before_apply", "text": translate("onboarding.step2", language=language), "risk_level": "medium"},
            {"id": "privacy", "text": translate("onboarding.step3", language=language), "risk_level": "privacy"},
        ],
    }


__all__ = ["ONBOARDING_SCHEMA_VERSION", "build_onboarding_state"]
