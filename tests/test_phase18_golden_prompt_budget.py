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
                "no full football pitch as the main visual subject",
                "no specific identifiable real venue",
            ),
            asset_ids=(),
            factual_constraints=(
                "the season is approaching rather than already decided",
                "playing-surface geometry is not a story dependency for this preview",
            ),
            metadata={
                "generated_branding_allowed": False,
                "generated_sport_geometry_allowed": False,
                "sport_geometry": "contextual_optional_not_required",
                "hybrid_surface_replacement_required": False,
                "hybrid_base_scene_contract": True,
                "reserved_base_scene_content": ("brand", "typography"),
                "visual_grammar_surface_visibility": "context_only",
                "visual_concept_selected_before_renderer": True,
            },
        )

    def test_compaction_preserves_policy_and_fact_constraints(self):
        source = self._package()
        compact = GoldenPromptBudget().compact(source, benchmark_id=GOLDEN_BENCHMARK_ID)
        self.assertEqual(compact.negative_constraints, source.negative_constraints)
        self.assertEqual(compact.factual_constraints, source.factual_constraints)
        self.assertEqual(compact.asset_ids, source.asset_ids)
        self.assertLessEqual(len(compact.scene_prompt), GOLDEN_SCENE_PROMPT_BUDGET_CHARS)
        self.assertEqual(compact.metadata["benchmark"], GOLDEN_BENCHMARK_ID)
        self.assertEqual(compact.metadata["golden_prompt_contract"], GOLDEN_PROMPT_BUDGET_CONTRACT)
        self.assertFalse(compact.metadata["generated_sport_geometry_allowed"])
        self.assertFalse(compact.metadata["partial_sport_geometry_allowed"])
        self.assertEqual(compact.metadata["sport_geometry_integrity_policy"], "exact_verified_or_visually_indeterminate")
        self.assertTrue(compact.metadata["partial_sport_geometry_hallucination_is_hard_failure"])
        self.assertTrue(compact.metadata["golden_prompt_compacted"])
        self.assertTrue(compact.metadata["golden_prompt_policy_boundaries_preserved"])

    def test_compaction_is_locked_to_current_golden_benchmark(self):
        with self.assertRaisesRegex(ValueError, "current Golden editorial v6"):
            GoldenPromptBudget().compact(self._package(), benchmark_id="another-benchmark")

    def test_compaction_refuses_relaxed_brand_or_surface_ownership(self):
        package = self._package()
        brand_metadata = dict(package.metadata)
        brand_metadata["generated_branding_allowed"] = True
        relaxed_brand = GenerationPackage(platform=package.platform, canvas=package.canvas, scene_prompt=package.scene_prompt, negative_constraints=package.negative_constraints, asset_ids=package.asset_ids, factual_constraints=package.factual_constraints, metadata=brand_metadata)
        with self.assertRaises(ValueError):
            GoldenPromptBudget().compact(relaxed_brand, benchmark_id=GOLDEN_BENCHMARK_ID)
        geometry_metadata = dict(package.metadata)
        geometry_metadata["sport_geometry"] = "deterministic_football_pitch_projective_v1"
        pitch_first_geometry = GenerationPackage(platform=package.platform, canvas=package.canvas, scene_prompt=package.scene_prompt, negative_constraints=package.negative_constraints, asset_ids=package.asset_ids, factual_constraints=package.factual_constraints, metadata=geometry_metadata)
        with self.assertRaises(ValueError):
            GoldenPromptBudget().compact(pitch_first_geometry, benchmark_id=GOLDEN_BENCHMARK_ID)
        replacement_metadata = dict(package.metadata)
        replacement_metadata["hybrid_surface_replacement_required"] = True
        pitch_first = GenerationPackage(platform=package.platform, canvas=package.canvas, scene_prompt=package.scene_prompt, negative_constraints=package.negative_constraints, asset_ids=package.asset_ids, factual_constraints=package.factual_constraints, metadata=replacement_metadata)
        with self.assertRaises(ValueError):
            GoldenPromptBudget().compact(pitch_first, benchmark_id=GOLDEN_BENCHMARK_ID)

    def test_actual_golden_handoff_is_compact_and_story_first(self):
        request = build_request(seed=7007001, request_id="golden-prompt-budget-test")
        self.assertEqual(request.metadata["golden_prompt_contract"], GOLDEN_PROMPT_BUDGET_CONTRACT)
        self.assertTrue(request.metadata["golden_prompt_compacted"])
        self.assertTrue(request.metadata["golden_prompt_policy_boundaries_preserved"])
        self.assertLessEqual(request.metadata["golden_scene_prompt_chars"], request.metadata["golden_scene_prompt_budget_chars"])
        self.assertLessEqual(len(request.prompt), 7000)
        self.assertIn("Verified factual constraints:", request.prompt)
        self.assertIn("Mandatory visual treatment:", request.prompt)
        self.assertFalse(request.metadata["generated_branding_allowed"])
        self.assertFalse(request.metadata["generated_sport_geometry_allowed"])
        self.assertFalse(request.metadata["partial_sport_geometry_allowed"])
        self.assertTrue(request.metadata["partial_sport_geometry_hallucination_is_hard_failure"])
        self.assertFalse(request.metadata["hybrid_surface_replacement_required"])
        self.assertEqual(request.metadata["visual_grammar_surface_visibility"], "context_only")
        self.assertEqual(request.metadata["sport_geometry"], "contextual_optional_not_required")
        lowered = request.prompt.casefold()
        required_v6_markers = (
            "one single continuous full-bleed editorial image",
            "premium european football season-opening anticipation",
            "deliberately non-identifying generic stadium",
            "asymmetric editorial hierarchy",
            "oblique three-quarter environmental camera",
            "no high-wide-central broadcast framing",
            "no full-pitch master shot",
            "turf is optional context only and visually subordinate",
            "show no goal frame or goal net",
            "no penalty-area or goal-area lines",
            "no corner arc or corner flag",
            "no centre circle or halfway line",
            "never invent isolated football geometry",
            "keep it outside the frame, fully occluded, or visually indeterminate",
            "do not fabricate exact pitch markings",
            "fully unbranded",
            "platform names",
            "never use collage, montage, split-screen, grid, diptych, triptych",
        )
        for marker in required_v6_markers:
            with self.subTest(marker=marker):
                self.assertIn(marker, lowered)
        self.assertNotIn("the exact surface will be replaced by deterministic code after generation", lowered)
        self.assertNotIn("pul7sar", lowered)
        self.assertNotIn("pulsar", lowered)


if __name__ == "__main__":
    unittest.main()
