import unittest

from engine.intelligence.direct_publication import (
    DirectPublicationReadinessEvidence,
    DirectPublicationReadinessGate,
    DirectSemanticPublicationGate,
)
from engine.intelligence.direct_visual_execution import DirectBaseSource, DirectVisualExecutionPlan
from engine.intelligence.direct_visual_quality import DirectRenderQualityDecision
from engine.intelligence.final_export import ExportAuthorization
from engine.intelligence.visual_execution_route import PixelExecutionRoute
from engine.intelligence.vision_verification_policy import (
    VisionVerificationCapability,
    VisionVerifierProfile,
)


class DirectPublicationGateTests(unittest.TestCase):
    def plan(self, *, verified_asset=False):
        return DirectVisualExecutionPlan(
            route=(PixelExecutionRoute.VERIFIED_ASSET_ONLY if verified_asset else PixelExecutionRoute.DETERMINISTIC_ONLY),
            base_source=(DirectBaseSource.VERIFIED_ASSET if verified_asset else DirectBaseSource.PROGRAMMATIC_CANVAS),
            platform="instagram_feed",
            canvas="1080x1350",
            accent_hex="#E10600",
            steps=(),
            verified_base_asset_ids=("verified-subject",) if verified_asset else (),
            exact_asset_ids=("pul7sar-logo",),
            headline="Verified headline",
            score=None,
            exact_data=(),
            deterministic_elements=(),
            metadata={
                "contract": "pul7sar-direct-visual-execution-v1",
                "generation_package_created": False,
                "provider_selection_performed": False,
                "gpu_job_required": False,
                "generator_bypassed": True,
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
        return VisionVerifierProfile(
            verifier_id="direct-test-verifier",
            local_zero_cost=local,
            capabilities=frozenset(caps),
            requires_network=network,
        )

    def semantic(self, *, verified_asset=False, identity_verified=None, approved=True, evidence_ref="receipt.json"):
        return DirectSemanticPublicationGate().evaluate(
            self.plan(verified_asset=verified_asset),
            DirectRenderQualityDecision(True),
            self.verifier(identity=verified_asset),
            semantic_visual_inspection_approved=approved,
            semantic_evidence_reference=evidence_ref,
            identity_verified=identity_verified,
        )

    def test_deterministic_direct_render_requires_concrete_semantic_evidence(self):
        decision = self.semantic()
        self.assertTrue(decision.allowed)
        self.assertFalse(decision.identity_required)
        self.assertEqual(decision.evidence_reference, "receipt.json")

        missing = self.semantic(evidence_ref="")
        self.assertFalse(missing.allowed)
        self.assertIn("semantic_visual_inspection:evidence_reference_missing", missing.failures)

    def test_verified_asset_route_requires_identity_verification(self):
        rejected = self.semantic(verified_asset=True, identity_verified=False)
        self.assertFalse(rejected.allowed)
        self.assertIn("verified_asset_identity:not_approved", rejected.failures)

        accepted = self.semantic(verified_asset=True, identity_verified=True)
        self.assertTrue(accepted.allowed)
        self.assertTrue(accepted.identity_required)
        self.assertTrue(accepted.identity_verified)

    def test_remote_or_incomplete_verifier_cannot_authorize_direct_publication(self):
        gate = DirectSemanticPublicationGate()
        remote = gate.evaluate(
            self.plan(),
            DirectRenderQualityDecision(True),
            self.verifier(local=False, network=True),
            semantic_visual_inspection_approved=True,
            semantic_evidence_reference="receipt.json",
        )
        self.assertFalse(remote.allowed)
        self.assertTrue(any(item.startswith("semantic_verifier:") for item in remote.failures))

    def test_execution_lock_drift_blocks_even_with_clean_render(self):
        plan = self.plan()
        broken = DirectVisualExecutionPlan(
            route=plan.route,
            base_source=plan.base_source,
            platform=plan.platform,
            canvas=plan.canvas,
            accent_hex=plan.accent_hex,
            steps=plan.steps,
            verified_base_asset_ids=plan.verified_base_asset_ids,
            exact_asset_ids=plan.exact_asset_ids,
            headline=plan.headline,
            score=plan.score,
            exact_data=plan.exact_data,
            deterministic_elements=plan.deterministic_elements,
            metadata={**dict(plan.metadata), "gpu_job_required": True},
        )
        decision = DirectSemanticPublicationGate().evaluate(
            broken,
            DirectRenderQualityDecision(True),
            self.verifier(),
            semantic_visual_inspection_approved=True,
            semantic_evidence_reference="receipt.json",
        )
        self.assertFalse(decision.allowed)
        self.assertIn("direct_execution_lock:gpu_job_required", decision.failures)

    def test_final_readiness_requires_all_independent_gates(self):
        semantic = self.semantic()
        gate = DirectPublicationReadinessGate()
        ready = gate.evaluate(DirectPublicationReadinessEvidence(
            semantic_publication=semantic,
            fact_integrity_approved=True,
            neutrality_approved=True,
            golden_visual_approved=True,
            exact_brand_integrity_approved=True,
            typography_integrity_approved=True,
            export_authorization=ExportAuthorization(True, (), "direct-export-token"),
        ))
        self.assertTrue(ready.ready)
        self.assertEqual(ready.status, "DIRECT_PUBLICATION_READY")

        blocked = gate.evaluate(DirectPublicationReadinessEvidence(
            semantic_publication=semantic,
            fact_integrity_approved=True,
            neutrality_approved=True,
            golden_visual_approved=False,
            exact_brand_integrity_approved=False,
            typography_integrity_approved=False,
            export_authorization=ExportAuthorization(False, ("typography missing",)),
        ))
        self.assertFalse(blocked.ready)
        self.assertIn("golden_visual_quality:not_approved", blocked.blockers)
        self.assertIn("exact_brand_integrity:not_approved", blocked.blockers)
        self.assertIn("typography_integrity:not_approved", blocked.blockers)
        self.assertIn("export:typography missing", blocked.blockers)


if __name__ == "__main__":
    unittest.main()
