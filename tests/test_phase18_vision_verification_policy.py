import unittest

from engine.intelligence.vision_verification_policy import (
    VisionVerificationCapability as C,
    VisionVerifierProfile,
    ZeroCostVisionVerificationGate,
)


class VisionVerificationPolicyTests(unittest.TestCase):
    def setUp(self):
        self.gate = ZeroCostVisionVerificationGate()
        self.base = {C.SUBJECT_DETECTION, C.SUBJECT_FRAMING, C.SEMANTIC_DEFECTS, C.FORBIDDEN_VISUALS, C.PROTECTED_REGION_CLUTTER}

    def profile(self, capabilities, **kwargs):
        return VisionVerifierProfile("test-local", True, frozenset(capabilities), **kwargs)

    def test_non_identity_story_does_not_require_face_similarity(self):
        decision = self.gate.evaluate(self.profile(self.base), identity_required=False)
        self.assertTrue(decision.eligible)

    def test_identity_story_requires_identity_similarity(self):
        decision = self.gate.evaluate(self.profile(self.base), identity_required=True)
        self.assertFalse(decision.eligible)
        self.assertIn(C.IDENTITY_SIMILARITY, decision.missing)

    def test_complete_identity_profile_is_eligible(self):
        decision = self.gate.evaluate(self.profile(self.base | {C.IDENTITY_SIMILARITY}), identity_required=True)
        self.assertTrue(decision.eligible)

    def test_paid_verifier_is_rejected_even_if_complete(self):
        profile = VisionVerifierProfile("paid", False, frozenset(self.base | {C.IDENTITY_SIMILARITY}))
        decision = self.gate.evaluate(profile, identity_required=True)
        self.assertFalse(decision.eligible)
        self.assertTrue(any("zero-cost" in item for item in decision.failures))

    def test_network_dependent_verifier_is_rejected_in_local_mode(self):
        profile = self.profile(self.base | {C.IDENTITY_SIMILARITY}, requires_network=True)
        decision = self.gate.evaluate(profile, identity_required=True)
        self.assertFalse(decision.eligible)
        self.assertTrue(any("network" in item for item in decision.failures))

    def test_missing_semantic_defect_check_blocks_publication(self):
        capabilities = self.base - {C.SEMANTIC_DEFECTS}
        decision = self.gate.evaluate(self.profile(capabilities), identity_required=False)
        self.assertFalse(decision.eligible)
        self.assertIn(C.SEMANTIC_DEFECTS, decision.missing)


if __name__ == "__main__":
    unittest.main()
