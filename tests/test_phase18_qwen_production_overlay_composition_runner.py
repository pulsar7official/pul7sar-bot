from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from PIL import Image

from engine.intelligence import qwen_image_production_overlay_composition_runner as runner


class QwenProductionOverlayCompositionRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path.cwd().resolve()

    @staticmethod
    def _binding(repo_root: Path, path: Path) -> dict[str, object]:
        raw = path.read_bytes()
        return {
            "repository_relative_path": path.resolve().relative_to(repo_root).as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "byte_size": len(raw),
        }

    def _png(self, path: Path, rgba: tuple[int, int, int, int], size=(8, 8)) -> None:
        Image.new("RGBA", size, rgba).save(path, format="PNG", optimize=False, compress_level=9)

    def test_exact_candidate_deterministic_and_verified_overlays_compose(self) -> None:
        with tempfile.TemporaryDirectory(dir=self.repo_root) as td:
            root = Path(td)
            candidate = root / "candidate.png"
            typography = root / "typography.png"
            brand = root / "brand.png"
            cs269_path = root / "cs269.json"
            cs269_path.write_text("{}\n", encoding="utf-8")
            self._png(candidate, (10, 20, 30, 255))
            self._png(typography, (200, 0, 0, 128))
            self._png(brand, (0, 255, 0, 64))

            candidate_binding = self._binding(self.repo_root, candidate)
            typography_binding = self._binding(self.repo_root, typography)
            brand_binding = self._binding(self.repo_root, brand)
            cs269_binding = self._binding(self.repo_root, cs269_path)
            story_sha = "a" * 64
            cs269 = {
                "schema": runner.CS269_SCHEMA,
                "composition_request_ready": True,
                "story_snapshot_sha256": story_sha,
                "candidate_png": candidate_binding,
                "composition_layers": [
                    {"name": "atmosphere_base", "source": "generative"},
                    {
                        "name": "editorial_typography",
                        "source": "deterministic",
                        "renderer_contract": runner.FULL_CANVAS_OVERLAY_CONTRACT,
                    },
                    {
                        "name": "pul7sar_brand",
                        "source": "verified_asset",
                        "asset_file": brand_binding,
                    },
                ],
            }
            preflight = {
                "composition_execution_ready": True,
                "story_snapshot_sha256": story_sha,
                "candidate_png": candidate_binding,
                "source_cs269_receipt": cs269_binding,
                "deterministic_payloads": [
                    {
                        "name": "editorial_typography",
                        "renderer_contract": runner.FULL_CANVAS_OVERLAY_CONTRACT,
                        "payload_file": typography_binding,
                    }
                ],
            }
            output = root / "composed.png"
            with mock.patch.object(runner, "verify_deterministic_composition_request", return_value=cs269):
                runner.compose_visual(preflight, output, self.repo_root)

            self.assertTrue(output.is_file())
            with Image.open(output) as image:
                self.assertEqual(image.format, "PNG")
                self.assertEqual(image.size, (8, 8))
                self.assertEqual(image.mode, "RGBA")

    def test_unsupported_deterministic_contract_fails_closed_without_output(self) -> None:
        with tempfile.TemporaryDirectory(dir=self.repo_root) as td:
            root = Path(td)
            candidate = root / "candidate.png"
            payload = root / "payload.png"
            cs269_path = root / "cs269.json"
            cs269_path.write_text("{}\n", encoding="utf-8")
            self._png(candidate, (0, 0, 0, 255))
            self._png(payload, (255, 255, 255, 255))
            candidate_binding = self._binding(self.repo_root, candidate)
            story_sha = "b" * 64
            cs269 = {
                "schema": runner.CS269_SCHEMA,
                "composition_request_ready": True,
                "story_snapshot_sha256": story_sha,
                "candidate_png": candidate_binding,
                "composition_layers": [
                    {"name": "atmosphere_base", "source": "generative"},
                    {"name": "editorial_typography", "source": "deterministic"},
                ],
            }
            preflight = {
                "composition_execution_ready": True,
                "story_snapshot_sha256": story_sha,
                "candidate_png": candidate_binding,
                "source_cs269_receipt": self._binding(self.repo_root, cs269_path),
                "deterministic_payloads": [
                    {
                        "name": "editorial_typography",
                        "renderer_contract": "unapproved-contract",
                        "payload_file": self._binding(self.repo_root, payload),
                    }
                ],
            }
            output = root / "composed.png"
            with mock.patch.object(runner, "verify_deterministic_composition_request", return_value=cs269):
                with self.assertRaisesRegex(ValueError, "UNSUPPORTED_RENDERER_CONTRACT"):
                    runner.compose_visual(preflight, output, self.repo_root)
            self.assertFalse(output.exists())

    def test_verified_asset_must_already_match_full_canvas(self) -> None:
        with tempfile.TemporaryDirectory(dir=self.repo_root) as td:
            root = Path(td)
            candidate = root / "candidate.png"
            brand = root / "brand.png"
            cs269_path = root / "cs269.json"
            cs269_path.write_text("{}\n", encoding="utf-8")
            self._png(candidate, (0, 0, 0, 255), (8, 8))
            self._png(brand, (255, 0, 0, 255), (4, 4))
            candidate_binding = self._binding(self.repo_root, candidate)
            story_sha = "c" * 64
            cs269 = {
                "schema": runner.CS269_SCHEMA,
                "composition_request_ready": True,
                "story_snapshot_sha256": story_sha,
                "candidate_png": candidate_binding,
                "composition_layers": [
                    {"name": "atmosphere_base", "source": "generative"},
                    {
                        "name": "pul7sar_brand",
                        "source": "verified_asset",
                        "asset_file": self._binding(self.repo_root, brand),
                    },
                ],
            }
            preflight = {
                "composition_execution_ready": True,
                "story_snapshot_sha256": story_sha,
                "candidate_png": candidate_binding,
                "source_cs269_receipt": self._binding(self.repo_root, cs269_path),
                "deterministic_payloads": [],
            }
            output = root / "composed.png"
            with mock.patch.object(runner, "verify_deterministic_composition_request", return_value=cs269):
                with self.assertRaisesRegex(ValueError, "CANVAS_DIMENSION_DRIFT"):
                    runner.compose_visual(preflight, output, self.repo_root)
            self.assertFalse(output.exists())

    def test_cs269_story_or_candidate_substitution_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(dir=self.repo_root) as td:
            root = Path(td)
            candidate = root / "candidate.png"
            cs269_path = root / "cs269.json"
            cs269_path.write_text("{}\n", encoding="utf-8")
            self._png(candidate, (0, 0, 0, 255))
            candidate_binding = self._binding(self.repo_root, candidate)
            preflight = {
                "composition_execution_ready": True,
                "story_snapshot_sha256": "d" * 64,
                "candidate_png": candidate_binding,
                "source_cs269_receipt": self._binding(self.repo_root, cs269_path),
                "deterministic_payloads": [],
            }
            cs269 = {
                "schema": runner.CS269_SCHEMA,
                "composition_request_ready": True,
                "story_snapshot_sha256": "e" * 64,
                "candidate_png": candidate_binding,
                "composition_layers": [],
            }
            with mock.patch.object(runner, "verify_deterministic_composition_request", return_value=cs269):
                with self.assertRaisesRegex(ValueError, "CS269_LINEAGE_DRIFT"):
                    runner.compose_visual(preflight, root / "out.png", self.repo_root)

    def test_runner_has_no_generation_network_or_publication_shortcut(self) -> None:
        source = Path("engine/intelligence/qwen_image_production_overlay_composition_runner.py").read_text(encoding="utf-8")
        self.assertNotIn("QwenImagePipeline", source)
        self.assertNotIn("requests.", source)
        self.assertNotIn("http://", source)
        self.assertNotIn("https://", source)
        self.assertNotIn("publication_ready", source)
        self.assertNotIn("semantic_approved", source)
        self.assertNotIn("human_visual_review_approved", source)


if __name__ == "__main__":
    unittest.main()
