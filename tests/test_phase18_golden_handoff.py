import unittest

from tools.phase18_build_golden_handoff import build_request


class GoldenVisualHandoffTests(unittest.TestCase):
    def test_golden_request_uses_real_phase18_layout_and_zero_cost_model(self):
        request = build_request(seed=7007001, request_id="golden-test")
        self.assertEqual(request.provider_id, "local-flux2-klein-4b")
        self.assertEqual(request.model_id, "black-forest-labs/FLUX.2-klein-4B")
        self.assertEqual(request.backend, "diffusers")
        self.assertEqual(request.metadata["cost_mode"], "$0-local")
        self.assertTrue(request.metadata["portable_handoff"])
        self.assertEqual(request.seed, 7007001)
        prompt = request.prompt.casefold()
        self.assertIn("european football", prompt)
        self.assertIn("season-opening", prompt)
        self.assertIn("do not render platform branding", prompt)
        self.assertIn("approaching rather than already decided", prompt)
        self.assertIn("use at most a restrained partial sport-surface context", prompt)
        self.assertIn("do not make a full pitch the visual subject", prompt)
        self.assertIn("story-specific visual concept archetype: generative_event_atmosphere", prompt)
        self.assertIn("story-specific non-identifying sports atmosphere", prompt)
        self.assertIn("specific real venue identity without verified reference", prompt)
        self.assertTrue(request.metadata["brand_name_redacted_from_generation_prompt"])
        self.assertFalse(request.metadata["generated_sport_geometry_allowed"])
        self.assertTrue(request.metadata["hybrid_surface_replacement_required"])
        self.assertEqual(request.metadata["visual_grammar_contract"], "pul7sar-visual-grammar-v1")
        self.assertTrue(request.metadata["visual_grammar_provider_agnostic"])
        self.assertEqual(request.metadata["visual_grammar_surface_visibility"], "partial_deterministic")
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
        self.assertIn("deliberately non-identifying", prompt)
        self.assertIn("must not imply a specific real venue", prompt)
        self.assertIn("specific real-person depiction", prompt)
        self.assertIn("generic architecture and no distinctive landmark", prompt)
        self.assertIn("free of identifiable real people or celebrity likenesses", prompt)

    def test_golden_request_is_deterministic_for_same_seed(self):
        first = build_request(seed=42, request_id="same")
        second = build_request(seed=42, request_id="same")
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
