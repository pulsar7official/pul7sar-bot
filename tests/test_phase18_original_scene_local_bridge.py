import unittest

from engine.intelligence.local_readiness_report import LocalGenerationReadinessReport
from engine.intelligence.original_scene_local_bridge import OriginalSceneLocalBridge, OriginalSceneLocalRuntimeQualifier
from engine.intelligence.original_scene_request_builder import OriginalSceneRequestBuilder
from engine.intelligence.original_scene_runtime_contract import OriginalSceneRuntimeKind
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily
from engine.intelligence.visual_concept_director import VisualConceptDirector, VisualConceptSignals
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


def readiness(*, ready=True, runtime_kind="local_cuda", provider_id=None, model_id=None, backend="diffusers"):
    return LocalGenerationReadinessReport(
        ready=ready,
        provider_id=provider_id or FLUX2_KLEIN_4B_LOCAL.provider_id,
        model_id=model_id or FLUX2_KLEIN_4B_LOCAL.model_id,
        backend=backend,
        runtime_kind=runtime_kind,
        gpu_name="test-cuda" if runtime_kind == "local_cuda" else None,
        gpu_vram_gb=16.0 if runtime_kind == "local_cuda" else None,
        blockers=() if ready else ("not-ready",),
        warnings=(),
    )


class OriginalSceneLocalBridgeTests(unittest.TestCase):
    def setUp(self):
        director = VisualConceptDirector()
        decision = director.direct(
            EditorialSceneFamily.EVENT_EDITORIAL,
            VisualConceptSignals(safe_generated_context=True),
        )
        self.request = OriginalSceneRequestBuilder().build(
            decision,
            emotional_tone="premium season-opening anticipation",
            safe_negative_space="upper-left",
            seed=7007001,
        )

    def test_flux_atmosphere_runtime_qualifies_only_from_ready_cuda_evidence(self):
        runtime = OriginalSceneLocalRuntimeQualifier().qualify(
            model=FLUX2_KLEIN_4B_LOCAL,
            readiness=readiness(),
            runtime_kind=OriginalSceneRuntimeKind.ATMOSPHERE,
        )
        self.assertTrue(runtime.qualified)
        self.assertFalse(runtime.paid_provider_required)
        self.assertFalse(runtime.network_dependency_required)

    def test_cpu_or_unready_runtime_does_not_qualify(self):
        qualifier = OriginalSceneLocalRuntimeQualifier()
        self.assertFalse(qualifier.qualify(
            model=FLUX2_KLEIN_4B_LOCAL,
            readiness=readiness(ready=False),
            runtime_kind=OriginalSceneRuntimeKind.ATMOSPHERE,
        ).qualified)
        self.assertFalse(qualifier.qualify(
            model=FLUX2_KLEIN_4B_LOCAL,
            readiness=readiness(runtime_kind="local_cpu"),
            runtime_kind=OriginalSceneRuntimeKind.ATMOSPHERE,
        ).qualified)

    def test_flux_is_not_silently_promoted_to_identity_conditioned_runtime(self):
        runtime = OriginalSceneLocalRuntimeQualifier().qualify(
            model=FLUX2_KLEIN_4B_LOCAL,
            readiness=readiness(),
            runtime_kind=OriginalSceneRuntimeKind.IDENTITY_CONDITIONED,
        )
        self.assertFalse(runtime.qualified)
        self.assertTrue(runtime.identity_fidelity_gate_required)

    def test_admitted_request_compiles_to_locked_zero_cost_local_request(self):
        compiled, receipt = OriginalSceneLocalBridge().compile(
            request=self.request,
            model=FLUX2_KLEIN_4B_LOCAL,
            readiness=readiness(),
            backend="diffusers",
            request_id="golden-original-scene-001",
        )
        self.assertEqual(compiled.seed, 7007001)
        self.assertEqual(compiled.metadata["cost_mode"], "$0-local")
        self.assertFalse(compiled.metadata["generated_branding_allowed"])
        self.assertFalse(compiled.metadata["generated_exact_facts_allowed"])
        self.assertFalse(compiled.metadata["generated_sport_geometry_allowed"])
        self.assertTrue(compiled.metadata["semantic_inspection_required"])
        self.assertFalse(compiled.metadata["publication_ready"])
        self.assertFalse(receipt.publication_ready)
        self.assertNotIn("pul7sar", compiled.prompt.casefold())
        self.assertNotIn("pulsar", compiled.prompt.casefold())

    def test_readiness_identity_drift_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "ORIGINAL_SCENE_LOCAL_RUNTIME_NOT_ADMITTED"):
            OriginalSceneLocalBridge().compile(
                request=self.request,
                model=FLUX2_KLEIN_4B_LOCAL,
                readiness=readiness(provider_id="wrong-provider"),
                backend="diffusers",
                request_id="golden-original-scene-001",
            )

    def test_unknown_forbidden_claim_cannot_be_silently_dropped(self):
        request = self.request.__class__(
            archetype=self.request.archetype,
            runtime_kind=self.request.runtime_kind,
            scene_intent=self.request.scene_intent,
            emotional_tone=self.request.emotional_tone,
            safe_negative_space=self.request.safe_negative_space,
            forbidden_visual_claims=("mysterious unsupported visual prohibition",),
            exact_fact_roles_reserved_for_compositor=self.request.exact_fact_roles_reserved_for_compositor,
            seed=self.request.seed,
        )
        with self.assertRaisesRegex(ValueError, "ORIGINAL_SCENE_FORBIDDEN_CLAIM_NOT_TRANSLATED"):
            OriginalSceneLocalBridge().compile(
                request=request,
                model=FLUX2_KLEIN_4B_LOCAL,
                readiness=readiness(),
                backend="diffusers",
                request_id="golden-original-scene-001",
            )


if __name__ == "__main__":
    unittest.main()
