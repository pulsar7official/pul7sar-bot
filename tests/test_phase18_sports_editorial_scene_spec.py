import unittest

from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.scene_spec import OriginalSceneSpecification
from engine.intelligence.sports_editorial_scene_spec import SportsEditorialSceneSpecAugmenter
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent
from engine.intelligence.editorial_headline_grammar import HeadlineTone


class SportsEditorialSceneSpecAugmenterTests(unittest.TestCase):
    def setUp(self):
        self.augmenter = SportsEditorialSceneSpecAugmenter()
        self.orchestrator = StoryToVisualOrchestrator()
        profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
        self.base = OriginalSceneSpecification(
            platform=profile.platform,
            width=profile.width,
            height=profile.height,
            aspect_ratio=profile.aspect_ratio,
            safe_area={"top": 60, "right": 60, "bottom": 80, "left": 60},
            family="transfers",
            concept="verified transfer scene",
            subject="Verified Player",
            identity_reference=None,
            environment="generic transfer environment",
            composition="generic composition",
            camera_direction="cinematic medium shot",
            emotional_mood="neutral",
            palette_strategy="verified club palette",
            required_assets=(),
            visual_copy="PLAYER JOINS CLUB",
            factual_constraints=("transfer confirmed",),
            forbidden_visual_elements=(),
            metadata={"dry_run": True},
        )

    def scene(self, event):
        story = VerifiedEditorialStory(
            event=event,
            sport="football",
            subject="Verified Player",
            fact_phrase="verified fact",
            story_core="verified story core",
            tone=HeadlineTone.NEUTRAL,
            confidence=0.99,
        )
        return self.orchestrator.decide(story).sports_editorial_scene

    def test_transfer_spec_becomes_transfer_signature_not_generic_transfer_template(self):
        spec = self.augmenter.augment(self.base, self.scene(EditorialEvent.TRANSFER_CONFIRMED))
        self.assertEqual(spec.family, "transfer_signature")
        self.assertIn("no mandatory pitch", spec.environment)
        self.assertIn("premium signing reveal", spec.composition)
        self.assertTrue(spec.metadata["premium_editorial_not_data_card"])
        self.assertIn("contextual accent only", spec.palette_strategy)

    def test_scene_forbidden_rules_propagate_to_scene_spec(self):
        spec = self.augmenter.augment(self.base, self.scene(EditorialEvent.TRANSFER_CONFIRMED))
        self.assertIn("legacy repository logo as canonical identity", spec.forbidden_visual_elements)
        self.assertIn("dense infographic copy", spec.forbidden_visual_elements)
        self.assertIn("forced full football pitch when story does not require it", spec.forbidden_visual_elements)


if __name__ == "__main__":
    unittest.main()
