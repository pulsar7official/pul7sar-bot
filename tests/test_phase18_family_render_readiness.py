import unittest
from dataclasses import replace

from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.family_render_plan import FamilyRenderPlanner
from engine.intelligence.family_render_readiness import FamilyRenderReadiness, FamilyRenderReadinessGate
from engine.intelligence.platform_editorial_composition import PlatformEditorialCompositionResolver
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent


class FamilyRenderReadinessTests(unittest.TestCase):
    def setUp(self):
        self.orchestrator = StoryToVisualOrchestrator()
        self.compositions = PlatformEditorialCompositionResolver()
        self.planner = FamilyRenderPlanner()
        self.gate = FamilyRenderReadinessGate()
        self.profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)

    def pair(self, event):
        story = VerifiedEditorialStory(
            event=event,
            sport="football",
            subject="Verified Subject",
            secondary_subjects=("Verified Secondary",),
            fact_phrase="verified fact",
            story_core="verified core",
            tone=HeadlineTone.NEUTRAL,
            confidence=0.99,
        )
        decision = self.orchestrator.decide(story)
        composition = self.compositions.resolve(decision, self.profile)
        return composition, self.planner.plan(composition)

    def test_all_six_families_are_structurally_render_ready_but_not_publication_ready(self):
        for event in (
            EditorialEvent.TRANSFER_CONFIRMED,
            EditorialEvent.RESULT,
            EditorialEvent.INJURY,
            EditorialEvent.TACTICS,
            EditorialEvent.TABLE,
            EditorialEvent.GENERAL,
        ):
            composition, plan = self.pair(event)
            verdict = self.gate.evaluate(composition, plan)
            self.assertEqual(verdict.status, FamilyRenderReadiness.RENDER_STRUCTURE_READY)
            self.assertTrue(verdict.render_allowed)
            self.assertFalse(verdict.publication_allowed)
            self.assertEqual(verdict.failures, ())

    def test_family_mismatch_fails_closed(self):
        transfer, transfer_plan = self.pair(EditorialEvent.TRANSFER_CONFIRMED)
        result, _ = self.pair(EditorialEvent.RESULT)
        verdict = self.gate.evaluate(result, transfer_plan)
        self.assertFalse(verdict.render_allowed)
        self.assertIn("composition and render plan story families differ", verdict.failures)

    def test_stale_platform_contract_fails_closed(self):
        composition, plan = self.pair(EditorialEvent.RESULT)
        stale = replace(composition, contract="pul7sar-platform-editorial-composition-v3")
        verdict = self.gate.evaluate(stale, plan)
        self.assertFalse(verdict.render_allowed)
        self.assertIn("platform composition contract is stale", verdict.failures)

    def test_render_plan_cannot_self_authorize_publication(self):
        _, plan = self.pair(EditorialEvent.INJURY)
        with self.assertRaisesRegex(ValueError, "RENDER_PLAN_ALONE_CANNOT_AUTHORIZE_PUBLICATION"):
            replace(plan, publication_ready=True)

    def test_assert_renderable_raises_on_mismatch(self):
        transfer, transfer_plan = self.pair(EditorialEvent.TRANSFER_CONFIRMED)
        result, _ = self.pair(EditorialEvent.RESULT)
        with self.assertRaisesRegex(ValueError, "FAMILY_RENDER_NOT_READY"):
            self.gate.assert_renderable(result, transfer_plan)


if __name__ == "__main__":
    unittest.main()
