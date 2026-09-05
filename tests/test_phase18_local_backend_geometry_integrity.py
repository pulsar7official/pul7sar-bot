import unittest

from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.local_backend_execution import LocalBackendRequestCompiler
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


class LocalBackendGeometryIntegrityTests(unittest.TestCase):
    def test_exact_or_indeterminate_policy_survives_portable_handoff(self):
        package = GenerationPackage(
            platform="instagram_feed",
            canvas="1080x1350",
            scene_prompt="generic football atmosphere with context-only turf",
            negative_constraints=("no isolated or partial goal frame or goal net",),
            asset_ids=(),
            factual_constraints=("playing-surface geometry is not a story dependency",),
            metadata={
                "hybrid_base_scene_contract": True,
                "visual_grammar_surface_visibility": "context_only",
                "generated_sport_geometry_allowed": False,
                "partial_sport_geometry_allowed": False,
                "sport_geometry_integrity_policy": "exact_verified_or_visually_indeterminate",
                "partial_sport_geometry_hallucination_is_hard_failure": True,
            },
        )
        request = LocalBackendRequestCompiler().compile_portable_handoff(
            package=package,
            model=FLUX2_KLEIN_4B_LOCAL,
            backend="diffusers",
            seed=7007001,
            request_id="geometry-integrity-handoff",
        )
        self.assertFalse(request.metadata["generated_sport_geometry_allowed"])
        self.assertFalse(request.metadata["partial_sport_geometry_allowed"])
        self.assertEqual(request.metadata["sport_geometry_integrity_policy"], "exact_verified_or_visually_indeterminate")
        self.assertTrue(request.metadata["partial_sport_geometry_hallucination_is_hard_failure"])
        self.assertFalse(request.metadata["hybrid_surface_replacement_required"])
        prompt = request.prompt.casefold()
        self.assertIn("outside the frame", prompt)
        self.assertIn("goal frames or nets", prompt)
        self.assertIn("physically coherent and story-authorized", prompt)


if __name__ == "__main__":
    unittest.main()
