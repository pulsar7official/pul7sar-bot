import unittest

from engine.intelligence.brand_approval_evidence import APPROVED_BRAND_GUIDE_EVIDENCE


class BrandApprovalEvidenceTests(unittest.TestCase):
    def test_approved_guide_fingerprint_and_decisions_are_locked(self):
        evidence = APPROVED_BRAND_GUIDE_EVIDENCE
        self.assertEqual(evidence.sha256, "0817d597efad133a9f599c1f9c8c1d0e31126a7528311791ab1ca3d68a1b47e6")
        self.assertIn("number 7 remains larger than surrounding letters", evidence.decisions)
        self.assertIn("pulse remains below wordmark", evidence.decisions)
        self.assertIn("small football remains near R as football signature", evidence.decisions)
        self.assertIn("only pulse and number 7 change with verified club/story color", evidence.decisions)


if __name__ == "__main__":
    unittest.main()
