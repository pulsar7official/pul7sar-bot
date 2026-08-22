import unittest

from engine.intelligence.assets import AssetBundle, AssetReference, AssetRole, AssetTreatment
from engine.intelligence.brand_semantics import BrandPlacementPlanner
from engine.intelligence.entity_theme import EntityPaletteEvidence, EntityThemeResolver
from engine.intelligence.platform_profiles import SocialPlatform
from engine.intelligence.social_assets import DestinationSocialAssetSelector


class BrandThemeSocialTests(unittest.TestCase):
    def setUp(self):
        self.bundle = AssetBundle((
            AssetReference("pul7sar-logo", AssetRole.PUL7SAR_LOGO, AssetTreatment.EXACT),
            AssetReference("pul7sar-pulse", AssetRole.PUL7SAR_PULSE, AssetTreatment.TINTABLE_ACCENT),
            AssetReference("arsenal-crest", AssetRole.TEAM_CREST, AssetTreatment.EXACT),
            AssetReference("ig-icon", AssetRole.SOCIAL_ICON, AssetTreatment.EXACT, metadata={"platform": "instagram"}),
            AssetReference("x-icon", AssetRole.SOCIAL_ICON, AssetTreatment.EXACT, metadata={"platform": "x"}),
            AssetReference("tg-icon", AssetRole.SOCIAL_ICON, AssetTreatment.EXACT, metadata={"platform": "telegram"}),
        ))

    def test_general_story_theme_defaults_to_pul7sar_red(self):
        theme = EntityThemeResolver().resolve(None)
        self.assertEqual(theme.accent_hex, "#E10600")
        self.assertFalse(theme.verified)

    def test_verified_entity_palette_controls_only_tintable_accent(self):
        theme = EntityThemeResolver().resolve(EntityPaletteEvidence(
            entity_name="Arsenal",
            primary_hex="#EF0107",
            confidence=0.95,
            source="verified-club-palette",
        ))
        plan = BrandPlacementPlanner().plan(self.bundle, theme)
        self.assertEqual(plan.pulse_tint_hex, "#EF0107")
        self.assertTrue(plan.preserve_wordmark_exact)
        self.assertTrue(plan.preserve_team_crests_exact)

    def test_low_confidence_palette_falls_back_to_pul7sar_red(self):
        theme = EntityThemeResolver().resolve(EntityPaletteEvidence(
            entity_name="Club",
            primary_hex="#123456",
            confidence=0.30,
            source="weak-source",
        ))
        self.assertEqual(theme.accent_hex, "#E10600")
        self.assertFalse(theme.verified)

    def test_instagram_destination_keeps_only_instagram_social_icon(self):
        selected = DestinationSocialAssetSelector().select(SocialPlatform.INSTAGRAM_STORY, self.bundle)
        ids = {asset.asset_id for asset in selected.assets}
        self.assertIn("ig-icon", ids)
        self.assertNotIn("x-icon", ids)
        self.assertNotIn("tg-icon", ids)
        self.assertIn("pul7sar-logo", ids)
        self.assertIn("arsenal-crest", ids)

    def test_x_destination_keeps_only_x_icon(self):
        selected = DestinationSocialAssetSelector().select(SocialPlatform.X_FEED, self.bundle)
        ids = {asset.asset_id for asset in selected.assets}
        self.assertIn("x-icon", ids)
        self.assertNotIn("ig-icon", ids)

    def test_duplicate_destination_icon_is_rejected(self):
        bundle = AssetBundle(self.bundle.assets + (
            AssetReference("ig-icon-2", AssetRole.SOCIAL_ICON, AssetTreatment.EXACT, metadata={"platform": "instagram"}),
        ))
        with self.assertRaises(ValueError):
            DestinationSocialAssetSelector().select(SocialPlatform.INSTAGRAM_FEED, bundle)


if __name__ == "__main__":
    unittest.main()
