import unittest

from engine.intelligence.original_scene_runtime_contract import (
    OriginalSceneRequest,
    OriginalSceneRuntimeKind,
    OriginalSceneRuntimeQualification,
    UNQUALIFIED_ATMOSPHERE_RUNTIME,
    UNQUALIFIED_IDENTITY_RUNTIME,
)
from engine.intelligence.visual_concept_director import VisualConceptArchetype


RESERVED = ("readable_text", "pul7sar_brand", "exact_score", "club_crest")


class OriginalSceneRuntimeContractTests(unittest.TestCase):
    def test_atmosphere_request_reserves_all_exact_fact_layers(self):
        req = OriginalSceneRequest(
            archetype=VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE,
            runtime_kind=OriginalSceneRuntimeKind.ATMOSPHERE,
            scene_intent="original football-night atmosphere without identifiable venue",
            emotional_tone="tense premium editorial",
            safe_negative_space="lower-right and upper-left",
            forbidden_visual_claims=("real venue identity", "readable signage", "real person"),
            exact_fact_roles_reserved_for_compositor=RESERVED,
            context_reference_ids=("reference:match-mood-001",),
            seed=18,
        )
        self.assertEqual(req.contract, "pul7sar-original-scene-request-v1")
        self.assertIn("pul7sar_brand", req.exact_fact_roles_reserved_for_compositor)

    def test_identity_conditioned_request_requires_verified_reference(self):
        with self.assertRaisesRegex(ValueError, "IDENTITY_CONDITIONED_SCENE_REQUIRES_VERIFIED_IDENTITY_REFERENCE"):
            OriginalSceneRequest(
                archetype=VisualConceptArchetype.HERO_ARRIVAL,
                runtime_kind=OriginalSceneRuntimeKind.IDENTITY_CONDITIONED,
                scene_intent="original player arrival",
                emotional_tone="confident",
                safe_negative_space="right",
                forbidden_visual_claims=("wrong identity",),
                exact_fact_roles_reserved_for_compositor=RESERVED,
            )

    def test_phase18_pending_runtimes_are_explicitly_unqualified(self):
        self.assertFalse(UNQUALIFIED_ATMOSPHERE_RUNTIME.qualified)
        self.assertFalse(UNQUALIFIED_IDENTITY_RUNTIME.qualified)
        self.assertFalse(UNQUALIFIED_ATMOSPHERE_RUNTIME.network_dependency_required)
        self.assertFalse(UNQUALIFIED_IDENTITY_RUNTIME.paid_provider_required)

    def test_paid_or_network_required_runtime_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "MAY_NOT_REQUIRE_NETWORK_OR_PAID_PROVIDER"):
            OriginalSceneRuntimeQualification(
                runtime_id="bad-provider",
                runtime_kind=OriginalSceneRuntimeKind.ATMOSPHERE,
                local_or_self_hosted=False,
                provider_agnostic_adapter=False,
                original_pixels=True,
                accepts_seed=True,
                semantic_inspection_required=True,
                identity_fidelity_gate_required=False,
                network_dependency_required=True,
                paid_provider_required=True,
            )


if __name__ == "__main__":
    unittest.main()
