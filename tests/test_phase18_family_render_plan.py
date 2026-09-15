import unittest

from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.family_render_plan import FamilyRenderPlanner, RenderOwner
from engine.intelligence.platform_editorial_composition import PlatformEditorialCompositionResolver
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent


class FamilyRenderPlanTests(unittest.TestCase):
    def setUp(self):
        self.orchestrator = StoryToVisualOrchestrator()
        self.compositions = PlatformEditorialCompositionResolver()
        self.planner = FamilyRenderPlanner()
        self.profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)

    def render_plan(self, event):
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
        return self.planner.plan(self.compositions.resolve(decision, self.profile))

    def test_all_families_end_with_deterministic_brand_then_qa(self):
        for event in (
            EditorialEvent.TRANSFER_CONFIRMED,
            EditorialEvent.RESULT,
            EditorialEvent.INJURY,
            EditorialEvent.TACTICS,
            EditorialEvent.TABLE,
            EditorialEvent.GENERAL,
        ):
            plan = self.render_plan(event)
            self.assertEqual(plan.stages[-2].stage_id, "pul7sar_brand")
            self.assertEqual(plan.stages[-2].owner, RenderOwner.DETERMINISTIC)
            self.assertEqual(plan.stages[-1].stage_id, "visual_qa")
            self.assertFalse(plan.readable_text_generator_owned)
            self.assertFalse(plan.exact_data_generator_owned)
            self.assertFalse(plan.exact_identity_generator_owned)
            self.assertFalse(plan.publication_ready)

    def test_transfer_uses_verified_hero_before_exact_club_and_copy(self):
        plan = self.render_plan(EditorialEvent.TRANSFER_CONFIRMED)
        ids = [stage.stage_id for stage in plan.stages]
        self.assertLess(ids.index("verified_hero"), ids.index("exact_club_context"))
        self.assertLess(ids.index("exact_club_context"), ids.index("editorial_copy"))

    def test_result_uses_exact_score_and_balanced_identity(self):
        plan = self.render_plan(EditorialEvent.RESULT)
        stages = {stage.stage_id: stage for stage in plan.stages}
        self.assertEqual(stages["balanced_club_identities"].owner, RenderOwner.DETERMINISTIC)
        self.assertTrue(stages["exact_score"].exact)
        self.assertEqual(stages["exact_score"].owner, RenderOwner.DETERMINISTIC)

    def test_injury_uses_verified_asset_not_generated_identity(self):
        plan = self.render_plan(EditorialEvent.INJURY)
        stage = next(stage for stage in plan.stages if stage.stage_id == "verified_subject")
        self.assertEqual(stage.owner, RenderOwner.VERIFIED_ASSET)
        self.assertTrue(stage.exact)

    def test_tactics_has_no_optional_atmosphere_stage(self):
        plan = self.render_plan(EditorialEvent.TACTICS)
        self.assertFalse(any(stage.owner is RenderOwner.OPTIONAL_ATMOSPHERE for stage in plan.stages))
        self.assertEqual(plan.stages[0].stage_id, "deterministic_sport_geometry")

    def test_family_stage_orders_are_not_one_template(self):
        plans = [
            self.render_plan(event)
            for event in (
                EditorialEvent.TRANSFER_CONFIRMED,
                EditorialEvent.RESULT,
                EditorialEvent.INJURY,
                EditorialEvent.TACTICS,
                EditorialEvent.TABLE,
                EditorialEvent.GENERAL,
            )
        ]
        signatures = {tuple(stage.stage_id for stage in plan.stages) for plan in plans}
        self.assertEqual(len(signatures), 6)


if __name__ == "__main__":
    unittest.main()
