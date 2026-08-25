import tempfile
import unittest
from pathlib import Path

from engine.intelligence.original_result_scene_renderer_v4 import OriginalResultSceneRendererV4
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.result_statement_composition import ResultStatementComposer
from engine.intelligence.result_visual_variation import ResultVisualFamily


FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


class OriginalResultSceneRendererV4Tests(unittest.TestCase):
    def setUp(self):
        self.profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
        self.composition = ResultStatementComposer().plan(self.profile)

    def _render(self, path: str, **kwargs):
        data = dict(
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
            seed=18001,
            story_key="north-city-south-united-2026-08-25",
        )
        data.update(kwargs)
        return OriginalResultSceneRendererV4().render(self.composition, **data)

    def test_v4_remains_original_and_never_fabricates_crests(self):
        with tempfile.TemporaryDirectory() as td:
            receipt = self._render(str(Path(td) / "scene.png"))
            self.assertFalse(receipt.source_photo_used)
            self.assertFalse(receipt.generator_used)
            self.assertFalse(receipt.network_used)
            self.assertFalse(receipt.fabricated_crest_used)
            self.assertFalse(receipt.publication_ready)
            self.assertEqual((receipt.width, receipt.height), (1080, 1350))

    def test_same_story_is_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            a = self._render(str(Path(td) / "a.png"))
            b = self._render(str(Path(td) / "b.png"))
            self.assertEqual(a.output_sha256, b.output_sha256)
            self.assertEqual(a.visual_family, b.visual_family)

    def test_recent_families_change_next_composition(self):
        with tempfile.TemporaryDirectory() as td:
            first = self._render(str(Path(td) / "a.png"))
            recent = (ResultVisualFamily(first.visual_family),)
            second = self._render(
                str(Path(td) / "b.png"),
                story_key="north-city-next-match",
                recent_visual_families=recent,
            )
            self.assertNotEqual(first.visual_family, second.visual_family)
            self.assertTrue(second.anti_repetition_applied)

    def test_score_is_smaller_than_v3_default_scale(self):
        with tempfile.TemporaryDirectory() as td:
            receipt = self._render(str(Path(td) / "scene.png"))
            self.assertLess(receipt.score_scale, 0.83)


if __name__ == "__main__":
    unittest.main()
