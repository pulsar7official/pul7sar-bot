import unittest

from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.image_evidence_extraction import GeneratedImageObservation
from engine.intelligence.local_identity_similarity import (
    IdentitySimilarityIntegrityGate,
    IdentitySimilarityRequest,
    IdentitySimilarityResult,
)


class LocalIdentitySimilarityTests(unittest.TestCase):
    def setUp(self):
        self.image = GeneratedImageObservation("/tmp/scene.png", 1080, 1350, "4:5")
        self.package = GenerationPackage(
            platform="instagram_feed",
            canvas="1080x1350",
            scene_prompt="scene",
            negative_constraints=(),
            asset_ids=("sam-ref-1",),
            factual_constraints=(),
            metadata={
                "identity_required": True,
                "identity_entity_name": "Sam Hickey",
                "identity_reference_ids": ("sam-ref-1",),
            },
        )
        self.request = IdentitySimilarityRequest(self.image, ("sam-ref-1",), "Sam Hickey")
        self.gate = IdentitySimilarityIntegrityGate()

    def test_high_confidence_match_becomes_identity_evidence(self):
        result = IdentitySimilarityResult(True, 0.96, "local-face-v1", ("sam-ref-1",))
        evidence = self.gate.validate(self.package, self.request, result)
        self.assertTrue(evidence.matched)
        self.assertEqual(evidence.reference_ids, ("sam-ref-1",))

    def test_identity_mismatch_fails_closed(self):
        result = IdentitySimilarityResult(False, 0.97, "local-face-v1", ("sam-ref-1",))
        with self.assertRaisesRegex(ValueError, "did not match"):
            self.gate.validate(self.package, self.request, result)

    def test_reference_drift_fails_closed(self):
        result = IdentitySimilarityResult(True, 0.97, "local-face-v1", ("other-ref",))
        with self.assertRaisesRegex(ValueError, "changed or omitted"):
            self.gate.validate(self.package, self.request, result)

    def test_low_confidence_fails_closed(self):
        result = IdentitySimilarityResult(True, 0.72, "local-face-v1", ("sam-ref-1",))
        with self.assertRaisesRegex(ValueError, "below threshold"):
            self.gate.validate(self.package, self.request, result)


if __name__ == "__main__":
    unittest.main()
