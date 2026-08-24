import unittest

from engine.intelligence.assets import AssetBundle, AssetReference, AssetRole, AssetTreatment
from engine.intelligence.direct_visual_execution import (
    DirectBaseSource,
    DirectExecutionStage,
    DirectVisualExecutionPlanner,
)
from engine.intelligence.layout_planner import DeterministicLayoutPlanner, LayoutRequirements
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent
from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.visual_execution_route import PixelExecutionRoute


class DirectVisualExecutionPlannerTests(unittest.TestCase):
    def setUp(self):
        self.orchestrator = StoryToVisualOrchestrator()
        self.planner = DirectVisualExecutionPlanner()
        self.profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
        self.layout = DeterministicLayoutPlanner().plan(
            self.profile,
            LayoutRequirements(include_score=True, include_crest=True),
            entity_accent_hex="#EF0107",
        )
        self.assets = AssetBundle((
            AssetReference("pul7sar-logo", AssetRole.PUL7SAR_LOGO, AssetTreatment.EXACT),
            AssetReference("pul7sar-pulse", AssetRole.PUL7SAR_PULSE, AssetTreatment.TINTABLE_ACCENT),
            AssetReference("club-crest", AssetRole.TEAM_CREST, AssetTreatment.EXACT),
            AssetReference("verified-subject", AssetRole.VERIFIED_IDENTITY_REFERENCE, AssetTreatment.REFERENCE_ONLY),
        ))

    def story(self, event, **kwargs):
        data = dict(
            event=event,
            sport="football",
            subject="Arsenal",
            fact_phrase="خبر موثق",
            story_core="verified story core",
            tone=HeadlineTone.NEUTRAL,
            confidence=0.98,
        )
        data.update(kwargs)
        return VerifiedEditorialStory(**data)

    def execution_for(self, story):
        return self.orchestrator.decide(story).visual_execution

    def test_table_story_completes_without_generation_package_provider_or_gpu(self):
        decision = self.orchestrator.decide(self.story(EditorialEvent.TABLE))
        self.assertEqual(decision.visual_execution.route, PixelExecutionRoute.DETERMINISTIC_ONLY)
        plan = self.planner.compile(
            decision.visual_execution,
            self.layout,
            self.assets,
            headline=decision.headline,
            exact_data=("1 Arsenal 9 pts", "2 Chelsea 7 pts"),
        )
        self.assertEqual(plan.base_source, DirectBaseSource.PROGRAMMATIC_CANVAS)
        self.assertFalse(plan.metadata["generation_package_created"])
        self.assertFalse(plan.metadata["provider_selection_performed"])
        self.assertFalse(plan.metadata["gpu_job_required"])
        self.assertTrue(plan.metadata["generator_bypassed"])
        self.assertEqual(plan.exact_data, ("1 Arsenal 9 pts", "2 Chelsea 7 pts"))
        self.assertNotIn("verified-subject", plan.steps[0].asset_ids)

    def test_injury_uses_verified_asset_base_without_provider(self):
        decision = self.orchestrator.decide(self.story(EditorialEvent.INJURY))
        self.assertEqual(decision.visual_execution.route, PixelExecutionRoute.VERIFIED_ASSET_ONLY)
        plan = self.planner.compile(
            decision.visual_execution,
            self.layout,
            self.assets,
            headline=decision.headline,
        )
        self.assertEqual(plan.base_source, DirectBaseSource.VERIFIED_ASSET)
        self.assertEqual(plan.verified_base_asset_ids, ("verified-subject",))
        self.assertEqual(plan.steps[0].stage, DirectExecutionStage.PREPARE_BASE)
        self.assertEqual(plan.steps[0].asset_ids, ("verified-subject",))
        self.assertFalse(plan.metadata["provider_selection_performed"])

    def test_verified_asset_route_fails_closed_without_verified_source(self):
        decision = self.orchestrator.decide(self.story(EditorialEvent.STATEMENT))
        assets = AssetBundle(tuple(asset for asset in self.assets.assets if asset.role is not AssetRole.VERIFIED_IDENTITY_REFERENCE))
        with self.assertRaises(ValueError):
            self.planner.compile(decision.visual_execution, self.layout, assets, headline=decision.headline)

    def test_result_hybrid_route_cannot_enter_direct_execution(self):
        decision = self.orchestrator.decide(self.story(EditorialEvent.RESULT))
        self.assertTrue(decision.visual_execution.generator_required)
        with self.assertRaises(ValueError):
            self.planner.compile(decision.visual_execution, self.layout, self.assets, headline=decision.headline, score="2-1")

    def test_direct_execution_stage_order_is_complete_and_has_no_generation_stage(self):
        decision = self.orchestrator.decide(self.story(EditorialEvent.TACTICS))
        plan = self.planner.compile(
            decision.visual_execution,
            self.layout,
            self.assets,
            headline=decision.headline,
            exact_data=("4-3-3",),
        )
        self.assertEqual(
            [step.stage for step in plan.steps],
            [
                DirectExecutionStage.PREPARE_BASE,
                DirectExecutionStage.APPLY_EXACT_ASSETS,
                DirectExecutionStage.APPLY_EXACT_DATA_GEOMETRY,
                DirectExecutionStage.APPLY_EDITORIAL_TEXT,
                DirectExecutionStage.QUALITY_VERIFY,
                DirectExecutionStage.EXPORT,
            ],
        )
        self.assertTrue(all(step.stage.value != "generate_base_scene" for step in plan.steps))

    def test_score_requires_score_layout_box(self):
        no_score_layout = DeterministicLayoutPlanner().plan(self.profile)
        decision = self.orchestrator.decide(self.story(EditorialEvent.TABLE))
        with self.assertRaises(ValueError):
            self.planner.compile(decision.visual_execution, no_score_layout, self.assets, headline=decision.headline, score="2-1")


if __name__ == "__main__":
    unittest.main()
