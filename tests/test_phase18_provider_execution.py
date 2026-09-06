import unittest

from engine.intelligence.assets import AssetBundle, AssetReference, AssetRole, AssetTreatment
from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.provider_capabilities import ProviderEligibilityDecision, ProviderFeature
from engine.intelligence.provider_execution import ExecutionStage, ProviderExecutionPlanner
from engine.intelligence.provider_selection import ProviderSelection
from engine.intelligence.visual_execution_route import PixelExecutionRoute, VisualExecutionDecision


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
        self.execution_route = self._route(
            PixelExecutionRoute.HYBRID_GENERATIVE,
            generator_required=True,
            provider_selection_allowed=True,
            generated_elements=("atmosphere", "lighting", "depth"),
        )

    @staticmethod
    def _route(route, *, generator_required, provider_selection_allowed, generated_elements=()):
        return VisualExecutionDecision(
            route=route,
            generator_required=generator_required,
            provider_selection_allowed=provider_selection_allowed,
            generated_elements=generated_elements,
            deterministic_elements=("PUL7SAR brand", "headline typography"),
            reason="test route",
            metadata={"contract": "pul7sar-visual-execution-route-v1"},
        )

    def compile(self, selection=None, execution_route=None):
        return self.planner.compile(
            self.package,
            self.assets,
            selection or self.selection,
            aspect_ratio="9:16",
            execution_route=execution_route or self.execution_route,
        )

    def test_exact_official_assets_are_post_composited_not_generated(self):
        plan = self.compile()
        self.assertIn("pul7sar-logo", plan.post_composite_asset_ids)
        self.assertIn("pul7sar-pulse", plan.post_composite_asset_ids)
        self.assertIn("arsenal-crest", plan.post_composite_asset_ids)
        self.assertIn("instagram-icon", plan.post_composite_asset_ids)
        self.assertNotIn("pul7sar-logo", plan.generated_reference_asset_ids)

    def test_verified_identity_reference_goes_to_provider_generation_stage(self):
        plan = self.compile()
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
        plan = self.compile()
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

    def test_generation_step_is_bound_to_declared_generator_owned_elements(self):
        plan = self.compile()
        generation = plan.steps[0]
        self.assertEqual(generation.stage, ExecutionStage.GENERATE_BASE_SCENE)
        self.assertEqual(generation.metadata["visual_execution_route"], "hybrid_generative")
        self.assertEqual(generation.metadata["generator_owned_elements"], ("atmosphere", "lighting", "depth"))
        self.assertEqual(generation.metadata["visual_execution_contract"], "pul7sar-visual-execution-route-v1")
        self.assertIn("atmosphere, lighting, depth", generation.instructions[0])

    def test_no_eligible_provider_blocks_execution_plan(self):
        with self.assertRaises(ValueError):
            self.compile(ProviderSelection(None, (ProviderEligibilityDecision("weak", False),)))

    def test_deterministic_route_cannot_compile_provider_plan_even_if_provider_exists(self):
        route = self._route(
            PixelExecutionRoute.DETERMINISTIC_ONLY,
            generator_required=False,
            provider_selection_allowed=False,
        )
        with self.assertRaisesRegex(ValueError, "provider execution is forbidden"):
            self.compile(execution_route=route)

    def test_verified_asset_route_cannot_compile_provider_plan_even_if_provider_exists(self):
        route = self._route(
            PixelExecutionRoute.VERIFIED_ASSET_ONLY,
            generator_required=False,
            provider_selection_allowed=False,
        )
        with self.assertRaisesRegex(ValueError, "provider execution is forbidden"):
            self.compile(execution_route=route)

    def test_provider_route_requires_explicit_generator_owned_elements(self):
        route = self._route(
            PixelExecutionRoute.HYBRID_GENERATIVE,
            generator_required=True,
            provider_selection_allowed=True,
            generated_elements=(),
        )
        with self.assertRaisesRegex(ValueError, "generator-owned elements"):
            self.compile(execution_route=route)

    def test_execution_route_type_is_required(self):
        with self.assertRaises(TypeError):
            self.planner.compile(
                self.package,
                self.assets,
                self.selection,
                aspect_ratio="9:16",
                execution_route=object(),
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
