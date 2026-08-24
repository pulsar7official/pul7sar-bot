import tempfile
import unittest
from pathlib import Path

from tools.phase18_build_result_composition_matrix import build


class ResultCompositionMatrixTests(unittest.TestCase):
    def test_builds_all_platforms_without_images_or_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "manifest.json"
            manifest = build(str(output))
            self.assertTrue(output.is_file())
            self.assertEqual(manifest["manifest_version"], "pul7sar-result-composition-matrix-v1")
            self.assertEqual(manifest["benchmark_id"], "result-statement-v1")
            self.assertEqual(manifest["family"], "result_statement")
            self.assertEqual(manifest["platform_count"], 7)
            self.assertTrue(manifest["zero_cost"])
            self.assertFalse(manifest["network_used"])
            self.assertFalse(manifest["image_generator_used"])
            self.assertFalse(manifest["image_created"])
            self.assertFalse(manifest["inherits_transfer_layout"])
            self.assertFalse(manifest["publication_ready"])

    def test_every_result_surface_is_neutral_and_exact_layer_owned(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = build(str(Path(tmp) / "manifest.json"))
            for entry in manifest["platforms"]:
                self.assertTrue(entry["score_is_primary"])
                self.assertTrue(entry["club_identity_scale_equal"])
                self.assertEqual(entry["winner_emphasis_mode"], "accent_and_hierarchy_only")
                self.assertEqual(entry["loser_treatment"], "neutral_respectful_no_degradation")
                self.assertFalse(entry["generated_score_allowed"])
                self.assertFalse(entry["generated_crest_allowed"])
                self.assertFalse(entry["publication_ready"])
                self.assertEqual(entry["brand"]["contract"], "pul7sar-adaptive-brand-placement-v1")
                self.assertLessEqual(entry["brand"]["max_width_ratio"], 0.25)

    def test_portrait_and_landscape_geometry_are_not_one_template(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = build(str(Path(tmp) / "manifest.json"))
            by_platform = {entry["platform"]: entry for entry in manifest["platforms"]}
            instagram = by_platform["instagram_feed"]
            x_feed = by_platform["x_feed"]
            self.assertNotEqual(instagram["score_box"], x_feed["score_box"])
            self.assertNotEqual(instagram["headline_box"], x_feed["headline_box"])


if __name__ == "__main__":
    unittest.main()
