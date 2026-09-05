from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from engine.intelligence.qwen_image_explicit_verified_brand_overlay_materializer import (
    CONTRACT as BRAND_CONTRACT,
    OUTPUT_RENDERER_CONTRACT,
)
from engine.intelligence.qwen_image_materialized_overlay_composition_manifest_bundle import (
    build_materialized_overlay_composition_manifest_bundle,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _binding(path: Path, root: Path) -> dict:
    return {
        "repository_relative_path": path.relative_to(root).as_posix(),
        "sha256": _sha(path),
        "byte_size": path.stat().st_size,
    }


class MaterializedOverlayCompositionManifestBundleTests(unittest.TestCase):
    def _fixture(self, root: Path, *, add_identity: bool = False) -> tuple[dict, dict, Path, Path]:
        candidate = root / "candidate.png"
        typography = root / "typography.png"
        brand_tile = root / "brand_tile.png"
        brand_overlay = root / "brand_overlay.png"
        candidate.write_bytes(b"candidate-bytes")
        typography.write_bytes(b"typography-overlay-bytes")
        brand_tile.write_bytes(b"brand-tile-bytes")
        brand_overlay.write_bytes(b"brand-full-canvas-overlay-bytes")

        candidate_binding = _binding(candidate, root)
        plan = [
            {"name": "atmosphere_base", "source": "generative", "purpose": "base", "required": True},
            {"name": "editorial_typography", "source": "deterministic", "purpose": "copy", "required": True},
            {"name": "pul7sar_brand", "source": "verified_asset", "purpose": "brand", "required": True},
        ]
        if add_identity:
            plan.append({"name": "human_identity", "source": "verified_asset", "purpose": "identity", "required": True})
        cs268 = {
            "generated_layer_qa_approved": True,
            "story_snapshot_sha256": "a" * 64,
            "candidate_png": candidate_binding,
            "hybrid_layer_plan": plan,
        }
        typography_receipt = {
            "story_snapshot_sha256": "a" * 64,
            "candidate_png": candidate_binding,
            "layer_name": "editorial_typography",
            "layer_source": "deterministic",
            "renderer_contract": OUTPUT_RENDERER_CONTRACT,
            "overlay_materialized": True,
            "overlay_file": _binding(typography, root),
        }
        manifest = {
            "contract": BRAND_CONTRACT,
            "story_sha256": "a" * 64,
            "layer_name": "pul7sar_brand",
            "layer_source": "verified_asset",
            "owner_brand_approval_required": True,
            "candidate": {
                "path": "candidate.png",
                "sha256": _sha(candidate),
                "size_bytes": candidate.stat().st_size,
                "width": 1080,
                "height": 1350,
            },
            "brand_tile": {
                "path": "brand_tile.png",
                "sha256": _sha(brand_tile),
                "size_bytes": brand_tile.stat().st_size,
            },
            "placement": {"x": 900, "y": 1200},
        }
        manifest_path = root / "brand_manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        receipt = {
            "contract": BRAND_CONTRACT,
            "story_sha256": "a" * 64,
            "layer_name": "pul7sar_brand",
            "layer_source": "verified_asset",
            "candidate_sha256": _sha(candidate),
            "candidate_size_bytes": candidate.stat().st_size,
            "brand_tile_sha256": _sha(brand_tile),
            "brand_tile_size_bytes": brand_tile.stat().st_size,
            "placement_x": 900,
            "placement_y": 1200,
            "canvas_width": 1080,
            "canvas_height": 1350,
            "output_path": "brand_overlay.png",
            "output_sha256": _sha(brand_overlay),
            "output_size_bytes": brand_overlay.stat().st_size,
            "output_mode": "RGBA",
            "renderer_contract": OUTPUT_RENDERER_CONTRACT,
            "overlay_materialized": True,
            "brand_publication_approved": False,
            "owner_brand_approval_required": True,
            "composition_executed": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
            "authoritative": False,
        }
        receipt_path = root / "brand_receipt.json"
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        return cs268, typography_receipt, manifest_path, receipt_path

    def test_builds_exact_cs269_and_cs270_manifests_without_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cs268, typography_receipt, manifest_path, receipt_path = self._fixture(root)
            output_dir = root / "bundle"
            with patch(
                "engine.intelligence.qwen_image_materialized_overlay_composition_manifest_bundle.verify_canonical_candidate_generated_layer_qa",
                return_value=cs268,
            ), patch(
                "engine.intelligence.qwen_image_materialized_overlay_composition_manifest_bundle.verify_explicit_overlay_materialization",
                return_value=typography_receipt,
            ):
                bundle_path = build_materialized_overlay_composition_manifest_bundle(
                    root / "cs268.json", root / "typography_receipt.json",
                    manifest_path, receipt_path, output_dir, repo_root=root,
                )
            bundle = json.loads(bundle_path.read_text())
            composition = json.loads((output_dir / "composition_input_manifest.json").read_text())
            payload = json.loads((output_dir / "deterministic_payload_manifest.json").read_text())
            self.assertTrue(bundle["composition_input_binding_ready"])
            self.assertFalse(bundle["composition_executed"])
            self.assertFalse(bundle["semantic_approved"])
            self.assertFalse(bundle["genuine_golden_png_created"])
            self.assertFalse(bundle["publication_ready"])
            self.assertEqual(composition["layers"][0]["name"], "editorial_typography")
            self.assertEqual(composition["layers"][1]["name"], "pul7sar_brand")
            self.assertEqual(payload["deterministic_payloads"][0]["payload_file"]["sha256"], composition["layers"][0]["payload_sha256"])

    def test_rejects_required_identity_layer_in_first_golden_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cs268, typography_receipt, manifest_path, receipt_path = self._fixture(root, add_identity=True)
            with patch(
                "engine.intelligence.qwen_image_materialized_overlay_composition_manifest_bundle.verify_canonical_candidate_generated_layer_qa",
                return_value=cs268,
            ), patch(
                "engine.intelligence.qwen_image_materialized_overlay_composition_manifest_bundle.verify_explicit_overlay_materialization",
                return_value=typography_receipt,
            ):
                with self.assertRaisesRegex(ValueError, "UNSUPPORTED_REQUIRED_LAYER:human_identity"):
                    build_materialized_overlay_composition_manifest_bundle(
                        root / "cs268.json", root / "typography_receipt.json",
                        manifest_path, receipt_path, root / "bundle", repo_root=root,
                    )

    def test_rejects_brand_receipt_placement_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cs268, typography_receipt, manifest_path, receipt_path = self._fixture(root)
            receipt = json.loads(receipt_path.read_text())
            receipt["placement_x"] = 899
            receipt_path.write_text(json.dumps(receipt))
            with patch(
                "engine.intelligence.qwen_image_materialized_overlay_composition_manifest_bundle.verify_canonical_candidate_generated_layer_qa",
                return_value=cs268,
            ), patch(
                "engine.intelligence.qwen_image_materialized_overlay_composition_manifest_bundle.verify_explicit_overlay_materialization",
                return_value=typography_receipt,
            ):
                with self.assertRaisesRegex(ValueError, "BRAND_RECEIPT_DRIFT"):
                    build_materialized_overlay_composition_manifest_bundle(
                        root / "cs268.json", root / "typography_receipt.json",
                        manifest_path, receipt_path, root / "bundle", repo_root=root,
                    )

    def test_source_contains_no_generation_rendering_or_authority_shortcut(self) -> None:
        source = Path("engine/intelligence/qwen_image_materialized_overlay_composition_manifest_bundle.py").read_text()
        for token in (
            "QwenImagePipeline", "Image.new(", "alpha_composite(", "requests.",
            "semantic_approved\": True", "genuine_golden_png_created\": True",
            "publication_ready\": True", "brand_publication_approved\": True",
        ):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
