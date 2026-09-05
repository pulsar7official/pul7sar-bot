import unittest

from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.image_evidence_extraction import GeneratedImageObservation
from engine.intelligence.local_semantic_safety import (
    SemanticSafetyIntegrityGate,
    SemanticSafetyRequest,
    SemanticSafetyResult,
)


class LocalSemanticSafetyTests(unittest.TestCase):
    def setUp(self):
        self.image = GeneratedImageObservation("/tmp/scene.png", 1080, 1350, "4:5")
        self.package = GenerationPackage(
            platform="instagram_feed",
            canvas="1080x1350",
            scene_prompt="scene",
            negative_constraints=("no humiliation", "no fake crest"),
            asset_ids=(),
            factual_constraints=(),
        )
        self.request = SemanticSafetyRequest(self.image, ("no humiliation", "no fake crest"))
        self.gate = SemanticSafetyIntegrityGate()

    def test_clean_high_confidence_result_is_accepted(self):
        result = SemanticSafetyResult(True, (), (), 0.96, "local-semantic-v1")
        evidence = self.gate.validate(self.package, self.request, result)
        self.assertTrue(evidence.defects.defect_free)
        self.assertEqual(evidence.forbidden_visuals_detected, ())

    def test_generation_defect_blocks_scene(self):
        result = SemanticSafetyResult(False, ("extra finger",), (), 0.97, "local-semantic-v1")
        with self.assertRaisesRegex(ValueError, "defects"):
            self.gate.validate(self.package, self.request, result)

    def test_forbidden_visual_blocks_scene(self):
        result = SemanticSafetyResult(True, (), ("fake crest",), 0.97, "local-semantic-v1")
        with self.assertRaisesRegex(ValueError, "forbidden"):
            self.gate.validate(self.package, self.request, result)

    def test_low_confidence_blocks_scene(self):
        result = SemanticSafetyResult(True, (), (), 0.61, "local-semantic-v1")
        with self.assertRaisesRegex(ValueError, "below threshold"):
            self.gate.validate(self.package, self.request, result)

    def test_request_must_match_locked_forbidden_visuals(self):
        request = SemanticSafetyRequest(self.image, ("no humiliation",))
        result = SemanticSafetyResult(True, (), (), 0.97, "local-semantic-v1")
        with self.assertRaisesRegex(ValueError, "locked forbidden visuals"):
            self.gate.validate(self.package, request, result)


if __name__ == "__main__":
    unittest.main()
