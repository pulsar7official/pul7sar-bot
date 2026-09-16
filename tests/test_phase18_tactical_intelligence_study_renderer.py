import tempfile
import unittest
from pathlib import Path

from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.tactical_intelligence_composition import TacticalIntelligenceComposer
from engine.intelligence.tactical_intelligence_study_renderer import (
    TacticalArrow,
    TacticalIntelligenceStudyRenderer,
    TacticalPosition,
)


class TacticalIntelligenceStudyRendererTests(unittest.TestCase):
    def setUp(self):
        self.profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
        self.composition = TacticalIntelligenceComposer().plan(self.profile)
        self.font = next(
            (p for p in (
                Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
                Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
            ) if p.is_file()),
            None,
        )
        if self.font is None:
            self.skipTest('DejaVu CI font unavailable')
        self.positions = (
            TacticalPosition('GK', 0.08, 0.50),
            TacticalPosition('LB', 0.25, 0.15),
            TacticalPosition('CB', 0.23, 0.38),
            TacticalPosition('CB', 0.23, 0.62),
            TacticalPosition('RB', 0.25, 0.85),
            TacticalPosition('DM', 0.43, 0.50),
            TacticalPosition('CM', 0.55, 0.30),
            TacticalPosition('CM', 0.55, 0.70),
            TacticalPosition('LW', 0.78, 0.17),
            TacticalPosition('ST', 0.84, 0.50),
            TacticalPosition('RW', 0.78, 0.83),
        )
        self.arrows = (
            TacticalArrow(0.25, 0.15, 0.48, 0.10),
            TacticalArrow(0.25, 0.85, 0.48, 0.90),
            TacticalArrow(0.55, 0.30, 0.69, 0.39),
        )

    def _render(self, output: Path):
        return TacticalIntelligenceStudyRenderer().render(
            self.composition,
            profile=self.profile,
            output_path=str(output),
            headline='TACTICAL INTELLIGENCE',
            analysis_text='WIDTH + MIDFIELD CONTROL',
            formation_label='4-3-3 | POSSESSION SHAPE',
            positions=self.positions,
            arrows=self.arrows,
            accent_hex='#17A8FF',
            opponent_accent_hex='#D8E1E8',
            brand_accent_hex='#17A8FF',
            font_path=str(self.font),
        )

    def test_tactical_renderer_owns_exact_geometry_and_positions(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self._render(Path(tmp)/'tactics.png')
            self.assertEqual(receipt.contract, 'pul7sar-tactical-intelligence-study-renderer-v1')
            self.assertEqual(receipt.position_count, 11)
            self.assertEqual(receipt.arrow_count, 3)
            self.assertTrue(receipt.exact_pitch_geometry_used)
            self.assertFalse(receipt.generated_pitch_markings_used)
            self.assertFalse(receipt.generated_player_positions_used)
            self.assertFalse(receipt.decorative_stadium_used)
            self.assertFalse(receipt.generator_used)
            self.assertFalse(receipt.network_used)
            self.assertEqual(receipt.brand_overlay_contract, 'pul7sar-adaptive-brand-overlay-v1')
            self.assertTrue(receipt.study_only)
            self.assertFalse(receipt.publication_ready)

    def test_same_tactical_data_produce_identical_png(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = self._render(root/'one.png')
            second = self._render(root/'two.png')
            self.assertEqual(first.output_sha256, second.output_sha256)
            self.assertEqual((root/'one.png').read_bytes(), (root/'two.png').read_bytes())

    def test_invalid_position_coordinates_fail_closed(self):
        with self.assertRaises(ValueError):
            TacticalPosition('ST', 1.01, 0.50)
        with self.assertRaises(ValueError):
            TacticalArrow(0.1, 0.2, -0.1, 0.4)

    def test_tactical_brand_is_smallest_family_treatment(self):
        self.assertLessEqual(self.composition.brand.max_width_ratio, 0.21)
        self.assertLessEqual(self.composition.brand.max_height_ratio, 0.075)
        self.assertTrue(self.composition.exact_sport_geometry_required)
        self.assertTrue(self.composition.exact_formation_data_required)
        self.assertFalse(self.composition.generated_pitch_markings_allowed)
        self.assertFalse(self.composition.generated_player_positions_allowed)


if __name__ == '__main__':
    unittest.main()
