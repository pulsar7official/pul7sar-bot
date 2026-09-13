import unittest

from engine.intelligence.assets import (
    AssetBundle,
    AssetReference,
    AssetRole,
    AssetTreatment,
)
from engine.intelligence.batch_scene import MultiPlatformSceneCompiler
from engine.intelligence.concept_director import ConceptBrief, ProposedConcept
from engine.intelligence.layout_safety import ElementBox, LayoutRole, PlatformLayoutSafetyGate
from engine.intelligence.models import Sentiment, VisualIntent
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform


class BatchAssetLayoutTests(unittest.TestCase):
    def _assets(self):
        return AssetBundle((
            AssetReference("pul7sar-wordmark-v1", AssetRole.PUL7SAR_LOGO, AssetTreatment.EXACT),
            AssetReference(
                "pul7sar-pulse-v1",
                AssetRole.PUL7SAR_PULSE,
                AssetTreatment.TINTABLE_ACCENT,
                accent_color="#EF233C",
            ),
            AssetReference("arsenal-crest-official", AssetRole.TEAM_CREST, AssetTreatment.EXACT),
            AssetReference("instagram-icon", AssetRole.SOCIAL_ICON, AssetTreatment.EXACT),
        ))

    def test_brand_bundle_requires_exact_wordmark(self):
        bundle = AssetBundle((
            AssetReference("bad-logo", AssetRole.PUL7SAR_LOGO, AssetTreatment.TINTABLE_ACCENT),
            AssetReference("pulse", AssetRole.PUL7SAR_PULSE, AssetTreatment.EXACT),
        ))
        with self.assertRaises(ValueError):
            bundle.assert_brand_ready()

    def test_team_crest_cannot_be_tintable(self):
        bundle = AssetBundle((
            AssetReference("logo", AssetRole.PUL7SAR_LOGO, AssetTreatment.EXACT),
            AssetReference("pulse", AssetRole.PUL7SAR_PULSE, AssetTreatment.EXACT),
            AssetReference("crest", AssetRole.TEAM_CREST, AssetTreatment.TINTABLE_ACCENT),
        ))
        with self.assertRaises(ValueError):
            bundle.assert_team_crests_exact()

    def test_one_story_compiles_to_distinct_platform_canvases(self):
        compiler = MultiPlatformSceneCompiler()
        intent = VisualIntent(
            family="general_world",
            concept="major European leagues return",
            sentiment=Sentiment.ANTICIPATORY,
            color_strategy="brand_red",
        )
        brief = ConceptBrief(
            family="general_world",
            objective="represent the wider sports world",
        )
        concept = ProposedConcept(description="premium multi-league editorial world")
        output = compiler.compile(
            platforms=(
                SocialPlatform.INSTAGRAM_FEED,
                SocialPlatform.INSTAGRAM_STORY,
                SocialPlatform.X_FEED,
            ),
            intent=intent,
            concept_brief=brief,
            proposed_concept=concept,
            assets=self._assets(),
        )
        self.assertEqual(len(output), 3)
        canvases = {item.generation_package.canvas for item in output}
        self.assertEqual(canvases, {"1080x1350", "1080x1920", "1600x900"})
        self.assertTrue(all(item.generation_package.metadata["dry_run"] for item in output))

    def test_batch_rejects_duplicate_platform(self):
        compiler = MultiPlatformSceneCompiler()
        intent = VisualIntent("general_world", "general", Sentiment.NEUTRAL)
        brief = ConceptBrief("general_world", "general")
        concept = ProposedConcept("general")
        with self.assertRaises(ValueError):
            compiler.compile(
                platforms=(SocialPlatform.X_FEED, SocialPlatform.X_FEED),
                intent=intent,
                concept_brief=brief,
                proposed_concept=concept,
                assets=self._assets(),
            )

    def test_safe_zone_accepts_critical_elements_inside_profile(self):
        profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_STORY)
        gate = PlatformLayoutSafetyGate()
        boxes = (
            ElementBox(LayoutRole.LOGO, 100, 240, 220, 80),
            ElementBox(LayoutRole.HERO, 160, 400, 700, 900),
            ElementBox(LayoutRole.HEADLINE, 120, 1350, 840, 180),
            ElementBox(LayoutRole.SOCIAL_FOOTER, 150, 1550, 780, 60),
        )
        self.assertTrue(gate.evaluate(profile, boxes).allowed)

    def test_safe_zone_rejects_footer_in_story_ui_risk_area(self):
        profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_STORY)
        gate = PlatformLayoutSafetyGate()
        decision = gate.evaluate(profile, (
            ElementBox(LayoutRole.SOCIAL_FOOTER, 100, 1750, 800, 80),
        ))
        self.assertFalse(decision.allowed)
        self.assertIn("social_footer leaves safe area", decision.violations)


if __name__ == "__main__":
    unittest.main()
