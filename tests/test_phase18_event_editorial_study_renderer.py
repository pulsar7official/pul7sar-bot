import tempfile
import unittest
from pathlib import Path

from engine.intelligence.event_editorial_composition import EventEditorialComposer
from engine.intelligence.event_editorial_study_renderer import EventAnchorKind, EventEditorialStudyRenderer
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform


class EventEditorialStudyRendererTests(unittest.TestCase):
    def setUp(self):
        self.profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
        self.composition = EventEditorialComposer().plan(self.profile)
        self.font = next((p for p in (
            Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
            Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
        ) if p.is_file()), None)
        if self.font is None:
            self.skipTest('DejaVu font unavailable')

    def _render(self, output: Path):
        return EventEditorialStudyRenderer().render(
            self.composition,
            profile=self.profile,
            output_path=str(output),
            headline='NEW ERA',
            kicker='OFFICIAL ANNOUNCEMENT',
            anchor_kind=EventAnchorKind.ANNOUNCEMENT,
            accent_hex='#C71925',
            font_path=str(self.font),
            seed_key='event-editorial-regression',
        )

    def test_renderer_uses_one_abstract_anchor_without_forced_motifs(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self._render(Path(tmp) / 'event.png')
            self.assertEqual(receipt.contract, 'pul7sar-event-editorial-study-renderer-v1-premium-anchor')
            self.assertTrue(receipt.single_anchor_used)
            self.assertFalse(receipt.person_used)
            self.assertFalse(receipt.full_pitch_used)
            self.assertFalse(receipt.decorative_stats_used)
            self.assertFalse(receipt.generator_used)
            self.assertFalse(receipt.network_used)
            self.assertTrue(receipt.study_only)
            self.assertFalse(receipt.publication_ready)
            self.assertLess(receipt.brand_width, 870)

    def test_same_input_is_byte_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / 'a.png'
            b = Path(tmp) / 'b.png'
            first = self._render(a)
            second = self._render(b)
            self.assertEqual(first.output_sha256, second.output_sha256)
            self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_anchor_kind_must_be_explicit_enum(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(TypeError, 'anchor_kind must be EventAnchorKind'):
                EventEditorialStudyRenderer().render(
                    self.composition,
                    profile=self.profile,
                    output_path=str(Path(tmp) / 'event.png'),
                    headline='NEW ERA',
                    kicker='OFFICIAL ANNOUNCEMENT',
                    anchor_kind='announcement',
                    accent_hex='#C71925',
                    font_path=str(self.font),
                )


if __name__ == '__main__':
    unittest.main()
