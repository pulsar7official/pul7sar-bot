import unittest

from engine.intelligence.assets import AssetBundle, AssetReference, AssetRole, AssetTreatment
from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.provider_capabilities import ProviderEligibilityDecision, ProviderFeature
from engine.intelligence.provider_execution import ExecutionStage, ProviderExecutionPlanner
from engine.intelligence.provider_selection import ProviderSelection


class ProviderExecutionPlannerTests(unittest.TestCase):
    def setUp(self):
        self.planner = ProviderExecutionPlanner()
        self.package = GenerationPackage(
            platform="instagram_story",
            canvas="1080x1920",
            scene_prompt="approved scene",
            negative_constraints=("no humiliation", "no fake signing"),
            asset_ids=("pul7sar-logo", "pul7sar-pulse", "arsenal-crest", "sam-hickey-ref"),
            factual_constraints=("verified fact",),
            layout_boxes={"hero": {"x": 100, "y": 200, "width": 700, "height": 900}},
            accent_hex="#EF0107",
        )
        self.assets = AssetBundle((
            AssetReference("pul7sar-logo", AssetRole.PUL7SAR_LOGO, AssetTreatment.EXACT),
            AssetReference("pul7sar-pulse", AssetRole.PUL7SAR_PULSE, AssetTreatment.TINTABLE_ACCENT),
            AssetReference("arsenal-crest", AssetRole.TEAM_CREST, AssetTreatment.EXACT),
            AssetReference("instagram-icon", AssetRole.SOCIAL_ICON, AssetTreatment.EXACT, metadata={"platform": "instagram"}),
            AssetReference("sam-hickey-ref", AssetRole.VERIFIED_IDENTITY_REFERENCE, AssetTreatment.REFERENCE_ONLY),
        ))
        self.selection = ProviderSelection(
            "eligible-provider",
            (ProviderEligibilityDecision("eligible-provider", True),),
        )

    def test_exact_official_assets_are_post_composited_not_generated(self):
        plan = self.planner.compile(self.package, self.assets, self.selection, aspect_ratio="9:16")
        self.assertIn("pul7sar-logo", plan.post_composite_asset_ids)
        self.assertIn("pul7sar-pulse", plan.post_composite_asset_ids)
        self.assertIn("arsenal-crest", plan.post_composite_asset_ids)
        self.assertIn("instagram-icon", plan.post_composite_asset_ids)
        self.assertNotIn("pul7sar-logo", plan.generated_reference_asset_ids)

    def test_verified_identity_reference_goes_to_provider_generation_stage(self):
        plan = self.planner.compile(self.package, self.assets, self.selection, aspect_ratio="9:16")
        self.assertEqual(plan.generated_reference_asset_ids, ("sam-hickey-ref",))
        self.assertIn(ProviderFeature.REFERENCE_IMAGE, plan.provider_requirements.required_features)

    def test_exact_asset_compositing_is_not_required_from_image_provider(self):
        requirements = self.planner.build_requirements(self.package, self.assets, aspect_ratio="9:16")
        self.assertNotIn(ProviderFeature.EXACT_ASSET_COMPOSITING, requirements.required_features)
        self.assertNotIn(ProviderFeature.TRANSPARENT_PNG_INPUT, requirements.required_features)

    def test_negative_constraints_require_provider_negative_instruction_support(self):
        requirements = self.planner.build_requirements(self.package, self.assets, aspect_ratio="9:16")
        self.assertIn(ProviderFeature.NEGATIVE_INSTRUCTIONS, requirements.required_features)

    def test_execution_stages_are_strictly_ordered(self):
        plan = self.planner.compile(self.package, self.assets, self.selection, aspect_ratio="9:16")
        self.assertEqual(
            [step.stage for step in plan.steps],
            [
                ExecutionStage.GENERATE_BASE_SCENE,
                ExecutionStage.APPLY_EXACT_ASSETS,
                ExecutionStage.APPLY_EDITORIAL_TEXT,
                ExecutionStage.QUALITY_VERIFY,
                ExecutionStage.EXPORT,
            ],
        )

    def test_no_eligible_provider_blocks_execution_plan(self):
        with self.assertRaises(ValueError):
            self.planner.compile(
                self.package,
                self.assets,
                ProviderSelection(None, (ProviderEligibilityDecision("weak", False),)),
                aspect_ratio="9:16",
            )

    def test_multiple_identity_references_require_multiple_reference_support(self):
        assets = AssetBundle(self.assets.assets + (
            AssetReference("second-ref", AssetRole.VERIFIED_IDENTITY_REFERENCE, AssetTreatment.REFERENCE_ONLY),
        ))
        requirements = self.planner.build_requirements(self.package, assets, aspect_ratio="9:16")
        self.assertIn(ProviderFeature.MULTIPLE_REFERENCES, requirements.required_features)
        self.assertEqual(requirements.reference_image_count, 2)


if __name__ == "__main__":
    unittest.main()
