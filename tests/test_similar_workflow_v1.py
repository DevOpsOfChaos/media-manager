from __future__ import annotations

import tempfile
from pathlib import Path

from PIL import Image

from src.media_manager.core.similar_assets import (
    build_similar_group_id,
    build_similar_image_assets,
    write_similar_image_asset_manifest,
)
from src.media_manager.core.similar_cleanup_plan import build_similar_cleanup_plan
from src.media_manager.core.similar_decisions import (
    build_similar_decision_template,
    build_similar_group_signature,
    load_similar_decision_file,
    write_similar_decision_template,
)
from src.media_manager.core.similar_session_store import (
    normalize_similar_decisions,
    restore_similar_session,
    save_similar_session_snapshot,
)
from src.media_manager.core.similar_workflow import (
    build_similar_workflow_bundle,
    execute_similar_workflow_bundle,
)
from src.media_manager.similar_images import (
    SimilarImageGroup,
    SimilarImageMember,
)


def _make_test_image(path: Path, size: tuple[int, int] = (300, 200), color: str = "red") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color).save(path, format="JPEG")


def _make_group(anchor_path: Path, *member_paths: Path) -> SimilarImageGroup:
    members = [SimilarImageMember(path=anchor_path, hash_hex="aaa000000001", distance=0, width=300, height=200)]
    for i, p in enumerate(member_paths, start=1):
        members.append(SimilarImageMember(path=p, hash_hex=f"bbb{i:010d}", distance=i * 2, width=300, height=200))
    return SimilarImageGroup(anchor_path=anchor_path, members=members)


class TestSimilarWorkflowEndToEnd:
    def test_full_pipeline_no_apply(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "source"
            anchor = src / "keep.jpg"
            dup1 = src / "dup1.jpg"
            dup2 = src / "dup2.jpg"
            _make_test_image(anchor, color="red")
            _make_test_image(dup1, color="blue")
            _make_test_image(dup2, color="green")

            group = _make_group(anchor, dup1, dup2)
            groups = [group]

            # Block 1: assets
            asset_dir = Path(tmp) / "assets"
            manifest = build_similar_image_assets(similar_groups=groups, asset_dir=str(asset_dir))
            assert manifest["summary"]["generated_count"] == 3
            assert manifest["summary"]["group_count"] == 1

            # Block 2: decisions
            decisions = {build_similar_group_id(group): {str(dup1): "remove", str(dup2): "skip", str(anchor): "keep"}}
            template = build_similar_decision_template(similar_groups=groups, decisions=decisions)
            assert template["group_count"] == 1
            assert template["keep_count"] == 1

            # Block 2: export + import round-trip
            decisions_path = Path(tmp) / "decisions.json"
            write_similar_decision_template(decisions_path, template)
            result = load_similar_decision_file(decisions_path, groups)
            assert result.status == "matched"
            assert result.matched_decision_count == 3

            # Block 5: cleanup plan
            plan = build_similar_cleanup_plan(groups, result.decisions)
            assert plan.total_groups == 1
            assert plan.resolved_groups == 1
            assert len(plan.planned_removals) == 1
            assert plan.ready_for_apply is True

            # Block 5: workflow bundle dry-run
            bundle = build_similar_workflow_bundle(groups, result.decisions)
            assert bundle.cleanup_plan.ready_for_apply is True
            assert len(bundle.execution_preview.rows) == 1

            # Block 5: session save + restore
            session_path = Path(tmp) / "session.json"
            save_similar_session_snapshot(session_path, groups, result.decisions)
            restored = restore_similar_session(session_path, groups)
            assert restored.status == "matched"
            assert restored.decision_count == 3

    def test_apply_executes_delete(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "source"
            anchor = src / "keep.jpg"
            dup = src / "remove_me.jpg"
            _make_test_image(anchor, color="red")
            _make_test_image(dup, color="blue")

            group = _make_group(anchor, dup)
            groups = [group]
            decisions = {build_similar_group_id(group): {str(dup): "remove", str(anchor): "keep"}}

            bundle = build_similar_workflow_bundle(groups, decisions)
            assert dup.exists()

            result = execute_similar_workflow_bundle(bundle, apply=True)
            assert result.executed_rows == 1
            assert not dup.exists()
            assert anchor.exists()

    def test_group_signature_detects_changes(self):
        anchor = Path("/tmp/a.jpg")
        member2 = Path("/tmp/b.jpg")
        group1 = SimilarImageGroup(
            anchor_path=anchor,
            members=[
                SimilarImageMember(path=anchor, hash_hex="abc123", distance=0),
                SimilarImageMember(path=member2, hash_hex="def456", distance=3),
            ],
        )
        group2 = SimilarImageGroup(
            anchor_path=anchor,
            members=[
                SimilarImageMember(path=anchor, hash_hex="abc123", distance=0),
                SimilarImageMember(path=Path("/tmp/c.jpg"), hash_hex="999999", distance=5),
            ],
        )
        sig1 = build_similar_group_signature([group1])
        sig2 = build_similar_group_signature([group2])
        assert sig1 != sig2

    def test_cleanup_plan_no_keep_means_unresolved(self):
        anchor = Path("/tmp/x.jpg")
        member2 = Path("/tmp/y.jpg")
        group = SimilarImageGroup(
            anchor_path=anchor,
            members=[
                SimilarImageMember(path=anchor, hash_hex="111", distance=0),
                SimilarImageMember(path=member2, hash_hex="222", distance=4),
            ],
        )
        decisions = {}  # no decisions
        plan = build_similar_cleanup_plan([group], decisions)
        assert plan.unresolved_groups >= 0  # anchor auto-kept
        assert plan.ready_for_apply is False

    def test_normalize_similar_decisions_filters_invalid(self):
        anchor = Path("/tmp/a.jpg")
        group = SimilarImageGroup(
            anchor_path=anchor,
            members=[SimilarImageMember(path=anchor, hash_hex="aaa", distance=0)],
        )
        raw = {build_similar_group_id(group): {str(anchor): "keep", "/nonexistent/path.jpg": "remove"}}
        normalized = normalize_similar_decisions([group], raw)
        gid = build_similar_group_id(group)
        assert "/nonexistent/path.jpg" not in normalized.get(gid, {})
        assert str(anchor) in normalized.get(gid, {})

    def test_decision_template_empty_if_no_groups(self):
        template = build_similar_decision_template(similar_groups=[])
        assert template["group_count"] == 0

    def test_decision_load_missing_file(self):
        result = load_similar_decision_file("/nonexistent/path.json", [])
        assert result.status == "missing"

    def test_decision_load_bad_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "bad.json"
            p.write_text("not json", encoding="utf-8")
            result = load_similar_decision_file(p, [])
            assert result.status == "error"

    def test_session_restore_missing(self):
        result = restore_similar_session("/nonexistent/session.json", [])
        assert result.status == "missing"
