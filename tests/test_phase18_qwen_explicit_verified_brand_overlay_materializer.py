from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from engine.intelligence.qwen_image_explicit_verified_brand_overlay_materializer import (
    BrandOverlayMaterializationError,
    CONTRACT,
    materialize_explicit_verified_brand_overlay,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ExplicitVerifiedBrandOverlayMaterializerTests(unittest.TestCase):
    def _fixture(self, root: Path, *, tile_mode: str = "RGBA") -> dict:
        candidate = root / "candidate.png"
        tile = root / "brand.png"
        Image.new("RGB", (320, 180), (12, 18, 24)).save(candidate)
        if tile_mode == "RGBA":
            image = Image.new("RGBA", (80, 24), (0, 0, 0, 0))
            for x in range(8, 72):
                for y in range(5, 19):
                    image.putpixel((x, y), (240, 240, 240, 220))
        else:
            image = Image.new("RGB", (80, 24), (240, 240, 240))
        image.save(tile)
        return {
            "contract": CONTRACT,
            "story_sha256": "a" * 64,
            "layer_name": "pul7sar_brand",
            "layer_source": "verified_asset",
            "owner_brand_approval_required": True,
            "candidate": {
                "path": "candidate.png",
                "sha256": _sha(candidate),
                "size_bytes": candidate.stat().st_size,
                "width": 320,
                "height": 180,
            },
            "brand_tile": {
                "path": "brand.png",
                "sha256": _sha(tile),
                "size_bytes": tile.stat().st_size,
            },
            "placement": {"x": 220, "y": 140},
        }

    def test_materializes_exact_tile_without_granting_brand_or_publication_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._fixture(root)
            output = root / "full_brand_overlay.png"
            receipt = materialize_explicit_verified_brand_overlay(manifest, output, root)
            self.assertTrue(receipt.overlay_materialized)
            self.assertFalse(receipt.brand_publication_approved)
            self.assertTrue(receipt.owner_brand_approval_required)
            self.assertFalse(receipt.composition_executed)
            self.assertFalse(receipt.semantic_approved)
            self.assertFalse(receipt.human_visual_review_approved)
            self.assertFalse(receipt.golden_quality_approved)
            self.assertFalse(receipt.genuine_golden_png_created)
            self.assertFalse(receipt.publication_ready)
            self.assertFalse(receipt.authoritative)
            with Image.open(output) as rendered, Image.open(root / "brand.png") as tile:
                self.assertEqual(rendered.mode, "RGBA")
                self.assertEqual(rendered.size, (320, 180))
                self.assertEqual(rendered.crop((220, 140, 300, 164)).tobytes(), tile.tobytes())
                self.assertEqual(rendered.getpixel((0, 0))[3], 0)

    def test_rejects_non_rgba_brand_tile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._fixture(root, tile_mode="RGB")
            with self.assertRaisesRegex(BrandOverlayMaterializationError, "native_rgba_png"):
                materialize_explicit_verified_brand_overlay(manifest, root / "out.png", root)

    def test_rejects_brand_byte_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._fixture(root)
            manifest["brand_tile"]["sha256"] = "b" * 64
            with self.assertRaisesRegex(BrandOverlayMaterializationError, "brand_tile_byte_drift"):
                materialize_explicit_verified_brand_overlay(manifest, root / "out.png", root)

    def test_rejects_candidate_byte_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._fixture(root)
            manifest["candidate"]["sha256"] = "c" * 64
            with self.assertRaisesRegex(BrandOverlayMaterializationError, "candidate_byte_drift"):
                materialize_explicit_verified_brand_overlay(manifest, root / "out.png", root)

    def test_rejects_out_of_bounds_placement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._fixture(root)
            manifest["placement"] = {"x": 300, "y": 170}
            with self.assertRaisesRegex(BrandOverlayMaterializationError, "out_of_bounds"):
                materialize_explicit_verified_brand_overlay(manifest, root / "out.png", root)

    def test_rejects_wrong_ownership(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._fixture(root)
            manifest["layer_source"] = "deterministic"
            with self.assertRaisesRegex(BrandOverlayMaterializationError, "unsupported_layer_source"):
                materialize_explicit_verified_brand_overlay(manifest, root / "out.png", root)

    def test_requires_owner_brand_approval_to_remain_explicitly_pending(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._fixture(root)
            manifest["owner_brand_approval_required"] = False
            with self.assertRaisesRegex(BrandOverlayMaterializationError, "owner_brand_approval"):
                materialize_explicit_verified_brand_overlay(manifest, root / "out.png", root)

    def test_source_contains_no_generation_resize_network_or_authority_shortcut(self) -> None:
        source = Path("engine/intelligence/qwen_image_explicit_verified_brand_overlay_materializer.py").read_text()
        forbidden = (
            "QwenImagePipeline",
            ".resize(",
            "requests.",
            "http://",
            "https://",
            "brand_publication_approved=True",
            "semantic_approved=True",
            "genuine_golden_png_created=True",
            "publication_ready=True",
        )
        for token in forbidden:
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
