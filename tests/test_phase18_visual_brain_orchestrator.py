import unittest

from engine.intelligence.visual_brain import VisualCriticEvidence
from engine.intelligence.visual_brain_orchestrator import VisualBrainOrchestrator


def evidence(concept_id: str, *, premium: bool) -> VisualCriticEvidence:
    if premium:
        return VisualCriticEvidence(
            concept_id=concept_id,
            editorial_specificity=.90,
            visual_impact=.92,
            composition_quality=.91,
            photographic_coherence=.94,
            concept_fidelity=.93,
            ordinary_stock_risk=.10,
        )
    return VisualCriticEvidence(
        concept_id=concept_id,
        geometry_violation=True,
        editorial_specificity=.40,
        visual_impact=.45,
        composition_quality=.55,
        photographic_coherence=.80,
        concept_fidelity=.50,
        ordinary_stock_risk=.80,
    )


class VisualBrainOrchestratorTests(unittest.TestCase):
    def test_rejected_first_attempt_is_retryable_but_never_publishable(self):
        brain = VisualBrainOrchestrator(max_attempts_per_concept=2)
        item = brain.critique(artifact="candidate.png", attempt=1, evidence=evidence("a", premium=False))
        self.assertTrue(brain.should_retry(item))
        selection = brain.select([item])
        self.assertIsNone(selection.winner)
        self.assertFalse(selection.publication_ready)
        self.assertEqual(selection.status, "VISUAL_BRAIN_NO_PUBLISHABLE_BASE_VISUAL")

    def test_retry_budget_is_bounded(self):
        brain = VisualBrainOrchestrator(max_attempts_per_concept=2)
        item = brain.critique(artifact="candidate.png", attempt=2, evidence=evidence("a", premium=False))
        self.assertFalse(brain.should_retry(item))

    def test_selection_uses_best_critic_score_not_first_success(self):
        brain = VisualBrainOrchestrator()
        first = brain.critique(artifact="first.png", attempt=1, evidence=VisualCriticEvidence(
            concept_id="first", editorial_specificity=.80, visual_impact=.80,
            composition_quality=.80, photographic_coherence=.82,
            concept_fidelity=.80, ordinary_stock_risk=.20))
        best = brain.critique(artifact="best.png", attempt=1, evidence=evidence("best", premium=True))
        selection = brain.select([first, best])
        self.assertEqual(selection.winner.concept_id, "best")
        self.assertFalse(selection.publication_ready)

    def test_hard_failure_cannot_win_even_with_other_high_scores(self):
        brain = VisualBrainOrchestrator()
        bad = VisualCriticEvidence(
            concept_id="bad", pseudo_text_detected=True,
            editorial_specificity=.99, visual_impact=.99, composition_quality=.99,
            photographic_coherence=.99, concept_fidelity=.99, ordinary_stock_risk=.01)
        rejected = brain.critique(artifact="bad.png", attempt=1, evidence=bad)
        good = brain.critique(artifact="good.png", attempt=1, evidence=evidence("good", premium=True))
        self.assertEqual(brain.select([rejected, good]).winner.concept_id, "good")


if __name__ == "__main__":
    unittest.main()
