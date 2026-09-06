import tempfile
import unittest
from pathlib import Path

from tools.phase18_build_story_family_composition_matrix import build


class StoryFamilyCompositionMatrixTests(unittest.TestCase):
    def test_builds_six_families_across_seven_platforms_without_images(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = build(str(Path(tmp) / "manifest.json"))
            self.assertEqual(manifest["manifest_version"], "pul7sar-story-family-composition-matrix-v1")
            self.assertEqual(manifest["family_count"], 6)
            self.assertEqual(manifest["platform_count"], 7)
            self.assertEqual(manifest["decision_count"], 42)
            self.assertEqual(manifest["expected_decision_count"], 42)
            self.assertTrue(manifest["all_families_have_distinct_contracts"])
            self.assertFalse(manifest["inherits_transfer_layout_anywhere"])
            self.assertTrue(manifest["zero_cost"])
            self.assertFalse(manifest["network_used"])
            self.assertFalse(manifest["image_generator_used"])
            self.assertFalse(manifest["image_created"])
            self.assertFalse(manifest["publication_ready"])

    def test_family_contracts_are_unique_and_brand_is_adaptive(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = build(str(Path(tmp) / "manifest.json"))
            contracts = manifest["family_contracts"]
            self.assertEqual(len(contracts), 6)
            self.assertEqual(len(set(contracts.values())), 6)
            for entry in manifest["entries"]:
                self.assertEqual(entry["brand_contract"], "pul7sar-adaptive-brand-placement-v1")
                self.assertFalse(entry["inherits_transfer_layout"])
                self.assertLessEqual(entry["brand_max_width_ratio"], 0.30)
                self.assertLessEqual(entry["brand_max_height_ratio"], 0.105)


if __name__ == "__main__":
    unittest.main()
