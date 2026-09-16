import unittest

from engine.intelligence.image_evidence_extraction import GeneratedImageObservation
from engine.intelligence.local_subject_verifier import (
    SubjectVerificationIntegrityGate,
    SubjectVerificationRequest,
    SubjectVerificationResult,
)


class LocalSubjectVerifierTests(unittest.TestCase):
    def setUp(self):
        self.image = GeneratedImageObservation(
            output_ref="/tmp/scene.png",
            width=1080,
            height=1350,
            aspect_ratio="4:5",
        )
        self.gate = SubjectVerificationIntegrityGate()

    def test_valid_result_becomes_subject_framing_evidence(self):
        request = SubjectVerificationRequest(self.image, "Sam Hickey")
        result = SubjectVerificationResult(True, True, True, 0.94, "local-subject-v1")
        evidence = self.gate.validate(request, result)
        self.assertTrue(evidence.subject_present)
        self.assertEqual(evidence.confidence, 0.94)

    def test_missing_expected_subject_fails_closed(self):
        request = SubjectVerificationRequest(self.image, "Sam Hickey")
        result = SubjectVerificationResult(False, True, True, 0.95, "local-subject-v1")
        with self.assertRaisesRegex(ValueError, "not detected"):
            self.gate.validate(request, result)

    def test_bad_crop_fails_closed(self):
        request = SubjectVerificationRequest(self.image, "Charlie Hull")
        result = SubjectVerificationResult(True, False, True, 0.95, "local-subject-v1")
        with self.assertRaisesRegex(ValueError, "not fully visible"):
            self.gate.validate(request, result)

    def test_low_confidence_fails_closed(self):
        request = SubjectVerificationRequest(self.image, "Charlie Hull")
        result = SubjectVerificationResult(True, True, True, 0.60, "local-subject-v1")
        with self.assertRaisesRegex(ValueError, "below threshold"):
            self.gate.validate(request, result)


if __name__ == "__main__":
    unittest.main()
