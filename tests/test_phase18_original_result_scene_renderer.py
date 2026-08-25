import tempfile
import unittest
from pathlib import Path

from engine.intelligence.original_result_scene_renderer import OriginalResultSceneRenderer
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.result_statement_composition import ResultStatementComposer


FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


class OriginalResultSceneRendererTests(unittest.TestCase):
    def setUp(self):
        self.profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
        self.composition = ResultStatementComposer().plan(self.profile)

    def _render(self, path: str, seed: int = 18001):
        return OriginalResultSceneRenderer().render(
            self.composition,
            profile=self.profile,
            output_path=path,
            home_name="NORTH CITY",
            away_name="SOUTH UNITED",
            home_score=3,
            away_score=1,
            headline="A NIGHT TO REMEMBER",
            home_accent_hex="#E30613",
            away_accent_hex="#1D5EFF",
            brand_accent_hex="#E30613",
            font_path=FONT,
            winner="home",
            seed=seed,
        )

    def test_scene_is_original_and_uses_no_external_pixels_or_generator(self):
        with tempfile.TemporaryDirectory() as td:
            receipt = self._render(str(Path(td) / "scene.png"))
            self.assertEqual(receipt.scene_origin, "100_percent_code_generated_original_pixels")
            self.assertFalse(receipt.source_photo_used)
            self.assertFalse(receipt.generator_used)
            self.assertFalse(receipt.network_used)
            self.assertFalse(receipt.fabricated_crest_used)
            self.assertFalse(receipt.publication_ready)
            self.assertTrue(receipt.study_only)

    def test_same_seed_and_inputs_are_byte_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            first = self._render(str(Path(td) / "a.png"))
            second = self._render(str(Path(td) / "b.png"))
            self.assertEqual(first.output_sha256, second.output_sha256)
            self.assertEqual(Path(first.output_path).read_bytes(), Path(second.output_path).read_bytes())

    def test_different_seed_changes_atmospheric_pixels_but_not_exact_score(self):
        with tempfile.TemporaryDirectory() as td:
            first = self._render(str(Path(td) / "a.png"), seed=18001)
            second = self._render(str(Path(td) / "b.png"), seed=18002)
            self.assertNotEqual(first.output_sha256, second.output_sha256)
            self.assertEqual(first.score_text, "3–1")
            self.assertEqual(second.score_text, "3–1")

    def test_adaptive_brand_is_real_overlay_not_generated_motif(self):
        with tempfile.TemporaryDirectory() as td:
            receipt = self._render(str(Path(td) / "scene.png"))
            self.assertIn("adaptive", receipt.brand_overlay_contract)
            self.assertLess(receipt.width, 2000)
            self.assertEqual((receipt.width, receipt.height), (1080, 1350))


if __name__ == "__main__":
    unittest.main()
