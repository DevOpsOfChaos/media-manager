from __future__ import annotations

import json
from pathlib import Path
import tempfile

from PIL import Image

from src.media_manager.core.similar_assets import (
    build_similar_group_id,
    build_similar_image_assets,
    write_similar_image_asset_manifest,
)
from src.media_manager.similar_images import (
    SimilarImageGroup,
    SimilarImageMember,
)


def _make_test_image(path: Path, size: tuple[int, int] = (100, 80), color: str = "red") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color).save(path, format="JPEG")


def _make_group(anchor_path: Path, member_count: int = 3) -> SimilarImageGroup:
    members: list[SimilarImageMember] = []
    for i in range(member_count):
        p = anchor_path.parent / f"member_{i}.jpg" if i > 0 else anchor_path
        members.append(
            SimilarImageMember(
                path=p,
                hash_hex=f"{i:016x}",
                distance=i,
                width=100,
                height=80,
            )
        )
    return SimilarImageGroup(anchor_path=anchor_path, members=members)


class TestBuildSimilarGroupId:
    def test_uses_anchor_stem_and_anchor_hash(self):
        anchor = Path("/photos/IMG_0001.jpg")
        group = SimilarImageGroup(
            anchor_path=anchor,
            members=[
                SimilarImageMember(path=anchor, hash_hex="abcdef1234567890", distance=0),
                SimilarImageMember(path=Path("/photos/IMG_0002.jpg"), hash_hex="1111111111111111", distance=4),
            ],
        )
        gid = build_similar_group_id(group)
        assert gid.startswith("similar-")
        assert "IMG_0001" in gid
        assert "abcdef123456" in gid

    def test_stable_for_same_input(self):
        anchor = Path("/photos/IMG_0001.jpg")
        group = SimilarImageGroup(
            anchor_path=anchor,
            members=[SimilarImageMember(path=anchor, hash_hex="aaaa00001111", distance=0)],
        )
        assert build_similar_group_id(group) == build_similar_group_id(group)


class TestBuildSimilarImageAssets:
    def test_generates_thumbnails_for_groups(self):
        with tempfile.TemporaryDirectory() as tmp:
            src_dir = Path(tmp) / "source"
            asset_dir = Path(tmp) / "assets"
            anchor = src_dir / "photo_a.jpg"
            member2 = src_dir / "photo_b.jpg"
            member3 = src_dir / "photo_c.jpg"
            _make_test_image(anchor, (200, 150), "red")
            _make_test_image(member2, (200, 150), "blue")
            _make_test_image(member3, (200, 150), "green")

            group = SimilarImageGroup(
                anchor_path=anchor,
                members=[
                    SimilarImageMember(path=anchor, hash_hex="abc000000001", distance=0, width=200, height=150),
                    SimilarImageMember(path=member2, hash_hex="abc000000002", distance=3, width=200, height=150),
                    SimilarImageMember(path=member3, hash_hex="abc000000003", distance=5, width=200, height=150),
                ],
            )

            manifest = build_similar_image_assets(
                similar_groups=[group],
                asset_dir=str(asset_dir),
                thumbnail_size=256,
                overwrite=True,
            )

            assert manifest["schema_version"] == 1
            assert manifest["kind"] == "similar_image_assets"
            assert manifest["summary"]["asset_count"] == 3
            assert manifest["summary"]["generated_count"] == 3
            assert manifest["summary"]["error_count"] == 0
            assert manifest["summary"]["group_count"] == 1

            anchor_asset = next(a for a in manifest["assets"] if a["is_anchor"])
            assert anchor_asset["status"] == "ok"
            assert anchor_asset["distance"] == 0
            assert Path(anchor_asset["asset_path"]).exists()

            candidate = next(a for a in manifest["assets"] if not a["is_anchor"])
            assert candidate["distance"] > 0
            assert candidate["hash_hex"] != ""

    def test_handles_missing_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            asset_dir = Path(tmp) / "assets"
            missing = Path(tmp) / "source" / "nope.jpg"
            group = SimilarImageGroup(
                anchor_path=missing,
                members=[SimilarImageMember(path=missing, hash_hex="dead00000001", distance=0)],
            )
            manifest = build_similar_image_assets(
                similar_groups=[group],
                asset_dir=str(asset_dir),
                overwrite=True,
            )
            assert manifest["summary"]["error_count"] == 1
            assert manifest["assets"][0]["status"] == "error"
            assert manifest["assets"][0]["error"] == "source_image_missing"

    def test_deterministic_group_id_from_same_input(self):
        anchor = Path("/photos/x.jpg")
        group = SimilarImageGroup(
            anchor_path=anchor,
            members=[SimilarImageMember(path=anchor, hash_hex="abcdabcdabcd", distance=0)],
        )
        id1 = build_similar_group_id(group)
        id2 = build_similar_group_id(group)
        assert id1 == id2

    def test_manifest_written_and_readable(self):
        with tempfile.TemporaryDirectory() as tmp:
            src_dir = Path(tmp) / "source"
            asset_dir = Path(tmp) / "assets"
            anchor = src_dir / "img.jpg"
            _make_test_image(anchor, (50, 50), "red")
            group = SimilarImageGroup(
                anchor_path=anchor,
                members=[SimilarImageMember(path=anchor, hash_hex="eeee00000001", distance=0)],
            )
            manifest = build_similar_image_assets(similar_groups=[group], asset_dir=str(asset_dir))
            manifest_path = Path(tmp) / "manifest.json"
            write_similar_image_asset_manifest(manifest_path, manifest)

            with open(manifest_path) as fh:
                reloaded = json.load(fh)
            assert reloaded["kind"] == "similar_image_assets"
            assert len(reloaded["assets"]) == 1

    def test_thumbnail_respects_max_size(self):
        with tempfile.TemporaryDirectory() as tmp:
            src_dir = Path(tmp) / "source"
            asset_dir = Path(tmp) / "assets"
            img = src_dir / "big.jpg"
            _make_test_image(img, (1200, 900), "red")
            group = SimilarImageGroup(
                anchor_path=img,
                members=[SimilarImageMember(path=img, hash_hex="fff000000001", distance=0)],
            )
            manifest = build_similar_image_assets(similar_groups=[group], asset_dir=str(asset_dir), thumbnail_size=256)

            asset = manifest["assets"][0]
            with Image.open(asset["asset_path"]) as thumb:
                assert thumb.width <= 256
                assert thumb.height <= 256
