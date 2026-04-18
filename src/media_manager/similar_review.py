from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from .similar_images import SimilarImageGroup

KeepPolicy = Literal["first", "newest", "oldest"]


@dataclass(slots=True, frozen=True)
class SimilarReviewRow:
    group_index: int
    group_size: int
    path: Path
    recommended_keep_path: Path
    status: str
    distance_to_keep: int
    hash_hex: str
    match_kind: str
    review_priority: str
    reason: str


@dataclass(slots=True)
class SimilarReviewReport:
    keep_policy: str
    rows: list[SimilarReviewRow] = field(default_factory=list)

    @property
    def group_count(self) -> int:
        return len({row.group_index for row in self.rows})

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def keep_count(self) -> int:
        return sum(1 for row in self.rows if row.status == "keep")

    @property
    def review_candidate_count(self) -> int:
        return sum(1 for row in self.rows if row.status == "review-candidate")

    @property
    def high_priority_count(self) -> int:
        return sum(1 for row in self.rows if row.review_priority == "high")

    @property
    def medium_priority_count(self) -> int:
        return sum(1 for row in self.rows if row.review_priority == "medium")

    @property
    def low_priority_count(self) -> int:
        return sum(1 for row in self.rows if row.review_priority == "low")

    @property
    def exact_hash_review_count(self) -> int:
        return sum(1 for row in self.rows if row.status == "review-candidate" and row.match_kind == "exact-hash")


def _hash_hex_to_int(hash_hex: str) -> int:
    return int(hash_hex, 16)


def _hamming_distance_from_hex(first_hash_hex: str, second_hash_hex: str) -> int:
    return (_hash_hex_to_int(first_hash_hex) ^ _hash_hex_to_int(second_hash_hex)).bit_count()


def _classify_match_kind(distance: int) -> str:
    if distance <= 0:
        return "exact-hash"
    if distance <= 2:
        return "very-close"
    if distance <= 5:
        return "close"
    return "broad"


def _classify_review_priority(distance: int) -> str:
    if distance <= 2:
        return "high"
    if distance <= 5:
        return "medium"
    return "low"


def _build_review_reason(match_kind: str, review_priority: str) -> str:
    if match_kind == "exact-hash":
        return "Matches the keep candidate on perceptual hash and should be reviewed first."
    if match_kind == "very-close":
        return f"Very close visual match to the keep candidate; review priority is {review_priority}."
    if match_kind == "close":
        return f"Close visual match to the keep candidate; review priority is {review_priority}."
    return f"Broader visual similarity to the keep candidate; review priority is {review_priority}."


def choose_similar_keep_path(group: SimilarImageGroup, policy: KeepPolicy) -> Path:
    if not group.members:
        raise ValueError("Similar image group must contain at least one member.")

    if policy == "first":
        member_paths = {member.path for member in group.members}
        if group.anchor_path in member_paths:
            return group.anchor_path
        return group.members[0].path

    dated_paths: list[tuple[float, Path]] = []
    for member in group.members:
        try:
            timestamp = member.path.stat().st_mtime
        except OSError:
            timestamp = 0.0
        dated_paths.append((timestamp, member.path))

    if policy == "newest":
        return max(dated_paths, key=lambda item: (item[0], str(item[1]).lower()))[1]
    if policy == "oldest":
        return min(dated_paths, key=lambda item: (item[0], str(item[1]).lower()))[1]

    raise ValueError(f"Unsupported similar-image keep policy: {policy}")


def build_similar_review_report(
    similar_groups: list[SimilarImageGroup],
    *,
    keep_policy: KeepPolicy = "first",
) -> SimilarReviewReport:
    report = SimilarReviewReport(keep_policy=keep_policy)

    for group_index, group in enumerate(similar_groups, start=1):
        if len(group.members) < 2:
            continue

        keep_path = choose_similar_keep_path(group, keep_policy)
        keep_member = next((member for member in group.members if member.path == keep_path), None)
        if keep_member is None:
            continue

        candidate_rows: list[SimilarReviewRow] = []
        for member in group.members:
            if member.path == keep_path:
                continue
            distance = _hamming_distance_from_hex(keep_member.hash_hex, member.hash_hex)
            match_kind = _classify_match_kind(distance)
            review_priority = _classify_review_priority(distance)
            candidate_rows.append(
                SimilarReviewRow(
                    group_index=group_index,
                    group_size=len(group.members),
                    path=member.path,
                    recommended_keep_path=keep_path,
                    status="review-candidate",
                    distance_to_keep=distance,
                    hash_hex=member.hash_hex,
                    match_kind=match_kind,
                    review_priority=review_priority,
                    reason=_build_review_reason(match_kind, review_priority),
                )
            )

        candidate_rows.sort(key=lambda row: (row.distance_to_keep, str(row.path).lower()))
        report.rows.append(
            SimilarReviewRow(
                group_index=group_index,
                group_size=len(group.members),
                path=keep_member.path,
                recommended_keep_path=keep_path,
                status="keep",
                distance_to_keep=0,
                hash_hex=keep_member.hash_hex,
                match_kind="keep",
                review_priority="keep",
                reason=f"Recommended keep candidate using '{keep_policy}' policy.",
            )
        )
        report.rows.extend(candidate_rows)

    return report
