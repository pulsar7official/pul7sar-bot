import unittest

from engine.intelligence.direct_publication import DirectPublicationReadinessEvidence, DirectPublicationReadinessGate, DirectSemanticPublicationGate
from engine.intelligence.direct_visual_execution import DirectBaseSource, DirectVisualExecutionPlan
from engine.intelligence.direct_visual_quality import DirectRenderQualityDecision
from engine.intelligence.final_export import ExportAuthorization
from engine.intelligence.verified_subject_compositor import VerifiedSubjectCompositionReceipt
from engine.intelligence.visual_execution_route import PixelExecutionRoute
from engine.intelligence.vision_verification_policy import VisionVerificationCapability, VisionVerifierProfile


class DirectPublicationGateTests(unittest.TestCase):
    def plan(self, *, verified_asset=False):
        return DirectVisualExecutionPlan(
            route=(PixelExecutionRoute.VERIFIED_ASSET_ONLY if verified_asset else PixelExecutionRoute.DETERMINISTIC_ONLY),
            base_source=(DirectBaseSource.VERIFIED_ASSET if verified_asset else DirectBaseSource.PROGRAMMATIC_CANVAS),
            platform="instagram_feed",
            canvas="1080x1350",
            accent_hex="#E10600",
            steps=(),
            verified_base_asset_ids=("verified-subject-visual",) if verified_asset else (),
            exact_asset_ids=("pul7sar-logo",),
            headline="Verified headline",
            score=None,
            exact_data=(),
            deterministic_elements=(),
            metadata={
                "contract": "pul7sar-direct-visual-execution-v2",
                "generation_package_created": False,
                "provider_selection_performed": False,
                "gpu_job_required": False,
                "generator_bypassed": True,
                "verified_subject_visual_ids": ("verified-subject-visual",) if verified_asset else (),
                "identity_reference_ids": ("verified-subject-reference",) if verified_asset else (),
            },
        )

    def verifier(self, *, identity=False, local=True, network=False):
        caps = {
            VisionVerificationCapability.SUBJECT_DETECTION,
            VisionVerificationCapability.SUBJECT_FRAMING,
            VisionVerificationCapability.SEMANTIC_DEFECTS,
            VisionVerificationCapability.FORBIDDEN_VISUALS,
            VisionVerificationCapability.PROTECTED_REGION_CLUTTER,
        }
        if identity:
            caps.add(VisionVerificationCapability.IDENTITY_SIMILARITY)
        return VisionVerifierProfile(verifier_id="direct-test-verifier", local_zero_cost=local, capabilities=frozenset(caps), requires_network=network)

    @staticmethod
    def subject_receipt(**overrides):
        values = dict(
            output_path="subject-composite.png",
            output_sha256="a" * 64,
            base_sha256="b" * 64,
            subject_asset_id="verified-subject-visual",
            subject_sha256="c" * 64,
            source_reference="trusted:subject:source",
            entity_name="Verified Player",
            identity_confidence=0.98,
            mode="transparent_cutout",
            identity_verified=True,
            generator_used=False,
            subject_placeholder_used=False,
            publication_ready=False,
        )
        values.update(overrides)
        return VerifiedSubjectCompositionReceipt(**values)

    def semantic(self, *, verified_asset=False, receipt=None, approved=True, evidence_ref="receipt.json"):
        return DirectSemanticPublicationGate().evaluate(
            self.plan(verified_asset=verified_asset),
            DirectRenderQualityDecision(True),
            self.verifier(identity=verified_asset),
            semantic_visual_inspection_approved=approved,
            semantic_evidence_reference=evidence_ref,
            verified_subject_receipt=receipt,
        )

    def test_deterministic_direct_render_requires_concrete_semantic_evidence(self):
        decision = self.semantic()
        self.assertTrue(decision.allowed)
        self.assertFalse(decision.identity_required)
        self.assertEqual(decision.evidence_reference, "receipt.json")
        missing = self.semantic(evidence_ref="")
        self.assertFalse(missing.allowed)
        self.assertIn("semantic_visual_inspection:evidence_reference_missing", missing.failures)

    def test_verified_asset_route_requires_subject_provenance_receipt(self):
        rejected = self.semantic(verified_asset=True, receipt=None)
        self.assertFalse(rejected.allowed)
        self.assertIn("verified_asset_identity:subject_provenance_receipt_missing", rejected.failures)
        accepted = self.semantic(verified_asset=True, receipt=self.subject_receipt())
        self.assertTrue(accepted.allowed)
        self.assertTrue(accepted.identity_verified)
        self.assertTrue(accepted.verified_subject_provenance_accepted)

    def test_verified_asset_receipt_identity_or_asset_drift_is_rejected(self):
        wrong_asset = self.semantic(verified_asset=True, receipt=self.subject_receipt(subject_asset_id="other-asset"))
        self.assertFalse(wrong_asset.allowed)
        self.assertIn("verified_asset_identity:subject_asset_id_drift", wrong_asset.failures)
        generated = self.semantic(verified_asset=True, receipt=self.subject_receipt(generator_used=True))
        self.assertFalse(generated.allowed)
        self.assertIn("verified_asset_identity:subject_was_generator_owned", generated.failures)

    def test_remote_or_incomplete_verifier_cannot_authorize_direct_publication(self):
        decision = DirectSemanticPublicationGate().evaluate(
            self.plan(), DirectRenderQualityDecision(True), self.verifier(local=False, network=True),
            semantic_visual_inspection_approved=True, semantic_evidence_reference="evidence.json",
        )
        self.assertFalse(decision.allowed)
        self.assertFalse(decision.semantic_verifier_eligible)

    def test_execution_lock_drift_blocks_even_with_clean_render(self):
        plan = self.plan()
        drifted = DirectVisualExecutionPlan(
            route=plan.route, base_source=plan.base_source, platform=plan.platform, canvas=plan.canvas,
            accent_hex=plan.accent_hex, steps=plan.steps, verified_base_asset_ids=plan.verified_base_asset_ids,
            exact_asset_ids=plan.exact_asset_ids, headline=plan.headline, score=plan.score,
            exact_data=plan.exact_data, deterministic_elements=plan.deterministic_elements,
            metadata={**dict(plan.metadata), "provider_selection_performed": True},
        )
        decision = DirectSemanticPublicationGate().evaluate(
            drifted, DirectRenderQualityDecision(True), self.verifier(),
            semantic_visual_inspection_approved=True, semantic_evidence_reference="evidence.json",
        )
        self.assertFalse(decision.allowed)
        self.assertIn("direct_execution_lock:provider_selection_performed", decision.failures)

    def test_final_readiness_requires_all_independent_gates(self):
        semantic = self.semantic()
        approved = DirectPublicationReadinessGate().evaluate(DirectPublicationReadinessEvidence(
            semantic_publication=semantic,
            fact_integrity_approved=True,
            neutrality_approved=True,
            golden_visual_approved=True,
            exact_brand_integrity_approved=True,
            typography_integrity_approved=True,
            export_authorization=ExportAuthorization(True, token="direct-export"),
        ))
        self.assertTrue(approved.ready)
        rejected = DirectPublicationReadinessGate().evaluate(DirectPublicationReadinessEvidence(
            semantic_publication=semantic,
            fact_integrity_approved=True,
            neutrality_approved=True,
            golden_visual_approved=False,
            exact_brand_integrity_approved=True,
            typography_integrity_approved=True,
            export_authorization=ExportAuthorization(True, token="direct-export"),
        ))
        self.assertFalse(rejected.ready)
        self.assertIn("golden_visual_quality:not_approved", rejected.blockers)


if __name__ == "__main__":
    unittest.main()
