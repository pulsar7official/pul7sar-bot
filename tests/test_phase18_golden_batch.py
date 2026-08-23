import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.local_generation_handoff import LocalGenerationHandoff
from tools.phase18_build_golden_batch import build_batch


class GoldenVisualBatchTests(unittest.TestCase):
    def test_batch_builds_unique_integrity_locked_handoffs(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest = build_batch(temp, (7007001, 7007002, 7007003))
            self.assertEqual(manifest["cost_mode"], "$0-local")
            self.assertEqual(manifest["composition_grammar"], "single_continuous_scene")
            self.assertEqual(manifest["sport_geometry"], "deterministic_football_pitch_projective_v1")
            self.assertFalse(manifest["generated_sport_geometry_allowed"])
            self.assertTrue(manifest["hybrid_surface_replacement_required"])
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
                self.assertIn("unmarked neutral sport-surface region reserved for deterministic overlay", prompt)
                self.assertIn("exact surface will be replaced by deterministic code", prompt)

    def test_manifest_is_written_and_matches_returned_structure(self):
        with tempfile.TemporaryDirectory() as temp:
            expected = build_batch(temp, (11, 12))
            saved = json.loads((Path(temp) / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(saved, expected)
            self.assertEqual(saved["manifest_version"], "pul7sar-golden-batch-v5")
            self.assertEqual(saved["composition_grammar"], "single_continuous_scene")
            self.assertEqual(saved["sport_geometry"], "deterministic_football_pitch_projective_v1")
            self.assertFalse(saved["generated_sport_geometry_allowed"])
            self.assertTrue(saved["hybrid_surface_replacement_required"])
            self.assertFalse(saved["generated_branding_allowed"])
            self.assertEqual(saved["brand_composition_policy"], "dynamic_deterministic_after_generation")

    def test_duplicate_seeds_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "unique"):
                build_batch(temp, (7, 7))


if __name__ == "__main__":
    unittest.main()
