from __future__ import annotations

USER_JOURNEY_SCHEMA_VERSION = "1.0"

_JOURNEYS = {
    "people-review": [
        ("open_bundle", "Open people review bundle"),
        ("review_groups", "Review detected groups"),
        ("fix_wrong_faces", "Reject or split wrong faces"),
        ("name_people", "Assign names"),
        ("preview_apply", "Preview catalog update"),
        ("apply_catalog", "Apply after confirmation"),
    ],
    "safe-cleanup": [
        ("select_profile", "Select profile"),
        ("preview", "Run preview"),
        ("review", "Review candidates"),
        ("apply", "Apply after confirmation"),
    ],
}


def build_user_journey_map(journey_id: str = "people-review", *, active_step_id: str | None = None) -> dict[str, object]:
    steps = _JOURNEYS.get(journey_id, _JOURNEYS["people-review"])
    active = active_step_id or steps[0][0]
    items = []
    active_seen = False
    for index, (step_id, label) in enumerate(steps, start=1):
        if step_id == active:
            active_seen = True
            state = "active"
        elif not active_seen:
            state = "complete"
        else:
            state = "pending"
        items.append({"index": index, "id": step_id, "label": label, "state": state})
    return {
        "schema_version": USER_JOURNEY_SCHEMA_VERSION,
        "kind": "qt_user_journey_map",
        "journey_id": journey_id,
        "active_step_id": active,
        "step_count": len(items),
        "steps": items,
    }


__all__ = ["USER_JOURNEY_SCHEMA_VERSION", "build_user_journey_map"]
