import unittest

from engine.intelligence.visual_quality_ladder import (
    VisualMaturity,
    VisualQualityEvidence,
    VisualQualityLadder,
)


class VisualQualityLadderTests(unittest.TestCase):
    def evidence(self, **kwargs):
        data = dict(
            coherent_story_world=True,
            story_specific_hero=True,
            materially_rich_scene=True,
            natural_depth_and_lighting=True,
            family_distinct_composition=True,
            exact_identity_safe=True,
            exact_facts_safe=True,
            no_placeholder_artifacts=True,
            no_generic_template_feel=True,
            no_procedural_demo_feel=True,
            brand_master_exact=True,
            human_visual_review_passed=False,
        )
        data.update(kwargs)
        return VisualQualityEvidence(**data)

    def test_procedural_demo_cannot_be_called_premium(self):
        d = VisualQualityLadder().evaluate(self.evidence(no_procedural_demo_feel=False))
        self.assertEqual(d.maturity, VisualMaturity.ART_DIRECTION_STUDY)
        self.assertFalse(d.publication_allowed)

    def test_generic_template_cannot_be_called_premium(self):
        d = VisualQualityLadder().evaluate(self.evidence(no_generic_template_feel=False))
        self.assertEqual(d.maturity, VisualMaturity.ART_DIRECTION_STUDY)
        self.assertFalse(d.publication_allowed)

    def test_placeholder_is_hard_safety_failure(self):
        d = VisualQualityLadder().evaluate(self.evidence(no_placeholder_artifacts=False))
        self.assertEqual(d.maturity, VisualMaturity.TECHNICAL_PROOF)
        self.assertFalse(d.publication_allowed)

    def test_visual_candidate_still_requires_human_review(self):
        d = VisualQualityLadder().evaluate(self.evidence())
        self.assertEqual(d.maturity, VisualMaturity.PREMIUM_CANDIDATE)
        self.assertFalse(d.publication_allowed)

    def test_only_reviewed_premium_candidate_becomes_publication_master(self):
        d = VisualQualityLadder().evaluate(self.evidence(human_visual_review_passed=True))
        self.assertEqual(d.maturity, VisualMaturity.PUBLICATION_MASTER)
        self.assertTrue(d.publication_allowed)
        self.assertEqual(d.blockers, ())


if __name__ == "__main__":
    unittest.main()
