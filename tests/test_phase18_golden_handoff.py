import unittest

from tools.phase18_build_golden_handoff import build_request


class GoldenVisualHandoffTests(unittest.TestCase):
    def test_golden_request_uses_story_first_v6_and_zero_cost_model(self):
        request = build_request(seed=7007001, request_id="golden-test")
        self.assertEqual(request.provider_id, "local-flux2-klein-4b")
        self.assertEqual(request.model_id, "black-forest-labs/FLUX.2-klein-4B")
        self.assertEqual(request.backend, "diffusers")
        self.assertEqual(request.metadata["cost_mode"], "$0-local")
        self.assertTrue(request.metadata["portable_handoff"])
        self.assertEqual(request.seed, 7007001)
        prompt = request.prompt.casefold()
        self.assertIn("european football", prompt)
        self.assertIn("season-opening anticipation", prompt)
        self.assertIn("approaching rather than already decided", prompt)
        self.assertIn("asymmetric editorial hierarchy", prompt)
        self.assertIn("oblique three-quarter environmental camera", prompt)
        self.assertIn("no high-wide-central broadcast framing", prompt)
        self.assertIn("no full-pitch master shot", prompt)
        self.assertIn("turf is optional context only and visually subordinate", prompt)
        self.assertIn("do not fabricate exact pitch markings", prompt)
        self.assertNotIn("reserved surface region plain and unmarked", prompt)
        self.assertNotIn("exact surface will be replaced by deterministic code", prompt)
        self.assertTrue(request.metadata["brand_name_redacted_from_generation_prompt"])
        self.assertFalse(request.metadata["generated_sport_geometry_allowed"])
        self.assertFalse(request.metadata["hybrid_surface_replacement_required"])
        self.assertEqual(request.metadata["sport_geometry"], "contextual_optional_not_required")
        self.assertEqual(request.metadata["football_camera_preset"], "editorial_environmental_oblique")
        self.assertEqual(request.metadata["visual_priority"], "story_focal_hierarchy_before_sport_surface")
        self.assertEqual(request.metadata["visual_grammar_contract"], "pul7sar-visual-grammar-v1")
        self.assertTrue(request.metadata["visual_grammar_provider_agnostic"])
        self.assertEqual(request.metadata["visual_grammar_surface_visibility"], "context_only")
        self.assertEqual(request.metadata["visual_grammar_fantasy_level"], "restrained")
        self.assertEqual(request.metadata["visual_concept_contract"], "pul7sar-visual-concept-director-v2-original-first")
        self.assertTrue(request.metadata["visual_concept_provider_agnostic"])
        self.assertTrue(request.metadata["visual_concept_selected_before_renderer"])
        self.assertEqual(request.metadata["visual_concept_archetype"], "generative_event_atmosphere")
        self.assertFalse(request.metadata["visual_concept_publication_ready"])
        self.assertNotIn("pul7sar", prompt)
        self.assertNotIn("pulsar", prompt)

    def test_golden_request_does_not_claim_specific_real_venue_or_person(self):
        request = build_request(seed=7007001, request_id="golden-safe-context")
        prompt = request.prompt.casefold()
        self.assertIn("deliberately non-identifying generic stadium", prompt)
        self.assertIn("do not imply a specific real venue, club, match or person", prompt)
        self.assertIn("no specific identifiable real venue", prompt)
        self.assertIn("no specific real-person depiction", prompt)

    def test_golden_request_is_deterministic_for_same_seed(self):
        first = build_request(seed=42, request_id="same")
        second = build_request(seed=42, request_id="same")
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
