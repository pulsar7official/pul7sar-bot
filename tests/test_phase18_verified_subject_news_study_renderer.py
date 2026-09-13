import hashlib
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from engine.intelligence.models import IdentityPlan, IdentityStatus
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.verified_subject_compositor import VerifiedSubjectAsset, VerifiedSubjectMode
from engine.intelligence.verified_subject_news_composition import VerifiedSubjectNewsComposer
from engine.intelligence.verified_subject_news_study_renderer import VerifiedSubjectNewsStudyRenderer


class VerifiedSubjectNewsStudyRendererTests(unittest.TestCase):
    def setUp(self):
        self.profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
        self.composition = VerifiedSubjectNewsComposer().plan(self.profile)
        self.font = next(
            (p for p in (
                Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
                Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
            ) if p.is_file()),
            None,
        )
        if self.font is None:
            self.skipTest('DejaVu CI font unavailable')

    @staticmethod
    def _fixture(path: Path) -> VerifiedSubjectAsset:
        image = Image.new('RGBA', (320, 640), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image, 'RGBA')
        # Geometric engineering fixture only: deliberately not a human depiction.
        draw.rounded_rectangle((80, 40, 240, 600), radius=70, fill=(225, 230, 235, 255))
        draw.ellipse((105, 80, 215, 190), fill=(180, 190, 200, 255))
        image.save(path, format='PNG')
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        return VerifiedSubjectAsset(
            asset_id='engineering-fixture-001',
            entity_name='Engineering Fixture',
            path=str(path),
            sha256=digest,
            source_reference='internal-test-fixture',
            mode=VerifiedSubjectMode.TRANSPARENT_CUTOUT,
        )

    @staticmethod
    def _identity(*, verified: bool = True) -> IdentityPlan:
        return IdentityPlan(
            entity_name='Engineering Fixture',
            status=IdentityStatus.VERIFIED if verified else IdentityStatus.UNVERIFIED,
            sport='football',
            role='test fixture',
            confidence=1.0 if verified else 0.0,
            depiction_allowed=verified,
            reason='engineering provenance test',
        )

    def _render(self, root: Path, filename: str = 'subject-news.png'):
        subject = self._fixture(root / 'fixture.png')
        return VerifiedSubjectNewsStudyRenderer().render(
            self.composition,
            profile=self.profile,
            output_path=str(root / filename),
            subject=subject,
            identity=self._identity(),
            headline='VERIFIED SUBJECT UPDATE',
            context_text='FACT-LOCKED CONTEXT ONLY',
            accent_hex='#034694',
            brand_accent_hex='#034694',
            font_path=str(self.font),
        )

    def test_asset_first_renderer_preserves_identity_and_zone_safety(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self._render(Path(tmp))
            self.assertEqual(receipt.contract, 'pul7sar-verified-subject-news-study-renderer-v1-asset-first')
            self.assertTrue(receipt.identity_verified)
            self.assertEqual(receipt.identity_confidence, 1.0)
            self.assertFalse(receipt.subject_placeholder_used)
            self.assertFalse(receipt.fabricated_pose_used)
            self.assertFalse(receipt.fabricated_expression_used)
            self.assertFalse(receipt.fantasy_medical_scene_used)
            self.assertFalse(receipt.subject_text_overlap_used)
            self.assertFalse(receipt.brand_subject_overlap_used)
            self.assertEqual(receipt.brand_overlay_contract, 'pul7sar-adaptive-brand-overlay-v1')
            self.assertFalse(receipt.generator_used)
            self.assertFalse(receipt.network_used)
            self.assertTrue(receipt.study_only)
            self.assertFalse(receipt.publication_ready)

    def test_same_asset_and_copy_produce_identical_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = self._render(root, 'one.png')
            second = self._render(root, 'two.png')
            self.assertEqual(first.output_sha256, second.output_sha256)
            self.assertEqual((root/'one.png').read_bytes(), (root/'two.png').read_bytes())

    def test_unverified_identity_fails_before_subject_composition(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subject = self._fixture(root / 'fixture.png')
            with self.assertRaisesRegex(ValueError, 'requires VERIFIED depiction-allowed identity'):
                VerifiedSubjectNewsStudyRenderer().render(
                    self.composition,
                    profile=self.profile,
                    output_path=str(root/'blocked.png'),
                    subject=subject,
                    identity=self._identity(verified=False),
                    headline='VERIFIED SUBJECT UPDATE',
                    context_text='FACT-LOCKED CONTEXT ONLY',
                    accent_hex='#034694',
                    brand_accent_hex='#034694',
                    font_path=str(self.font),
                )
            self.assertFalse((root/'blocked.png').exists())

    def test_composition_contract_separates_subject_from_copy(self):
        subject = self.composition.subject_box
        for box in (self.composition.headline_box, self.composition.context_box):
            overlaps = not (
                subject.x + subject.width <= box.x
                or box.x + box.width <= subject.x
                or subject.y + subject.height <= box.y
                or box.y + box.height <= subject.y
            )
            self.assertFalse(overlaps)
        self.assertFalse(self.composition.subject_text_overlap_allowed)
        self.assertTrue(self.composition.brand_must_not_overlap_face)


if __name__ == '__main__':
    unittest.main()
