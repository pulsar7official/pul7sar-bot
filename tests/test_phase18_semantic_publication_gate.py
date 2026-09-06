import unittest

from engine.intelligence.base_scene_quality import (
    BaseSceneEvidence,
    GenerationDefectEvidence,
    IdentityVisualEvidence,
    ProtectedRegionEvidence,
    SubjectFramingEvidence,
)
from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.semantic_publication_gate import SemanticPublicationGate
from engine.intelligence.vision_verification_policy import (
    VisionVerificationCapability as C,
    VisionVerifierProfile,
)


class SemanticPublicationGateTests(unittest.TestCase):
    def package(self, *, identity_required=False):
        refs = ("identity-ref-1",) if identity_required else ()
        return GenerationPackage(
            platform="instagram_story",
            canvas="1080x1920",
            scene_prompt="premium sports editorial base scene",
            negative_constraints=(),
            asset_ids=refs,
            factual_constraints=(),
            layout_boxes={"hero": {"x": 0, "y": 0, "width": 700, "height": 1500}},
            metadata={"identity_required": identity_required, "identity_reference_ids": refs},
        )

    def evidence(self, *, identity_required=False, refs=None):
        refs = refs if refs is not None else (("identity-ref-1",) if identity_required else ())
        return BaseSceneEvidence(
            provider_id="local",
            output_ref="scene.png",
            width=1080,
            height=1920,
            aspect_ratio="9:16",
            framing=SubjectFramingEvidence(True, True, True, 0.97),
            identity=IdentityVisualEvidence(identity_required, True, 0.98, refs),
            protected_regions=(),
            defects=GenerationDefectEvidence(True),
            forbidden_visuals_detected=(),
            safe_crop_possible=True,
            provenance={"request_id": "req-1"},
        )

    def verifier(self, *, identity=False, complete=True):
        caps = {C.SUBJECT_DETECTION, C.SUBJECT_FRAMING, C.SEMANTIC_DEFECTS, C.FORBIDDEN_VISUALS, C.PROTECTED_REGION_CLUTTER}
        if identity:
            caps.add(C.IDENTITY_SIMILARITY)
        if not complete:
            caps.discard(C.SEMANTIC_DEFECTS)
        return VisionVerifierProfile("local-complete", True, frozenset(caps))

    def test_complete_non_identity_scene_is_publication_ready(self):
        decision = SemanticPublicationGate().evaluate(self.package(), self.evidence(), self.verifier())
        self.assertTrue(decision.allowed)

    def test_identity_story_requires_identity_capability(self):
        decision = SemanticPublicationGate().evaluate(
            self.package(identity_required=True),
            self.evidence(identity_required=True),
            self.verifier(identity=False),
        )
        self.assertFalse(decision.allowed)
        self.assertTrue(any("identity_similarity" in failure for failure in decision.failures))

    def test_incomplete_semantic_verification_blocks_publication(self):
        decision = SemanticPublicationGate().evaluate(self.package(), self.evidence(), self.verifier(complete=False))
        self.assertFalse(decision.allowed)

    def test_identity_reference_mismatch_blocks_publication(self):
        decision = SemanticPublicationGate().evaluate(
            self.package(identity_required=True),
            self.evidence(identity_required=True, refs=("wrong-ref",)),
            self.verifier(identity=True),
        )
        self.assertFalse(decision.allowed)
        self.assertIn("visual identity evidence does not match approved reference IDs", decision.failures)

    def test_generated_scene_with_bad_framing_is_still_blocked(self):
        evidence = self.evidence()
        evidence = BaseSceneEvidence(
            provider_id=evidence.provider_id,
            output_ref=evidence.output_ref,
            width=evidence.width,
            height=evidence.height,
            aspect_ratio=evidence.aspect_ratio,
            framing=SubjectFramingEvidence(True, False, True, 0.97),
            identity=evidence.identity,
            protected_regions=evidence.protected_regions,
            defects=evidence.defects,
            provenance=evidence.provenance,
        )
        decision = SemanticPublicationGate().evaluate(self.package(), evidence, self.verifier())
        self.assertFalse(decision.allowed)
        self.assertFalse(decision.base_scene_accepted)


if __name__ == "__main__":
    unittest.main()
