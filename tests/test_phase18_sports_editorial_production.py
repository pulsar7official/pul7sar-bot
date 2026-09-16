import unittest

from engine.intelligence.assets import AssetBundle
from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.scene_spec import OriginalSceneSpecification
from engine.intelligence.sports_editorial_production import SportsEditorialProductionCompiler
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent


class SportsEditorialProductionCompilerTests(unittest.TestCase):
    def setUp(self):
        self.compiler = SportsEditorialProductionCompiler()
        self.orchestrator = StoryToVisualOrchestrator()
        profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
        self.spec = OriginalSceneSpecification(
            platform=profile.platform,
            width=profile.width,
            height=profile.height,
            aspect_ratio=profile.aspect_ratio,
            safe_area={"top": 60, "right": 60, "bottom": 80, "left": 60},
            family="transfers",
            concept="verified sports editorial concept",
            subject="Verified Player",
            identity_reference=None,
            environment="generic environment",
            composition="generic composition",
            camera_direction="cinematic medium shot",
            emotional_mood="neutral",
            palette_strategy="verified entity accent",
            required_assets=(),
            visual_copy="PLAYER JOINS CLUB",
            factual_constraints=("verified fact",),
            forbidden_visual_elements=(),
            metadata={"dry_run": True},
        )

    def decision(self, event):
        return self.orchestrator.decide(VerifiedEditorialStory(
            event=event,
            sport="football",
            subject="Verified Player",
            fact_phrase="verified fact",
            story_core="verified story core",
            tone=HeadlineTone.NEUTRAL,
            confidence=0.99,
        ))

    def test_transfer_generation_package_cannot_skip_story_specific_scene(self):
        artifact = self.compiler.compile(self.decision(EditorialEvent.TRANSFER_CONFIRMED), self.spec, AssetBundle(()))
        package = artifact.generation_package
        self.assertEqual(artifact.scene_specification.family, "transfer_signature")
        self.assertEqual(package.metadata["sports_editorial_scene_family"], "transfer_signature")
        self.assertEqual(package.metadata["brand_identity_id"], "pul7sar-hybrid-adaptive-v1")
        self.assertTrue(package.metadata["premium_editorial_not_data_card"])
        self.assertIn("no mandatory pitch", package.scene_prompt)
        self.assertNotIn("pul7sar", package.scene_prompt.casefold())
        self.assertNotIn("pulsar", package.scene_prompt.casefold())

    def test_result_keeps_respectful_loser_rule_in_generation_context(self):
        artifact = self.compiler.compile(self.decision(EditorialEvent.RESULT), self.spec, AssetBundle(()))
        self.assertIn("neutral and respected", artifact.generation_package.scene_prompt)
        self.assertFalse(artifact.generation_package.metadata["supporting_copy_allowed"])

    def test_generator_bypass_story_is_rejected_from_generation_compiler(self):
        decision = self.decision(EditorialEvent.TACTICS)
        self.assertFalse(decision.execution_route.generator_required)
        with self.assertRaisesRegex(ValueError, "GENERATOR_BYPASS_STORY_MUST_USE_DIRECT_EXECUTION"):
            self.compiler.compile(decision, self.spec, AssetBundle(()))


if __name__ == "__main__":
    unittest.main()
