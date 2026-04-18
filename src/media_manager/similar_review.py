from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from .similar_images import SimilarImageGroup

KeepPolicy = Literal["first", "newest", "oldest"]


@dataclass(slots=True, frozen=True)
class SimilarReviewRow:
    group_index: int
    path: Path
    recommended_keep_path: Path
    status: str
    distance_to_keep: int
    hash_hex: str
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


def _hash_hex_to_int(hash_hex: str) -> int:
    return int(hash_hex, 16)


def _hamming_distance_from_hex(first_hash_hex: str, second_hash_hex: str) -> int:
    return (_hash_hex_to_int(first_hash_hex) ^ _hash_hex_to_int(second_hash_hex)).bit_count()


def choose_similar_keep_path(group: SimilarImageGroup, policy: KeepPolicy) -> Path:
    if not group.members:
        raise ValueError("Similar image group must contain at least one member.")

    if policy == "first":
        return min((member.path for member in group.members), key=lambda path: str(path).lower())

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

        ordered_members = sorted(group.members, key=lambda member: str(member.path).lower())
        for member in ordered_members:
            if member.path == keep_path:
                report.rows.append(
                    SimilarReviewRow(
                        group_index=group_index,
                        path=member.path,
                        recommended_keep_path=keep_path,
                        status="keep",
                        distance_to_keep=0,
                        hash_hex=member.hash_hex,
                        reason=f"Recommended keep candidate using '{keep_policy}' policy.",
                    )
                )
                continue

            report.rows.append(
                SimilarReviewRow(
                    group_index=group_index,
                    path=member.path,
                    recommended_keep_path=keep_path,
                    status="review-candidate",
                    distance_to_keep=_hamming_distance_from_hex(keep_member.hash_hex, member.hash_hex),
                    hash_hex=member.hash_hex,
                    reason="Visually similar image candidate that should be reviewed before removal.",
                )
            )

    return report
