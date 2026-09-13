import tempfile
import unittest
from pathlib import Path

from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.result_statement_composition import ResultStatementComposer
from engine.intelligence.result_statement_study_renderer import ResultStatementStudyRenderer


class ResultStatementStudyRendererTests(unittest.TestCase):
    def setUp(self):
        self.profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
        self.composition = ResultStatementComposer().plan(self.profile)
        self.font = next(
            (p for p in (
                Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
                Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
            ) if p.is_file()),
            None,
        )
        if self.font is None:
            self.skipTest('DejaVu CI font unavailable')

    def _render(self, output: Path):
        return ResultStatementStudyRenderer().render(
            self.composition,
            profile=self.profile,
            output_path=str(output),
            home_name='HOME CLUB',
            away_name='AWAY CLUB',
            home_score=3,
            away_score=1,
            headline='FULL TIME',
            home_accent_hex='#034694',
            away_accent_hex='#B21F2D',
            brand_accent_hex='#034694',
            font_path=str(self.font),
            winner='home',
        )

    def test_result_renderer_is_independent_and_preserves_neutrality_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self._render(Path(tmp) / 'result.png')
            self.assertEqual(receipt.contract, 'pul7sar-result-statement-study-renderer-v2-score-monument')
            self.assertEqual(receipt.visual_grammar, 'score_monument')
            self.assertTrue(receipt.club_identity_scale_equal)
            self.assertEqual(receipt.loser_treatment, 'neutral_respectful_no_degradation')
            self.assertTrue(receipt.home_identity_placeholder_used)
            self.assertTrue(receipt.away_identity_placeholder_used)
            self.assertFalse(receipt.identity_initial_letters_used)
            self.assertFalse(receipt.giant_color_panels_used)
            self.assertFalse(receipt.full_pitch_used)
            self.assertFalse(receipt.generator_used)
            self.assertFalse(receipt.network_used)
            self.assertTrue(receipt.study_only)
            self.assertFalse(receipt.publication_ready)
            self.assertEqual(receipt.brand_overlay_contract, 'pul7sar-adaptive-brand-overlay-v1')
            self.assertLess(receipt.brand_width, 870)

    def test_same_inputs_produce_identical_png_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            one = Path(tmp) / 'one.png'
            two = Path(tmp) / 'two.png'
            first = self._render(one)
            second = self._render(two)
            self.assertEqual(first.output_sha256, second.output_sha256)
            self.assertEqual(one.read_bytes(), two.read_bytes())

    def test_result_identity_boxes_are_equal_and_below_score_monument(self):
        home = self.composition.home_identity_box
        away = self.composition.away_identity_box
        score = self.composition.score_box
        self.assertEqual(home.width, away.width)
        self.assertEqual(home.height, away.height)
        self.assertNotEqual(home.x, away.x)
        self.assertGreaterEqual(home.y, score.y + score.height)
        self.assertGreaterEqual(away.y, score.y + score.height)
        self.assertTrue(self.composition.score_is_primary)
        self.assertFalse(self.composition.generated_score_allowed)
        self.assertFalse(self.composition.generated_crest_allowed)

    def test_invalid_winner_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'winner must be home, away or None'):
                ResultStatementStudyRenderer().render(
                    self.composition,
                    profile=self.profile,
                    output_path=str(Path(tmp) / 'result.png'),
                    home_name='HOME CLUB',
                    away_name='AWAY CLUB',
                    home_score=3,
                    away_score=1,
                    headline='FULL TIME',
                    home_accent_hex='#034694',
                    away_accent_hex='#B21F2D',
                    brand_accent_hex='#034694',
                    font_path=str(self.font),
                    winner='invalid',
                )


if __name__ == '__main__':
    unittest.main()
