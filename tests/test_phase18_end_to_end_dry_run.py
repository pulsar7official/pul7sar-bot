import unittest

from engine.intelligence.assets import AssetBundle, AssetReference, AssetRole, AssetTreatment
from engine.intelligence.batch_scene import MultiPlatformSceneCompiler
from engine.intelligence.concept_director import ConceptDirector, ProposedConcept
from engine.intelligence.dry_run_manifest import DryRunManifestCompiler
from engine.intelligence.entity_theme import EntityPaletteEvidence
from engine.intelligence.layout_planner import LayoutRequirements
from engine.intelligence.models import ClaimKind, LockedClaim, Sentiment, VisualIntent
from engine.intelligence.platform_profiles import SocialPlatform


class EndToEndDryRunFixtureTests(unittest.TestCase):
    """Editorial regression fixture; it validates pipeline behavior, not live news truth."""

    def setUp(self):
        self.scene_compiler = MultiPlatformSceneCompiler()
        self.manifest_compiler = DryRunManifestCompiler()
        self.director = ConceptDirector()

        self.assets = AssetBundle((
            AssetReference("pul7sar-wordmark-official", AssetRole.PUL7SAR_LOGO, AssetTreatment.EXACT),
            AssetReference("pul7sar-seven-pulse-official", AssetRole.PUL7SAR_PULSE, AssetTreatment.TINTABLE_ACCENT),
            AssetReference("arsenal-crest-official", AssetRole.TEAM_CREST, AssetTreatment.EXACT, display_name="Arsenal"),
            AssetReference("social-instagram", AssetRole.SOCIAL_ICON, AssetTreatment.EXACT, metadata={"platform": "instagram"}),
            AssetReference("social-facebook", AssetRole.SOCIAL_ICON, AssetTreatment.EXACT, metadata={"platform": "facebook"}),
            AssetReference("social-x", AssetRole.SOCIAL_ICON, AssetTreatment.EXACT, metadata={"platform": "x"}),
            AssetReference("social-threads", AssetRole.SOCIAL_ICON, AssetTreatment.EXACT, metadata={"platform": "threads"}),
            AssetReference("social-tiktok", AssetRole.SOCIAL_ICON, AssetTreatment.EXACT, metadata={"platform": "tiktok"}),
            AssetReference("social-telegram", AssetRole.SOCIAL_ICON, AssetTreatment.EXACT, metadata={"platform": "telegram"}),
        ))

    def test_transfer_story_compiles_to_fully_inspectable_cross_platform_manifest(self):
        # Synthetic regression fixture based on the earlier PUL7SAR transfer-story shape.
        # It intentionally preserves "approach" rather than asserting a completed signing.
        intent = VisualIntent(
            family="transfers",
            concept="show transfer momentum and negotiation without implying a completed signing",
            sentiment=Sentiment.ANTICIPATORY,
            hero_entity="Alberto Alvarez",
            visual_copy="Arsenal move closer",
            color_strategy="adaptive_entity_palette",
            metadata={"requires_identity_gate": False},
        )
        brief = self.director.build_brief(intent)
        concept = ProposedConcept(
            description="premium transfer scene with Arsenal visual context and directional movement, no signing ceremony",
            claimed_constraints=brief.required_constraints,
        )
        self.director.validate(brief, concept)

        claims = (
            LockedClaim(
                "Arsenal are approaching a deal",
                ClaimKind.FACT,
                source="fixture-source",
                confidence=0.95,
            ),
            LockedClaim(
                "The transfer is not represented as completed",
                ClaimKind.SAFE_INFERENCE,
                source="editorial-guard",
                confidence=1.0,
            ),
        )

        packages = self.scene_compiler.compile(
            platforms=(
                SocialPlatform.INSTAGRAM_FEED,
                SocialPlatform.INSTAGRAM_STORY,
                SocialPlatform.FACEBOOK_FEED,
                SocialPlatform.X_FEED,
                SocialPlatform.THREADS_FEED,
                SocialPlatform.TIKTOK_PHOTO,
                SocialPlatform.TELEGRAM_POST,
            ),
            intent=intent,
            concept_brief=brief,
            proposed_concept=concept,
            assets=self.assets,
            locked_claims=claims,
            extra_forbidden_elements=("completed signing ceremony", "contract signature", "fake official announcement"),
            layout_requirements=LayoutRequirements(include_crest=True),
            entity_palette_evidence=EntityPaletteEvidence(
                "Arsenal", "#EF0107", 0.98, "verified-brand-palette-fixture"
            ),
        )

        manifest = self.manifest_compiler.compile("fixture-transfer-arsenal-001", packages).to_dict()
        self.assertEqual(len(manifest["platforms"]), 7)

        instagram = manifest["platforms"][SocialPlatform.INSTAGRAM_FEED.value]
        x = manifest["platforms"][SocialPlatform.X_FEED.value]
        telegram = manifest["platforms"][SocialPlatform.TELEGRAM_POST.value]

        self.assertEqual(instagram["theme"]["accent_hex"], "#EF0107")
        self.assertTrue(instagram["theme"]["verified"])
        self.assertTrue(instagram["brand_plan"]["preserve_wordmark_exact"])
        self.assertTrue(instagram["brand_plan"]["preserve_team_crests_exact"])
        self.assertEqual(instagram["brand_plan"]["pulse_tint_hex"], "#EF0107")

        self.assertIn("social-instagram", instagram["asset_ids"])
        self.assertNotIn("social-x", instagram["asset_ids"])
        self.assertIn("social-x", x["asset_ids"])
        self.assertNotIn("social-instagram", x["asset_ids"])
        self.assertIn("social-telegram", telegram["asset_ids"])

        self.assertEqual(instagram["canvas"], "1080x1350")
        self.assertEqual(manifest["platforms"][SocialPlatform.INSTAGRAM_STORY.value]["canvas"], "1080x1920")
        self.assertEqual(x["canvas"], "1600x900")
        self.assertEqual(telegram["canvas"], "1280x720")
        self.assertNotEqual(instagram["layout_boxes"]["hero"], x["layout_boxes"]["hero"])

        self.assertIn("Arsenal are approaching a deal", instagram["factual_constraints"])
        self.assertNotIn("The transfer is not represented as completed", instagram["factual_constraints"])
        self.assertIn("no_unverified_signing", instagram["negative_constraints"])
        self.assertIn("completed signing ceremony", instagram["negative_constraints"])
        self.assertIn("Arsenal", instagram["scene_prompt"])
        self.assertNotIn("social-facebook", instagram["asset_ids"])


if __name__ == "__main__":
    unittest.main()
