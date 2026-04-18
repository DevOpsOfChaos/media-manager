from __future__ import annotations

from pathlib import Path

from media_manager.similar_images import SimilarImageGroup, SimilarImageMember
from media_manager.similar_review import build_similar_review_report


def test_build_similar_review_report_adds_priority_and_match_kind() -> None:
    group = SimilarImageGroup(
        anchor_path=Path('/photos/keep.jpg'),
        members=[
            SimilarImageMember(path=Path('/photos/keep.jpg'), hash_hex='0f', distance=0),
            SimilarImageMember(path=Path('/photos/exact.jpg'), hash_hex='0f', distance=0),
            SimilarImageMember(path=Path('/photos/close.jpg'), hash_hex='0e', distance=1),
            SimilarImageMember(path=Path('/photos/broad.jpg'), hash_hex='f0', distance=8),
        ],
    )

    report = build_similar_review_report([group], keep_policy='first')

    assert report.group_count == 1
    assert report.keep_count == 1
    assert report.review_candidate_count == 3
    assert report.high_priority_count == 2
    assert report.low_priority_count == 1
    assert report.exact_hash_review_count == 1

    keep_row, first_candidate, second_candidate, third_candidate = report.rows
    assert keep_row.status == 'keep'
    assert keep_row.review_priority == 'keep'
    assert first_candidate.path == Path('/photos/exact.jpg')
    assert first_candidate.match_kind == 'exact-hash'
    assert first_candidate.review_priority == 'high'
    assert second_candidate.path == Path('/photos/close.jpg')
    assert second_candidate.match_kind == 'very-close'
    assert second_candidate.review_priority == 'high'
    assert third_candidate.path == Path('/photos/broad.jpg')
    assert third_candidate.match_kind == 'broad'
    assert third_candidate.review_priority == 'low'


def test_build_similar_review_report_orders_candidates_by_distance_then_path() -> None:
    group = SimilarImageGroup(
        anchor_path=Path('/photos/keep.jpg'),
        members=[
            SimilarImageMember(path=Path('/photos/c.jpg'), hash_hex='0d', distance=2),
            SimilarImageMember(path=Path('/photos/keep.jpg'), hash_hex='0f', distance=0),
            SimilarImageMember(path=Path('/photos/a.jpg'), hash_hex='0e', distance=1),
            SimilarImageMember(path=Path('/photos/b.jpg'), hash_hex='0e', distance=1),
        ],
    )

    report = build_similar_review_report([group], keep_policy='first')

    assert [row.path.name for row in report.rows] == ['keep.jpg', 'a.jpg', 'b.jpg', 'c.jpg']
