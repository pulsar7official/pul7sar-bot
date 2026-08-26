import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.local_generation_handoff import LocalGenerationHandoff
from tools.phase18_build_golden_batch import build_batch


class GoldenVisualBatchTests(unittest.TestCase):
    def test_batch_builds_unique_integrity_locked_story_first_handoffs(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest = build_batch(temp, (7007001, 7007002, 7007003))
            self.assertEqual(manifest["cost_mode"], "$0-local")
            self.assertEqual(manifest["composition_grammar"], "single_continuous_scene")
            self.assertEqual(manifest["visual_grammar_contract"], "pul7sar-visual-grammar-v1")
            self.assertEqual(manifest["visual_grammar_surface_visibility"], "context_only")
            self.assertEqual(manifest["sport_geometry"], "context_only_no_exact_surface_required")
            self.assertFalse(manifest["generated_sport_geometry_allowed"])
            self.assertFalse(manifest["hybrid_surface_replacement_required"])
            self.assertEqual(manifest["football_camera_preset"], "editorial_environmental_oblique")
            self.assertEqual(manifest["visual_priority"], "story_focal_hierarchy_before_sport_surface")
            self.assertFalse(manifest["generated_branding_allowed"])
            self.assertEqual(manifest["brand_composition_policy"], "dynamic_deterministic_after_generation")
            self.assertEqual(len(manifest["candidates"]), 3)
            hashes = {item["payload_sha256"] for item in manifest["candidates"]}
            self.assertEqual(len(hashes), 3)
            for item in manifest["candidates"]:
                request = LocalGenerationHandoff.read(str(Path(temp) / item["handoff"]))
                self.assertEqual(request.seed, item["seed"])
                self.assertEqual(request.metadata["cost_mode"], "$0-local")
                prompt = request.prompt.casefold()
                self.assertIn("one single continuous full-bleed editorial image", prompt)
                self.assertIn("asymmetric editorial hierarchy", prompt)
                self.assertIn("no high-wide-central broadcast framing", prompt)
                self.assertIn("no full-pitch master shot", prompt)
                self.assertIn("the visual hero is anticipation, light, depth and place", prompt)
                self.assertNotIn("reserved surface region plain and unmarked", prompt)
                self.assertNotIn("exact surface will be replaced by deterministic code", prompt)
                self.assertTrue(request.metadata["hybrid_base_scene_contract"])
                self.assertEqual(request.metadata["visual_grammar_contract"], "pul7sar-visual-grammar-v1")
                self.assertTrue(request.metadata["visual_grammar_provider_agnostic"])
                self.assertEqual(request.metadata["visual_grammar_surface_visibility"], "context_only")
                self.assertFalse(request.metadata["generated_sport_geometry_allowed"])
                self.assertFalse(request.metadata["hybrid_surface_replacement_required"])
                self.assertEqual(request.metadata["football_camera_preset"], "editorial_environmental_oblique")
                self.assertEqual(request.metadata["visual_priority"], "story_focal_hierarchy_before_sport_surface")
                self.assertTrue(request.metadata["brand_name_redacted_from_generation_prompt"])
                self.assertEqual(item["visual_grammar_surface_visibility"], "context_only")
                self.assertNotIn("pul7sar", prompt)
                self.assertNotIn("pulsar", prompt)

    def test_manifest_is_written_and_matches_returned_structure(self):
        with tempfile.TemporaryDirectory() as temp:
            expected = build_batch(temp, (11, 12))
            saved = json.loads((Path(temp) / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(saved, expected)
            self.assertEqual(saved["manifest_version"], "pul7sar-golden-batch-v6")
            self.assertEqual(saved["composition_grammar"], "single_continuous_scene")
            self.assertEqual(saved["visual_grammar_contract"], "pul7sar-visual-grammar-v1")
            self.assertEqual(saved["visual_grammar_surface_visibility"], "context_only")
            self.assertEqual(saved["sport_geometry"], "context_only_no_exact_surface_required")
            self.assertFalse(saved["generated_sport_geometry_allowed"])
            self.assertFalse(saved["hybrid_surface_replacement_required"])
            self.assertEqual(saved["football_camera_preset"], "editorial_environmental_oblique")
            self.assertEqual(saved["visual_priority"], "story_focal_hierarchy_before_sport_surface")
            self.assertFalse(saved["generated_branding_allowed"])
            self.assertEqual(saved["brand_composition_policy"], "dynamic_deterministic_after_generation")

    def test_duplicate_seeds_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "unique"):
                build_batch(temp, (7, 7))


if __name__ == "__main__":
    unittest.main()
