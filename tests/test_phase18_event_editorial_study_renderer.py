import hashlib
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from engine.intelligence.event_editorial_composition import EventEditorialComposer
from engine.intelligence.event_editorial_study_renderer import EventAnchorKind, EventEditorialStudyRenderer
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.verified_context_surface import ContextRightsBasis, VerifiedContextAsset


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

    def _render(self, output: Path, *, context_asset=None):
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
            context_asset=context_asset,
        )

    @staticmethod
    def _fixture_asset(root: Path) -> VerifiedContextAsset:
        path = root / 'context.jpg'
        image = Image.new('RGB', (1600, 1000), (18, 28, 44))
        draw = ImageDraw.Draw(image)
        for y in range(0, 1000, 40):
            draw.rectangle((0, y, 1600, y + 20), fill=(20 + y // 60, 33 + y // 80, 54 + y // 70))
        draw.ellipse((120, 180, 900, 900), fill=(64, 82, 106))
        draw.rectangle((980, 100, 1590, 920), fill=(7, 13, 25))
        image.save(path, quality=94)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        return VerifiedContextAsset(
            asset_id='fixture-context',
            path=str(path),
            sha256=digest,
            source_reference='test://fixture-context',
            rights_basis=ContextRightsBasis.OWNER_SUPPLIED,
        )

    def test_renderer_uses_one_abstract_anchor_without_forced_motifs(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self._render(Path(tmp) / 'event.png')
            self.assertEqual(receipt.contract, 'pul7sar-event-editorial-study-renderer-v1-premium-anchor')
            self.assertTrue(receipt.single_anchor_used)
            self.assertFalse(receipt.person_used)
            self.assertFalse(receipt.full_pitch_used)
            self.assertFalse(receipt.decorative_stats_used)
            self.assertFalse(receipt.photographic_context_used)
            self.assertIsNone(receipt.context_contract)
            self.assertFalse(receipt.generator_used)
            self.assertFalse(receipt.network_used)
            self.assertTrue(receipt.study_only)
            self.assertFalse(receipt.publication_ready)
            self.assertLess(receipt.brand_width, 870)

    def test_verified_photographic_context_becomes_anchor_without_graphic_portal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            asset = self._fixture_asset(root)
            receipt = self._render(root / 'hybrid.png', context_asset=asset)
            self.assertTrue(receipt.photographic_context_used)
            self.assertFalse(receipt.single_anchor_used)
            self.assertEqual(receipt.context_contract, 'pul7sar-verified-context-surface-v1')
            self.assertEqual(receipt.context_source_reference, 'test://fixture-context')
            self.assertEqual(receipt.atmosphere_contract, 'pul7sar-verified-context-surface-v1')
            self.assertTrue((root / 'hybrid.png').is_file())

    def test_same_input_is_byte_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / 'a.png'
            b = Path(tmp) / 'b.png'
            first = self._render(a)
            second = self._render(b)
            self.assertEqual(first.output_sha256, second.output_sha256)
            self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_same_verified_context_is_byte_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            asset = self._fixture_asset(root)
            a = root / 'a-hybrid.png'
            b = root / 'b-hybrid.png'
            first = self._render(a, context_asset=asset)
            second = self._render(b, context_asset=asset)
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
