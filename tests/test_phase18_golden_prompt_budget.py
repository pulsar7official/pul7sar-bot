import unittest

from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.golden_prompt_budget import (
    GOLDEN_BENCHMARK_ID,
    GOLDEN_PROMPT_BUDGET_CONTRACT,
    GOLDEN_SCENE_PROMPT_BUDGET_CHARS,
    GoldenPromptBudget,
)
from tools.phase18_build_golden_handoff import build_request


class GoldenPromptBudgetTests(unittest.TestCase):
    @staticmethod
    def _package() -> GenerationPackage:
        return GenerationPackage(
            platform="instagram_feed",
            canvas="1080x1350",
            scene_prompt="Very long repeated scene direction. " * 100,
            negative_constraints=(
                "no generated branding, wordmarks, readable text, numerals or pseudo-text",
                "no football pitch markings in the reserved surface context",
                "no specific identifiable real venue",
            ),
            asset_ids=(),
            factual_constraints=(
                "the season is approaching rather than already decided",
                "exact football geometry is applied deterministically later",
            ),
            metadata={
                "generated_branding_allowed": False,
                "hybrid_base_scene_contract": True,
                "reserved_base_scene_content": ("playing-surface geometry", "brand", "typography"),
                "visual_concept_selected_before_renderer": True,
            },
        )

    def test_compaction_preserves_exact_policy_and_fact_constraints(self):
        source = self._package()
        compact = GoldenPromptBudget().compact(source, benchmark_id=GOLDEN_BENCHMARK_ID)
        self.assertEqual(compact.negative_constraints, source.negative_constraints)
        self.assertEqual(compact.factual_constraints, source.factual_constraints)
        self.assertEqual(compact.asset_ids, source.asset_ids)
        self.assertLessEqual(len(compact.scene_prompt), GOLDEN_SCENE_PROMPT_BUDGET_CHARS)
        self.assertEqual(compact.metadata["benchmark"], GOLDEN_BENCHMARK_ID)
        self.assertEqual(compact.metadata["golden_prompt_contract"], GOLDEN_PROMPT_BUDGET_CONTRACT)
        self.assertTrue(compact.metadata["golden_prompt_compacted"])
        self.assertTrue(compact.metadata["golden_prompt_policy_boundaries_preserved"])

    def test_compaction_is_locked_to_current_golden_benchmark(self):
        with self.assertRaisesRegex(ValueError, "current Golden Hybrid v5"):
            GoldenPromptBudget().compact(self._package(), benchmark_id="another-benchmark")

    def test_compaction_refuses_relaxed_geometry_or_brand_ownership(self):
        package = self._package()

        brand_metadata = dict(package.metadata)
        brand_metadata["generated_branding_allowed"] = True
        relaxed_brand = GenerationPackage(
            platform=package.platform,
            canvas=package.canvas,
            scene_prompt=package.scene_prompt,
            negative_constraints=package.negative_constraints,
            asset_ids=package.asset_ids,
            factual_constraints=package.factual_constraints,
            metadata=brand_metadata,
        )
        with self.assertRaises(ValueError):
            GoldenPromptBudget().compact(relaxed_brand, benchmark_id=GOLDEN_BENCHMARK_ID)

        geometry_metadata = dict(package.metadata)
        geometry_metadata["reserved_base_scene_content"] = ("brand", "typography")
        relaxed_geometry = GenerationPackage(
            platform=package.platform,
            canvas=package.canvas,
            scene_prompt=package.scene_prompt,
            negative_constraints=package.negative_constraints,
            asset_ids=package.asset_ids,
            factual_constraints=package.factual_constraints,
            metadata=geometry_metadata,
        )
        with self.assertRaises(ValueError):
            GoldenPromptBudget().compact(relaxed_geometry, benchmark_id=GOLDEN_BENCHMARK_ID)

    def test_actual_golden_handoff_is_compact_but_keeps_provider_policy(self):
        request = build_request(seed=7007001, request_id="golden-prompt-budget-test")
        self.assertEqual(request.metadata["golden_prompt_contract"], GOLDEN_PROMPT_BUDGET_CONTRACT)
        self.assertTrue(request.metadata["golden_prompt_compacted"])
        self.assertTrue(request.metadata["golden_prompt_policy_boundaries_preserved"])
        self.assertLessEqual(
            request.metadata["golden_scene_prompt_chars"],
            request.metadata["golden_scene_prompt_budget_chars"],
        )
        # Previous Golden v5 CPU artifact compiled to 8,352 prompt characters.
        # Keep a meaningful deterministic ceiling while leaving room for all
        # provider-positive reframes and factual constraints.
        self.assertLessEqual(len(request.prompt), 6500)
        self.assertIn("Verified factual constraints:", request.prompt)
        self.assertIn("Mandatory visual treatment:", request.prompt)
        self.assertFalse(request.metadata["generated_branding_allowed"])
        self.assertFalse(request.metadata["generated_sport_geometry_allowed"])
        lowered = request.prompt.casefold()
        required_v5_markers = (
            "one single continuous full-bleed editorial image",
            "story-specific non-identifying sports atmosphere",
            "must not imply a specific real venue",
            "never use collage, montage, split-screen, grid, diptych, triptych",
            "reserved surface region plain and unmarked",
            "no field/court/rink lines",
            "the exact surface will be replaced by deterministic code after generation",
            "fully unbranded",
            "platform names",
        )
        for marker in required_v5_markers:
            with self.subTest(marker=marker):
                self.assertIn(marker, lowered)
        self.assertNotIn("pul7sar", lowered)
        self.assertNotIn("pulsar", lowered)


if __name__ == "__main__":
    unittest.main()
