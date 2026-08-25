import hashlib
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from engine.intelligence.moment_led_result_renderer import MomentLedResultRenderer
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.result_statement_composition import ResultStatementComposer
from engine.intelligence.verified_story_moment import StoryMomentKind, StoryMomentRights, VerifiedStoryMomentAsset


class MomentLedResultRendererTests(unittest.TestCase):
    def setUp(self):
        self.profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
        self.composition = ResultStatementComposer().plan(self.profile)
        self.font = next((p for p in (
            Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
            Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
        ) if p.is_file()), None)
        if self.font is None:
            self.skipTest('DejaVu font unavailable')

    @staticmethod
    def _moment(root: Path) -> VerifiedStoryMomentAsset:
        path = root / 'moment.jpg'
        image = Image.new('RGB', (1500, 1000), (19, 31, 47))
        draw = ImageDraw.Draw(image)
        draw.ellipse((80, 120, 950, 960), fill=(72, 94, 123))
        draw.rectangle((1000, 0, 1500, 1000), fill=(8, 15, 26))
        image.save(path, quality=95)
        return VerifiedStoryMomentAsset(
            asset_id='verified-action-fixture',
            path=str(path),
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            source_reference='test://verified-action-fixture',
            moment_kind=StoryMomentKind.DECISIVE_ACTION,
            rights_basis=StoryMomentRights.OWNER_SUPPLIED,
            contains_people=False,
        )

    def _render(self, root: Path, name='result.png'):
        return MomentLedResultRenderer().render(
            self.composition,
            profile=self.profile,
            output_path=str(root / name),
            moment_asset=self._moment(root),
            home_name='HOME CLUB',
            away_name='AWAY CLUB',
            home_score=3,
            away_score=1,
            home_accent_hex='#034694',
            away_accent_hex='#B21F2D',
            brand_accent_hex='#034694',
            font_path=str(self.font),
        )

    def test_verified_photo_is_primary_and_score_is_secondary(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self._render(Path(tmp))
            self.assertEqual(receipt.contract, 'pul7sar-moment-led-result-renderer-v1')
            self.assertTrue(receipt.photograph_is_primary)
            self.assertTrue(receipt.score_is_secondary)
            self.assertEqual(receipt.score_text, '3  –  1')
            self.assertEqual(receipt.loser_treatment, 'neutral_no_humiliation')
            self.assertTrue(receipt.club_identity_scale_equal)
            self.assertFalse(receipt.generator_used)
            self.assertFalse(receipt.publication_ready)
            self.assertLess(receipt.brand_width, 870)

    def test_same_input_is_byte_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a = self._render(root, 'a.png')
            b = MomentLedResultRenderer().render(
                self.composition,
                profile=self.profile,
                output_path=str(root / 'b.png'),
                moment_asset=VerifiedStoryMomentAsset(
                    asset_id='verified-action-fixture',
                    path=str(root / 'moment.jpg'),
                    sha256=hashlib.sha256((root / 'moment.jpg').read_bytes()).hexdigest(),
                    source_reference='test://verified-action-fixture',
                    moment_kind=StoryMomentKind.DECISIVE_ACTION,
                    rights_basis=StoryMomentRights.OWNER_SUPPLIED,
                    contains_people=False,
                ),
                home_name='HOME CLUB', away_name='AWAY CLUB', home_score=3, away_score=1,
                home_accent_hex='#034694', away_accent_hex='#B21F2D', brand_accent_hex='#034694',
                font_path=str(self.font),
            )
            self.assertEqual(a.output_sha256, b.output_sha256)
            self.assertEqual((root/'a.png').read_bytes(), (root/'b.png').read_bytes())

    def test_wrong_moment_kind_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / 'object.jpg'
            Image.new('RGB', (800, 600), (10, 20, 30)).save(path)
            asset = VerifiedStoryMomentAsset(
                asset_id='detail', path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                source_reference='test://detail', moment_kind=StoryMomentKind.VERIFIED_OBJECT_DETAIL,
                rights_basis=StoryMomentRights.OWNER_SUPPLIED, contains_people=False,
            )
            with self.assertRaisesRegex(ValueError, 'REQUIRES_ACTION_OR_CELEBRATION'):
                MomentLedResultRenderer().render(
                    self.composition, profile=self.profile, output_path=str(root/'bad.png'), moment_asset=asset,
                    home_name='HOME', away_name='AWAY', home_score=1, away_score=0,
                    home_accent_hex='#034694', away_accent_hex='#B21F2D', brand_accent_hex='#034694',
                    font_path=str(self.font),
                )


if __name__ == '__main__':
    unittest.main()
