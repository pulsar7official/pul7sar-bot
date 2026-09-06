import unittest

from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent
from engine.intelligence.verified_subject_editorial_pipeline import (
    VerifiedSubjectEditorialPipelinePlanner,
    VerifiedSubjectStage,
)


class VerifiedSubjectEditorialPipelineTests(unittest.TestCase):
    def scene(self, event):
        return StoryToVisualOrchestrator().decide(VerifiedEditorialStory(
            event=event,
            sport="football",
            subject="Verified Player",
            fact_phrase="verified update",
            story_core="verified identity-led story",
            tone=HeadlineTone.NEUTRAL,
            confidence=1.0,
        )).sports_editorial_scene

    def test_transfer_layer_order_is_locked(self):
        pipeline = VerifiedSubjectEditorialPipelinePlanner().compile(self.scene(EditorialEvent.TRANSFER_CONFIRMED))
        self.assertEqual(
            [step.stage for step in pipeline.steps],
            [
                VerifiedSubjectStage.PREPARE_ATMOSPHERE,
                VerifiedSubjectStage.COMPOSE_VERIFIED_SUBJECT,
                VerifiedSubjectStage.APPLY_EXACT_CONTEXT_ASSETS,
                VerifiedSubjectStage.APPLY_EDITORIAL_COPY,
                VerifiedSubjectStage.APPLY_PUL7SAR_IDENTITY,
                VerifiedSubjectStage.VISUAL_QA,
                VerifiedSubjectStage.EXPORT_CANDIDATE,
            ],
        )
        self.assertFalse(pipeline.generator_may_own_subject)
        self.assertFalse(pipeline.placeholder_allowed_in_real_candidate)
        self.assertFalse(pipeline.publication_ready)

    def test_injury_uses_same_verified_subject_safety_order(self):
        pipeline = VerifiedSubjectEditorialPipelinePlanner().compile(self.scene(EditorialEvent.INJURY))
        subject_step = next(step for step in pipeline.steps if step.stage is VerifiedSubjectStage.COMPOSE_VERIFIED_SUBJECT)
        self.assertIn("SHA-locked", subject_step.instruction)
        self.assertIn("no face generation", subject_step.instruction)

    def test_result_is_not_forced_through_person_pipeline(self):
        with self.assertRaisesRegex(ValueError, "identity-led"):
            VerifiedSubjectEditorialPipelinePlanner().compile(self.scene(EditorialEvent.RESULT))


if __name__ == "__main__":
    unittest.main()
