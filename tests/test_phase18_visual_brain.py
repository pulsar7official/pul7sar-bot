import unittest

from engine.intelligence.visual_brain import (
    VisualConceptCompetition,
    VisualCriticEvidence,
    VisualCriticGate,
)


class VisualBrainTests(unittest.TestCase):
    def test_preview_competition_is_concept_diverse_not_seed_diverse(self):
        concepts = VisualConceptCompetition().preview_season_return()
        self.assertGreaterEqual(len(concepts), 4)
        self.assertEqual(len({item.concept_id for item in concepts}), len(concepts))
        self.assertEqual(len({item.focal_strategy for item in concepts}), len(concepts))
        for concept in concepts:
            prompt = concept.scene_prompt.casefold()
            self.assertNotIn("pul7sar", prompt)
            self.assertNotIn("pulsar", prompt)
            self.assertIn("generic", prompt)
            self.assertTrue(any("playing surface" in item for item in concept.forbidden_elements))
            self.assertTrue(any("pseudo-text" in item for item in concept.forbidden_elements))

    def test_preview_does_not_lock_tunnel_as_template(self):
        concepts = VisualConceptCompetition().preview_season_return()
        self.assertTrue(all("illuminated_tunnel_lower_left" not in item.focal_strategy for item in concepts))
        self.assertTrue(all("tunnel" not in item.title.casefold() for item in concepts))

    def test_critic_rejects_previous_candidate_failure_pattern(self):
        evidence = VisualCriticEvidence(
            concept_id="legacy-candidate-1",
            geometry_violation=True,
            pseudo_text_detected=True,
            editorial_specificity=0.35,
            visual_impact=0.42,
            composition_quality=0.55,
            photographic_coherence=0.80,
            concept_fidelity=0.50,
            ordinary_stock_risk=0.82,
        )
        decision = VisualCriticGate().evaluate(evidence)
        self.assertFalse(decision.accepted)
        self.assertEqual(decision.score, 0.0)
        self.assertIn("sport geometry violation", decision.failures)
        self.assertIn("generated pseudo-text/readable text", decision.failures)
        self.assertIn("technically correct but visually ordinary/stock-like", decision.failures)

    def test_critic_accepts_only_premium_safe_candidate(self):
        evidence = VisualCriticEvidence(
            concept_id="premium",
            editorial_specificity=0.88,
            visual_impact=0.91,
            composition_quality=0.90,
            photographic_coherence=0.94,
            concept_fidelity=0.92,
            ordinary_stock_risk=0.12,
        )
        decision = VisualCriticGate().evaluate(evidence)
        self.assertTrue(decision.accepted)
        self.assertGreater(decision.score, 0.85)
        self.assertEqual(decision.failures, ())


if __name__ == "__main__":
    unittest.main()
