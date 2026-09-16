import unittest

from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.sports_editorial_generation import SportsEditorialGenerationAugmenter
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent
from engine.intelligence.editorial_headline_grammar import HeadlineTone


class SportsEditorialGenerationAugmenterTests(unittest.TestCase):
    def setUp(self):
        self.augmenter = SportsEditorialGenerationAugmenter()
        self.orchestrator = StoryToVisualOrchestrator()
        self.base = GenerationPackage(
            platform="instagram_feed",
            canvas="1080x1350",
            scene_prompt="Create a clean premium football editorial base scene with no branding or readable text.",
            negative_constraints=(),
            asset_ids=(),
            factual_constraints=(),
            metadata={"generated_branding_allowed": False},
        )

    def scene(self, event):
        story = VerifiedEditorialStory(
            event=event,
            sport="football",
            subject="Verified Subject",
            fact_phrase="verified fact",
            story_core="verified story core",
            tone=HeadlineTone.NEUTRAL,
            confidence=0.99,
        )
        return self.orchestrator.decide(story).sports_editorial_scene

    def test_transfer_prompt_is_story_specific_and_not_pitch_forced(self):
        package = self.augmenter.augment(self.base, self.scene(EditorialEvent.TRANSFER_CONFIRMED))
        self.assertIn("transfer_signature", package.scene_prompt)
        self.assertIn("no mandatory pitch", package.scene_prompt)
        self.assertTrue(package.metadata["premium_editorial_not_data_card"])
        self.assertNotIn("pul7sar", package.scene_prompt.casefold())
        self.assertNotIn("pulsar", package.scene_prompt.casefold())

    def test_result_prompt_preserves_respectful_loser_treatment(self):
        package = self.augmenter.augment(self.base, self.scene(EditorialEvent.RESULT))
        self.assertIn("neutral and respected", package.scene_prompt)
        self.assertFalse(package.metadata["supporting_copy_allowed"])

    def test_brand_and_dense_copy_remain_forbidden_generated_elements(self):
        package = self.augmenter.augment(self.base, self.scene(EditorialEvent.TRANSFER_CONFIRMED))
        self.assertIn("generated readable PUL7SAR wordmark", package.negative_constraints)
        self.assertIn("dense infographic copy", package.negative_constraints)
        self.assertIn("generic ECG substituted for PUL7SAR pulse signature", package.negative_constraints)
        ownership = package.metadata["sports_editorial_deterministic_ownership"]
        self.assertIn("PUL7SAR fixed metallic wordmark geometry", ownership)
        self.assertIn("PUL7SAR enlarged 7 geometry", ownership)
        self.assertIn("PUL7SAR integrated pulse signature centered on 7", ownership)
        self.assertIn("PUL7SAR small football near R geometry", ownership)


if __name__ == "__main__":
    unittest.main()
