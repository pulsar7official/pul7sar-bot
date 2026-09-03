from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image

from engine.intelligence.qwen_image_explicit_overlay_materializer import (
    FULL_CANVAS_OVERLAY_CONTRACT,
    MANIFEST_SCHEMA,
    build_explicit_overlay_materialization,
    verify_explicit_overlay_materialization,
)


def _binding(path: Path, root: Path) -> dict[str, object]:
    raw = path.read_bytes()
    return {
        "repository_relative_path": path.relative_to(root).as_posix(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
    }


class ExplicitOverlayMaterializerTests(unittest.TestCase):
    def _fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path, Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        assets = root / "assets"
        manifests = root / "manifests"
        runs = root / "runs"
        assets.mkdir()
        manifests.mkdir()
        runs.mkdir()

        candidate = assets / "candidate.png"
        Image.new("RGB", (320, 180), (12, 20, 28)).save(candidate, format="PNG")
        title = assets / "title_tile.png"
        tile = Image.new("RGBA", (100, 24), (0, 0, 0, 0))
        for x in range(10, 90):
            for y in range(5, 19):
                tile.putpixel((x, y), (245, 245, 245, 230))
        tile.save(title, format="PNG")
        label = assets / "label_tile.png"
        Image.new("RGBA", (50, 16), (220, 20, 20, 180)).save(label, format="PNG")

        manifest = {
            "schema": MANIFEST_SCHEMA,
            "story_snapshot_sha256": "a" * 64,
            "candidate_png": _binding(candidate, root),
            "layer_name": "editorial_typography",
            "layer_source": "deterministic",
            "renderer_contract": FULL_CANVAS_OVERLAY_CONTRACT,
            "canvas": {"width": 320, "height": 180},
            "tiles": [
                {"source_file": _binding(title, root), "x": 30, "y": 110, "z_index": 10},
                {"source_file": _binding(label, root), "x": 30, "y": 140, "z_index": 20},
            ],
        }
        manifest_path = manifests / "explicit_typography_layout.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return temp, root, manifest_path

    def test_materializes_exact_full_canvas_rgba_without_downstream_authority(self) -> None:
        temp, root, manifest_path = self._fixture()
        self.addCleanup(temp.cleanup)
        run = build_explicit_overlay_materialization(manifest_path, root / "runs" / "cs332", repo_root=root)
        receipt = verify_explicit_overlay_materialization(run.receipt_path, repo_root=root)
        self.assertTrue(receipt["overlay_materialized"])
        self.assertEqual(receipt["layer_name"], "editorial_typography")
        self.assertEqual(receipt["renderer_contract"], FULL_CANVAS_OVERLAY_CONTRACT)
        for field in (
            "composition_executed",
            "composed_visual_approved",
            "semantic_approved",
            "human_visual_review_approved",
            "genuine_golden_png_created",
            "golden_quality_approved",
            "publication_ready",
        ):
            self.assertFalse(receipt[field])
        with Image.open(run.overlay_path) as image:
            self.assertEqual(image.format, "PNG")
            self.assertEqual(image.mode, "RGBA")
            self.assertEqual(image.size, (320, 180))
            self.assertEqual(image.getpixel((35, 115))[3], 0)
            self.assertGreater(image.getpixel((45, 120))[3], 0)
            self.assertGreater(image.getpixel((35, 145))[3], 0)

    def test_rejects_out_of_bounds_geometry_without_output_directory(self) -> None:
        temp, root, manifest_path = self._fixture()
        self.addCleanup(temp.cleanup)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["tiles"][0]["x"] = 250
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        output = root / "runs" / "blocked"
        with self.assertRaisesRegex(ValueError, "TILE_OUT_OF_BOUNDS"):
            build_explicit_overlay_materialization(manifest_path, output, repo_root=root)
        self.assertFalse(output.exists())

    def test_rejects_non_rgba_tile(self) -> None:
        temp, root, manifest_path = self._fixture()
        self.addCleanup(temp.cleanup)
        rgb = root / "assets" / "rgb.png"
        Image.new("RGB", (20, 20), (255, 255, 255)).save(rgb, format="PNG")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["tiles"][0]["source_file"] = _binding(rgb, root)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "NOT_RGBA"):
            build_explicit_overlay_materialization(manifest_path, root / "runs" / "blocked", repo_root=root)

    def test_rejects_verified_asset_ownership(self) -> None:
        temp, root, manifest_path = self._fixture()
        self.addCleanup(temp.cleanup)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["layer_source"] = "verified_asset"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "LAYER_OWNERSHIP_INVALID"):
            build_explicit_overlay_materialization(manifest_path, root / "runs" / "blocked", repo_root=root)

    def test_byte_drift_is_rejected_on_replay(self) -> None:
        temp, root, manifest_path = self._fixture()
        self.addCleanup(temp.cleanup)
        run = build_explicit_overlay_materialization(manifest_path, root / "runs" / "cs332", repo_root=root)
        title = root / "assets" / "title_tile.png"
        title.write_bytes(title.read_bytes() + b"drift")
        with self.assertRaisesRegex(ValueError, "BYTE_DRIFT"):
            verify_explicit_overlay_materialization(run.receipt_path, repo_root=root)

    def test_source_has_no_resize_network_generation_or_authority_shortcuts(self) -> None:
        source = (Path(__file__).parents[1] / "engine" / "intelligence" / "qwen_image_explicit_overlay_materializer.py").read_text(encoding="utf-8")
        self.assertNotIn(".resize(", source)
        self.assertNotIn("requests.", source)
        self.assertNotIn("urllib", source)
        self.assertNotIn("QwenImagePipeline", source)
        self.assertNotIn('"semantic_approved": True', source)
        self.assertNotIn('"publication_ready": True', source)
        self.assertNotIn('"genuine_golden_png_created": True', source)


if __name__ == "__main__":
    unittest.main()
