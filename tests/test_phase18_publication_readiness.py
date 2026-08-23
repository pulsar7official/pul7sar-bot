import unittest

from engine.intelligence.final_export import ExportAuthorization
from engine.intelligence.hybrid_visual_inspection_policy import HybridVisualInspectionDecision
from engine.intelligence.hybrid_visual_quality_gate import HybridVisualQualityDecision
from engine.intelligence.publication_readiness import PublicationReadinessEvidence, PublicationReadinessGate
from engine.intelligence.visual_failure_scenarios import FailureScenarioReport
from engine.intelligence.visual_premortem_gate import PremortemAction, VisualPremortemDecision


class PublicationReadinessGateTests(unittest.TestCase):
    def setUp(self):
        self.gate = PublicationReadinessGate()

    def good(self):
        return PublicationReadinessEvidence(
            premortem=VisualPremortemDecision(PremortemAction.PROCEED, True, True, FailureScenarioReport(()), (), ()),
            inspection=HybridVisualInspectionDecision("AUTO_VISUAL_QA_READY", True, True, True, ()),
            hybrid_quality=HybridVisualQualityDecision(True, ()),
            semantic_publication_approved=True,
            golden_visual_approved=True,
            export_authorization=ExportAuthorization(True, (), "export:test"),
        )

    def test_every_independent_gate_must_pass(self):
        decision = self.gate.evaluate(self.good())
        self.assertTrue(decision.ready)
        self.assertEqual(decision.status, "PUBLICATION_READY")

    def test_png_or_hybrid_quality_alone_is_not_enough(self):
        evidence = self.good()
        evidence = PublicationReadinessEvidence(
            premortem=evidence.premortem,
            inspection=HybridVisualInspectionDecision(
                "VISUAL_QA_CAPABILITY_INCOMPLETE", True, False, False, ("forbidden_visual_detection",)
            ),
            hybrid_quality=evidence.hybrid_quality,
            semantic_publication_approved=True,
            golden_visual_approved=True,
            export_authorization=evidence.export_authorization,
        )
        decision = self.gate.evaluate(evidence)
        self.assertFalse(decision.ready)
        self.assertIn("inspection_missing:forbidden_visual_detection", decision.blockers)

    def test_golden_quality_failure_blocks_even_if_semantics_pass(self):
        evidence = self.good()
        evidence = PublicationReadinessEvidence(
            premortem=evidence.premortem,
            inspection=evidence.inspection,
            hybrid_quality=evidence.hybrid_quality,
            semantic_publication_approved=True,
            golden_visual_approved=False,
            export_authorization=evidence.export_authorization,
        )
        decision = self.gate.evaluate(evidence)
        self.assertIn("golden_visual_quality_not_approved", decision.blockers)

    def test_export_failure_is_preserved(self):
        evidence = self.good()
        evidence = PublicationReadinessEvidence(
            premortem=evidence.premortem,
            inspection=evidence.inspection,
            hybrid_quality=evidence.hybrid_quality,
            semantic_publication_approved=True,
            golden_visual_approved=True,
            export_authorization=ExportAuthorization(False, ("missing rendered text roles",)),
        )
        decision = self.gate.evaluate(evidence)
        self.assertIn("export:missing rendered text roles", decision.blockers)


if __name__ == "__main__":
    unittest.main()
