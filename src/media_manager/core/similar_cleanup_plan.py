from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from media_manager.similar_images import SimilarImageGroup

from .similar_assets import build_similar_group_id


@dataclass(slots=True)
class SimilarPlannedRemoval:
    group_id: str
    keep_path: Path
    remove_path: Path
    hash_hex: str
    distance: int


@dataclass(slots=True)
class SimilarCleanupPlan:
    total_groups: int = 0
    resolved_groups: int = 0
    unresolved_groups: int = 0
    keep_paths: list[Path] = field(default_factory=list)
    planned_removals: list[SimilarPlannedRemoval] = field(default_factory=list)
    skipped_paths: list[Path] = field(default_factory=list)
    estimated_reclaimable_bytes: int = 0

    @property
    def ready_for_apply(self) -> bool:
        return self.unresolved_groups == 0 and len(self.planned_removals) > 0


def build_similar_cleanup_plan(
    groups: list[SimilarImageGroup],
    decisions: dict[str, dict[str, str]],
) -> SimilarCleanupPlan:
    """Build a delete-only cleanup plan from per-member similar-image decisions."""

    plan = SimilarCleanupPlan(total_groups=len(groups))

    for group in groups:
        group_id = build_similar_group_id(group)
        group_decisions = decisions.get(group_id, {})
        keep_count = 0
        remove_count = 0
        has_unresolved = False

        for member in group.members:
            path_str = str(member.path)
            decision = group_decisions.get(path_str)
            if decision is None and member.path == group.anchor_path:
                decision = "keep"

            if decision == "keep":
                keep_count += 1
                plan.keep_paths.append(member.path)
            elif decision == "remove":
                remove_count += 1
                try:
                    file_size = member.path.stat().st_size
                except OSError:
                    file_size = 0
                plan.planned_removals.append(
                    SimilarPlannedRemoval(
                        group_id=group_id,
                        keep_path=group.anchor_path,
                        remove_path=member.path,
                        hash_hex=member.hash_hex,
                        distance=member.distance,
                    )
                )
                plan.estimated_reclaimable_bytes += file_size
            elif decision == "skip":
                plan.skipped_paths.append(member.path)
            else:
                has_unresolved = True

        if keep_count >= 1 and remove_count >= 1 and not has_unresolved:
            plan.resolved_groups += 1
        elif has_unresolved:
            plan.unresolved_groups += 1
        elif keep_count >= 1 and remove_count == 0:
            plan.resolved_groups += 1

    return plan


__all__ = [
    "SimilarCleanupPlan",
    "SimilarPlannedRemoval",
    "build_similar_cleanup_plan",
]
