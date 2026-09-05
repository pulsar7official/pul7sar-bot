import unittest

from engine.intelligence.concept_director import ConceptBrief, ProposedConcept
from engine.intelligence.models import (
    ClaimKind,
    IdentityPlan,
    IdentityStatus,
    LockedClaim,
    Sentiment,
    VisualIntent,
)
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.scene_spec import SceneSpecCompiler


class PlatformSceneSpecTests(unittest.TestCase):
    def setUp(self):
        self.registry = PlatformProfileRegistry()
        self.compiler = SceneSpecCompiler()

    def test_each_platform_has_distinct_profile(self):
        profiles = self.registry.all()
        keys = {(p.platform, p.width, p.height) for p in profiles}
        self.assertEqual(len(keys), len(profiles))
        self.assertGreaterEqual(len(profiles), 7)

    def test_instagram_story_is_vertical(self):
        profile = self.registry.get(SocialPlatform.INSTAGRAM_STORY)
        self.assertEqual((profile.width, profile.height), (1080, 1920))
        self.assertEqual(profile.aspect_ratio, "9:16")

    def test_x_feed_is_landscape(self):
        profile = self.registry.get(SocialPlatform.X_FEED)
        self.assertEqual((profile.width, profile.height), (1600, 900))
        self.assertEqual(profile.aspect_ratio, "16:9")

    def test_telegram_post_keeps_current_landscape_world(self):
        profile = self.registry.get(SocialPlatform.TELEGRAM_POST)
        self.assertEqual((profile.width, profile.height), (1280, 720))

    def test_scene_spec_uses_platform_dimensions_and_safe_area(self):
        profile = self.registry.get(SocialPlatform.TIKTOK_PHOTO)
        intent = VisualIntent(
            family="general_world",
            concept="global sports season launch",
            sentiment=Sentiment.ANTICIPATORY,
            color_strategy="brand_red",
        )
        brief = ConceptBrief(
            family="general_world",
            objective="global sports season launch",
        )
        proposed = ProposedConcept(description="premium multi-league world")
        spec = self.compiler.compile(
            profile=profile,
            intent=intent,
            concept_brief=brief,
            proposed_concept=proposed,
        )
        self.assertEqual((spec.width, spec.height), (1080, 1920))
        self.assertEqual(spec.aspect_ratio, "9:16")
        self.assertGreater(spec.safe_area["bottom"], 0)
        self.assertTrue(spec.metadata["dry_run"])

    def test_verified_identity_is_carried_into_scene_spec(self):
        profile = self.registry.get(SocialPlatform.INSTAGRAM_FEED)
        identity = IdentityPlan(
            entity_name="Sam Hickey",
            status=IdentityStatus.VERIFIED,
            sport="boxing",
            role="middleweight boxer",
            gender="male",
            nationality="Scottish",
            confidence=0.98,
            depiction_allowed=True,
        )
        intent = VisualIntent(
            family="player_stories",
            concept="rising prospect portrait",
            sentiment=Sentiment.POSITIVE,
            hero_entity="Sam Hickey",
            identity_plan=identity,
            color_strategy="adaptive_entity_palette",
        )
        brief = ConceptBrief(
            family="player_stories",
            objective="rising prospect portrait",
        )
        proposed = ProposedConcept(description="authentic boxing portrait")
        spec = self.compiler.compile(
            profile=profile,
            intent=intent,
            concept_brief=brief,
            proposed_concept=proposed,
            locked_claims=(
                LockedClaim("Sam Hickey is a Scottish middleweight boxer", ClaimKind.FACT),
            ),
        )
        self.assertEqual(spec.identity_reference.entity_name, "Sam Hickey")
        self.assertEqual(spec.identity_reference.sport, "boxing")
        self.assertIn("Sam Hickey is a Scottish middleweight boxer", spec.factual_constraints)

    def test_unverified_identity_cannot_enter_scene_spec(self):
        profile = self.registry.get(SocialPlatform.INSTAGRAM_FEED)
        intent = VisualIntent(
            family="player_stories",
            concept="portrait",
            sentiment=Sentiment.NEUTRAL,
            hero_entity="Unknown Person",
            identity_plan=IdentityPlan(
                entity_name="Unknown Person",
                status=IdentityStatus.PARTIAL,
                confidence=0.5,
                depiction_allowed=False,
            ),
        )
        with self.assertRaises(ValueError):
            self.compiler.compile(
                profile=profile,
                intent=intent,
                concept_brief=ConceptBrief(family="player_stories", objective="portrait"),
                proposed_concept=ProposedConcept(description="portrait"),
            )


if __name__ == "__main__":
    unittest.main()
