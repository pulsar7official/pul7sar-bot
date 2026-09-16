from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

from engine.intelligence import qwen_image_production_overlay_execution_readiness as readiness


def _binding(root: Path, path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    return {
        "repository_relative_path": path.relative_to(root).as_posix(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
    }


def _write_overlay(path: Path, size=(12, 16), mode="RGBA", opaque=False) -> None:
    if mode == "RGBA":
        image = Image.new("RGBA", size, (0, 0, 0, 255 if opaque else 0))
        if not opaque:
            image.putpixel((1, 1), (255, 255, 255, 255))
    else:
        image = Image.new(mode, size, 0)
    image.save(path, format="PNG")


class ProductionOverlayExecutionReadinessTests(unittest.TestCase):
    def test_overlay_png_requires_native_rgba_exact_canvas_and_partial_transparency(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            valid = root / "valid.png"
            _write_overlay(valid)
            descriptor, blocker = readiness._inspect_overlay_png(valid, (12, 16))
            self.assertIsNone(blocker)
            self.assertEqual(descriptor["mode"], "RGBA")
            self.assertEqual(descriptor["alpha_min"], 0)
            self.assertEqual(descriptor["alpha_max"], 255)

            rgb = root / "rgb.png"
            _write_overlay(rgb, mode="RGB")
            self.assertEqual(readiness._inspect_overlay_png(rgb, (12, 16))[1], "not_rgba")

            opaque = root / "opaque.png"
            _write_overlay(opaque, opaque=True)
            self.assertEqual(
                readiness._inspect_overlay_png(opaque, (12, 16))[1],
                "fully_opaque_full_canvas",
            )
            self.assertEqual(
                readiness._inspect_overlay_png(valid, (16, 12))[1],
                "canvas_dimension_drift",
            )

    def test_build_ready_replays_lineage_without_composition_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = root / "candidate.png"
            Image.new("RGB", (12, 16), (10, 20, 30)).save(candidate, format="PNG")
            typography = root / "typography.png"
            brand = root / "brand.png"
            _write_overlay(typography)
            _write_overlay(brand)
            cs269_file = root / "cs269.json"
            cs269_file.write_text("{}", encoding="utf-8")
            cs270_file = root / "cs270.json"
            cs270_file.write_text("{}", encoding="utf-8")
            story_sha = "1" * 64
            candidate_binding = _binding(root, candidate)
            cs269 = {
                "schema": readiness.CS269_SCHEMA,
                "receipt_sha256": "2" * 64,
                "story_snapshot_sha256": story_sha,
                "candidate_png": candidate_binding,
                "composition_request_ready": True,
                "composition_layers": [
                    {"name": "atmosphere_base", "source": "generative"},
                    {"name": "editorial_typography", "source": "deterministic"},
                    {"name": "pul7sar_brand", "source": "verified_asset", "asset_file": _binding(root, brand)},
                ],
                **{field: False for field in readiness._DOWNSTREAM_FALSE},
            }
            cs270 = {
                "schema": readiness.CS270_SCHEMA,
                "receipt_sha256": "3" * 64,
                "story_snapshot_sha256": story_sha,
                "candidate_png": candidate_binding,
                "source_cs269_receipt": {**_binding(root, cs269_file), "receipt_sha256": cs269["receipt_sha256"]},
                "deterministic_payloads": [{
                    "name": "editorial_typography",
                    "renderer_contract": readiness.FULL_CANVAS_OVERLAY_CONTRACT,
                    "payload_sha256": _binding(root, typography)["sha256"],
                    "payload_file": _binding(root, typography),
                }],
                "composition_execution_ready": True,
                **{field: False for field in readiness._DOWNSTREAM_FALSE},
            }
            output_dir = root / "out"
            with patch.object(readiness, "verify_composition_execution_preflight", return_value=cs270), patch.object(
                readiness, "verify_deterministic_composition_request", return_value=cs269
            ):
                run = readiness.build_production_overlay_execution_readiness(cs270_file, output_dir, repo_root=root)
                receipt = readiness.verify_production_overlay_execution_readiness(run.receipt_path, repo_root=root)
            self.assertTrue(run.overlay_execution_ready)
            self.assertTrue(receipt["overlay_execution_ready"])
            self.assertEqual({item["name"] for item in receipt["checked_overlays"]}, {"editorial_typography", "pul7sar_brand"})
            for field in readiness._DOWNSTREAM_FALSE:
                self.assertIs(receipt[field], False)

    def test_unsupported_renderer_contract_blocks_before_one_shot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            overlay = root / "overlay.png"
            _write_overlay(overlay)
            cs269 = {
                "composition_layers": [{"name": "editorial_typography", "source": "deterministic"}],
            }
            cs270 = {
                "deterministic_payloads": [{
                    "name": "editorial_typography",
                    "renderer_contract": "some-other-renderer-v1",
                    "payload_file": _binding(root, overlay),
                }],
            }
            checked, blockers = readiness._assess_layers(
                cs270, cs269, repo_root=root, expected_size=(12, 16)
            )
            self.assertEqual(checked, [])
            self.assertEqual(blockers, ["unsupported_renderer_contract:editorial_typography"])

    def test_verified_asset_canvas_drift_is_blocker_not_resized(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brand = root / "brand.png"
            _write_overlay(brand, size=(6, 8))
            cs269 = {
                "composition_layers": [{
                    "name": "pul7sar_brand",
                    "source": "verified_asset",
                    "asset_file": _binding(root, brand),
                }],
            }
            checked, blockers = readiness._assess_layers(
                {"deterministic_payloads": []}, cs269, repo_root=root, expected_size=(12, 16)
            )
            self.assertEqual(checked, [])
            self.assertEqual(blockers, ["overlay_not_execution_ready:pul7sar_brand:canvas_dimension_drift"])

    def test_source_contains_no_generation_network_or_authority_shortcut(self) -> None:
        source = Path(readiness.__file__).read_text(encoding="utf-8")
        self.assertNotIn("QwenImagePipeline", source)
        self.assertNotIn("requests.", source)
        self.assertNotIn("urllib", source)
        self.assertNotIn("Image.resize", source)
        self.assertNotIn("semantic_approved\": True", source)
        self.assertNotIn("publication_ready\": True", source)
        self.assertNotIn("genuine_golden_png_created\": True", source)


if __name__ == "__main__":
    unittest.main()
