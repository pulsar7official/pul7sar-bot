import hashlib
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.premium_hybrid_result_study_renderer import PremiumHybridResultStudyRenderer
from engine.intelligence.result_statement_composition import ResultStatementComposer
from engine.intelligence.verified_context_surface import ContextRightsBasis, VerifiedContextAsset


class PremiumHybridResultStudyRendererTests(unittest.TestCase):
    def _fixture(self, root: Path) -> VerifiedContextAsset:
        path = root / "context.jpg"
        image = Image.new("RGB", (1600, 1000), (28, 36, 46))
        draw = ImageDraw.Draw(image)
        for y in range(image.height):
            t = y / image.height
            draw.line((0, y, image.width, y), fill=(round(24+36*t), round(34+42*t), round(48+58*t)))
        # Photo-like horizon lights with no people, marks or readable text.
        for x in range(80, 1520, 105):
            draw.ellipse((x-6, 290, x+6, 302), fill=(220, 225, 210))
        draw.rectangle((0, 650, 1600, 1000), fill=(24, 58, 42))
        image.save(path, quality=92)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        return VerifiedContextAsset(
            asset_id="unit-context",
            path=str(path),
            sha256=digest,
            source_reference="unit-test-owner-supplied",
            rights_basis=ContextRightsBasis.OWNER_SUPPLIED,
            contains_verified_person=False,
            publication_allowed=True,
        )

    def test_photographic_context_remains_atmosphere_only(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
            composition = ResultStatementComposer().plan(profile)
            font = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
            if not font.is_file():
                self.skipTest("CI font unavailable")
            receipt = PremiumHybridResultStudyRenderer().render(
                composition,
                profile=profile,
                output_path=str(root / "out.png"),
                context_asset=self._fixture(root),
                home_name="HOME CLUB",
                away_name="AWAY CLUB",
                home_score=3,
                away_score=1,
                headline="FULL TIME",
                home_accent_hex="#034694",
                away_accent_hex="#B21F2D",
                brand_accent_hex="#034694",
                font_path=str(font),
                winner="home",
            )
            self.assertEqual(receipt.context_role, "atmosphere_only_not_event_evidence")
            self.assertTrue(receipt.club_identity_scale_equal)
            self.assertTrue(receipt.home_identity_placeholder_used)
            self.assertTrue(receipt.away_identity_placeholder_used)
            self.assertFalse(receipt.generator_used)
            self.assertFalse(receipt.network_used_by_renderer)
            self.assertTrue(receipt.study_only)
            self.assertFalse(receipt.publication_ready)
            self.assertTrue((root / "out.png").is_file())
            self.assertEqual(hashlib.sha256((root / "out.png").read_bytes()).hexdigest(), receipt.output_sha256)

    def test_context_asset_with_person_is_rejected_before_renderer(self):
        with self.assertRaises(ValueError):
            VerifiedContextAsset(
                asset_id="bad",
                path="not-used.jpg",
                sha256="0" * 64,
                source_reference="bad",
                rights_basis=ContextRightsBasis.OWNER_SUPPLIED,
                contains_verified_person=True,
            )


if __name__ == "__main__":
    unittest.main()
