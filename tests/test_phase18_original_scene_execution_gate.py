import unittest

from engine.intelligence.original_scene_execution_gate import OriginalSceneExecutionGate
from engine.intelligence.original_scene_runtime_contract import (
    OriginalSceneRequest,
    OriginalSceneRuntimeKind,
    OriginalSceneRuntimeQualification,
    UNQUALIFIED_ATMOSPHERE_RUNTIME,
)
from engine.intelligence.visual_concept_director import VisualConceptArchetype


RESERVED = ("readable_text", "pul7sar_brand", "exact_score", "club_crest")


def atmosphere_request():
    return OriginalSceneRequest(
        archetype=VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE,
        runtime_kind=OriginalSceneRuntimeKind.ATMOSPHERE,
        scene_intent="original football event atmosphere",
        emotional_tone="premium editorial tension",
        safe_negative_space="lower-right",
        forbidden_visual_claims=("real venue identity", "real person", "readable signage"),
        exact_fact_roles_reserved_for_compositor=RESERVED,
        seed=18,
    )


class OriginalSceneExecutionGateTests(unittest.TestCase):
    def setUp(self):
        self.gate = OriginalSceneExecutionGate()

    def test_missing_runtime_fails_closed(self):
        decision = self.gate.evaluate(atmosphere_request(), None)
        self.assertFalse(decision.admitted)
        self.assertEqual(decision.reason, "ORIGINAL_SCENE_RUNTIME_MISSING")

    def test_pending_runtime_is_not_admitted(self):
        decision = self.gate.evaluate(atmosphere_request(), UNQUALIFIED_ATMOSPHERE_RUNTIME)
        self.assertFalse(decision.admitted)
        self.assertEqual(decision.reason, "ORIGINAL_SCENE_RUNTIME_NOT_QUALIFIED")

    def test_qualified_local_runtime_is_admitted_but_not_publication_ready(self):
        runtime = OriginalSceneRuntimeQualification(
            runtime_id="test-local-atmosphere-v1",
            runtime_kind=OriginalSceneRuntimeKind.ATMOSPHERE,
            local_or_self_hosted=True,
            provider_agnostic_adapter=True,
            original_pixels=True,
            accepts_seed=True,
            semantic_inspection_required=True,
            identity_fidelity_gate_required=False,
            qualified=True,
        )
        decision = self.gate.evaluate(atmosphere_request(), runtime)
        self.assertTrue(decision.admitted)
        self.assertTrue(decision.requires_semantic_inspection)
        self.assertFalse(decision.publication_ready)

    def test_runtime_kind_mismatch_is_rejected(self):
        runtime = OriginalSceneRuntimeQualification(
            runtime_id="test-local-identity-v1",
            runtime_kind=OriginalSceneRuntimeKind.IDENTITY_CONDITIONED,
            local_or_self_hosted=True,
            provider_agnostic_adapter=True,
            original_pixels=True,
            accepts_seed=True,
            semantic_inspection_required=True,
            identity_fidelity_gate_required=True,
            qualified=True,
        )
        decision = self.gate.evaluate(atmosphere_request(), runtime)
        self.assertFalse(decision.admitted)
        self.assertEqual(decision.reason, "ORIGINAL_SCENE_RUNTIME_KIND_MISMATCH")


if __name__ == "__main__":
    unittest.main()
