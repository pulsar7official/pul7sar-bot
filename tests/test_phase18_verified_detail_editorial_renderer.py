import hashlib
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from engine.intelligence.adaptive_brand_placement import AdaptiveBrandPlacementResolver
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily
from engine.intelligence.verified_detail_editorial_renderer import (
    DetailEditorialMode,
    VerifiedDetailEditorialRenderer,
)
from engine.intelligence.verified_story_moment import (
    StoryMomentKind,
    StoryMomentRights,
    VerifiedStoryMomentAsset,
)


class VerifiedDetailEditorialRendererTests(unittest.TestCase):
    def setUp(self):
        self.profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
        self.brand = AdaptiveBrandPlacementResolver().resolve(
            family=EditorialSceneFamily.TRANSFER_SIGNATURE,
            profile=self.profile,
        )
        self.font = next((p for p in (
            Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
            Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
        ) if p.is_file()), None)
        if self.font is None:
            self.skipTest('DejaVu font unavailable')

    @staticmethod
    def _asset(root: Path, kind=StoryMomentKind.VERIFIED_OBJECT_DETAIL):
        path = root / 'detail.jpg'
        image = Image.new('RGB', (1400, 1000), (14, 26, 40))
        draw = ImageDraw.Draw(image)
        draw.rectangle((720, 100, 1250, 880), fill=(105, 116, 129))
        draw.ellipse((800, 220, 1160, 580), fill=(177, 187, 196))
        image.save(path, quality=95)
        return VerifiedStoryMomentAsset(
            asset_id='verified-detail-fixture',
            path=str(path),
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            source_reference='test://verified-detail',
            moment_kind=kind,
            rights_basis=StoryMomentRights.OWNER_SUPPLIED,
            contains_people=False,
        )

    def _render(self, root: Path, output='detail.png', mode=DetailEditorialMode.SYMBOLIC_SIGNING):
        return VerifiedDetailEditorialRenderer().render(
            profile=self.profile,
            adaptive_brand=self.brand,
            output_path=str(root/output),
            asset=self._asset(root),
            mode=mode,
            headline='NEW SIGNING',
            kicker='OFFICIAL MOVE',
            accent_hex='#034694',
            font_path=str(self.font),
        )

    def test_symbolic_signing_is_photo_led_without_fake_person_or_pulse(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self._render(Path(tmp))
            self.assertEqual(receipt.contract, 'pul7sar-verified-detail-editorial-renderer-v1')
            self.assertTrue(receipt.photograph_is_primary)
            self.assertFalse(receipt.person_fabricated)
            self.assertFalse(receipt.decorative_pulse_used)
            self.assertFalse(receipt.generator_used)
            self.assertFalse(receipt.publication_ready)
            self.assertLess(receipt.brand_width, 870)

    def test_same_input_is_byte_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = self._render(root, 'a.png')
            second = VerifiedDetailEditorialRenderer().render(
                profile=self.profile,
                adaptive_brand=self.brand,
                output_path=str(root/'b.png'),
                asset=VerifiedStoryMomentAsset(
                    asset_id='verified-detail-fixture',
                    path=str(root/'detail.jpg'),
                    sha256=hashlib.sha256((root/'detail.jpg').read_bytes()).hexdigest(),
                    source_reference='test://verified-detail',
                    moment_kind=StoryMomentKind.VERIFIED_OBJECT_DETAIL,
                    rights_basis=StoryMomentRights.OWNER_SUPPLIED,
                    contains_people=False,
                ),
                mode=DetailEditorialMode.SYMBOLIC_SIGNING,
                headline='NEW SIGNING', kicker='OFFICIAL MOVE', accent_hex='#034694', font_path=str(self.font),
            )
            self.assertEqual(first.output_sha256, second.output_sha256)
            self.assertEqual((root/'a.png').read_bytes(), (root/'b.png').read_bytes())

    def test_person_bearing_detail_is_rejected_even_if_identity_metadata_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            path=root/'person.jpg'
            Image.new('RGB',(900,700),(20,30,40)).save(path)
            asset=VerifiedStoryMomentAsset(
                asset_id='person-detail',path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                source_reference='test://person',moment_kind=StoryMomentKind.PRESS_MOMENT,
                rights_basis=StoryMomentRights.OWNER_SUPPLIED,contains_people=True,
                verified_identity_ids=('person:001',),
            )
            with self.assertRaisesRegex(ValueError,'MUST_NOT_CONTAIN_PEOPLE'):
                VerifiedDetailEditorialRenderer().render(
                    profile=self.profile,adaptive_brand=self.brand,output_path=str(root/'bad.png'),asset=asset,
                    mode=DetailEditorialMode.VERIFIED_EVIDENCE,headline='DETAIL',kicker='VERIFIED',
                    accent_hex='#034694',font_path=str(self.font),
                )


if __name__=='__main__':
    unittest.main()
