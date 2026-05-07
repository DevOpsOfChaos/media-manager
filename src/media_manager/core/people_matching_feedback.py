from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


FEEDBACK_SCHEMA_VERSION = 1


@dataclass(slots=True)
class FaceFeedbackEntry:
    face_id: str
    suggested_person_id: str | None = None
    suggested_name: str | None = None
    user_person_id: str | None = None
    user_name: str | None = None
    user_action: str = "none"
    corrected: bool = False
    recorded_at_utc: str = ""


@dataclass(slots=True)
class MatchingFeedbackStore:
    entries: list[FaceFeedbackEntry] = field(default_factory=list)
    correction_counts: dict[str, int] = field(default_factory=dict)
    total_suggestions: int = 0
    total_corrections: int = 0
    accuracy_ratio: float = 1.0

    @property
    def needs_improvement(self) -> bool:
        return self.total_suggestions >= 5 and self.accuracy_ratio < 0.7

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": FEEDBACK_SCHEMA_VERSION,
            "kind": "people_matching_feedback",
            "total_suggestions": self.total_suggestions,
            "total_corrections": self.total_corrections,
            "accuracy_ratio": round(self.accuracy_ratio, 4),
            "needs_improvement": self.needs_improvement,
            "correction_counts": dict(sorted(self.correction_counts.items())),
            "recent_entries": [
                {
                    "face_id": entry.face_id,
                    "suggested_name": entry.suggested_name,
                    "user_name": entry.user_name,
                    "user_action": entry.user_action,
                    "corrected": entry.corrected,
                    "recorded_at_utc": entry.recorded_at_utc,
                }
                for entry in self.entries[-20:]
            ],
            "recommendation": (
                "Consider adding more reference photos for frequently corrected persons."
                if self.needs_improvement
                else "Face matching accuracy is good. Keep adding reference photos to maintain quality."
            ),
        }


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def record_face_feedback(
    store: MatchingFeedbackStore,
    *,
    face_id: str,
    suggested_person_id: str | None = None,
    suggested_name: str | None = None,
    user_person_id: str | None = None,
    user_name: str | None = None,
    user_action: str = "none",
) -> MatchingFeedbackStore:
    corrected = False
    if suggested_person_id and user_person_id and suggested_person_id != user_person_id:
        corrected = True
        store.correction_counts[suggested_person_id] = store.correction_counts.get(suggested_person_id, 0) + 1
    if suggested_name and user_name and suggested_name != user_name:
        corrected = True

    entry = FaceFeedbackEntry(
        face_id=face_id,
        suggested_person_id=suggested_person_id,
        suggested_name=suggested_name,
        user_person_id=user_person_id,
        user_name=user_name,
        user_action=user_action,
        corrected=corrected,
        recorded_at_utc=_now_utc(),
    )
    store.entries.append(entry)
    if store.entries and user_action != "none":
        store.total_suggestions += 1
    if corrected:
        store.total_corrections += 1
    if store.total_suggestions > 0:
        store.accuracy_ratio = max(0.0, 1.0 - (store.total_corrections / store.total_suggestions))
    return store


def load_matching_feedback(path: str | Path) -> MatchingFeedbackStore:
    resolved = Path(path)
    if not resolved.exists():
        return MatchingFeedbackStore()
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except Exception:
        return MatchingFeedbackStore()
    if not isinstance(payload, dict):
        return MatchingFeedbackStore()

    store = MatchingFeedbackStore(
        total_suggestions=int(payload.get("total_suggestions", 0)),
        total_corrections=int(payload.get("total_corrections", 0)),
        accuracy_ratio=float(payload.get("accuracy_ratio", 1.0)),
    )
    correction_counts = payload.get("correction_counts")
    if isinstance(correction_counts, dict):
        store.correction_counts = {str(k): int(v) for k, v in correction_counts.items() if isinstance(v, (int, float))}

    recent = payload.get("recent_entries")
    if isinstance(recent, list):
        for item in recent[-50:]:
            if isinstance(item, dict):
                store.entries.append(
                    FaceFeedbackEntry(
                        face_id=str(item.get("face_id", "")),
                        suggested_person_id=item.get("suggested_person_id") if isinstance(item.get("suggested_person_id"), str) else None,
                        suggested_name=item.get("suggested_name") if isinstance(item.get("suggested_name"), str) else None,
                        user_person_id=item.get("user_person_id") if isinstance(item.get("user_person_id"), str) else None,
                        user_name=item.get("user_name") if isinstance(item.get("user_name"), str) else None,
                        user_action=str(item.get("user_action", "none")),
                        corrected=bool(item.get("corrected")),
                        recorded_at_utc=str(item.get("recorded_at_utc") or ""),
                    )
                )
    return store


def save_matching_feedback(path: str | Path, store: MatchingFeedbackStore) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(store.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output


def suggest_tolerance_adjustment(store: MatchingFeedbackStore, current_tolerance: float = 0.6) -> dict[str, object]:
    if store.total_suggestions < 5:
        return {"action": "keep", "suggested_tolerance": current_tolerance, "reason": "Not enough feedback data to adjust tolerance."}
    if store.accuracy_ratio >= 0.85:
        return {"action": "keep", "suggested_tolerance": current_tolerance, "reason": "Matching accuracy is excellent."}
    if store.accuracy_ratio < 0.6:
        suggested = round(min(0.5, current_tolerance - 0.05), 2)
        return {"action": "decrease", "suggested_tolerance": suggested, "reason": "High correction rate. Try a stricter tolerance to reduce false matches."}
    return {"action": "keep", "suggested_tolerance": current_tolerance, "reason": "Accuracy is acceptable. Add more reference photos to improve further."}


__all__ = [
    "FaceFeedbackEntry",
    "MatchingFeedbackStore",
    "load_matching_feedback",
    "record_face_feedback",
    "save_matching_feedback",
    "suggest_tolerance_adjustment",
]
