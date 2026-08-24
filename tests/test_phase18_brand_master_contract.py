import unittest
from dataclasses import replace

from engine.intelligence.brand_master_contract import APPROVED_PUL7SAR_BRAND_MASTER


class BrandMasterContractTests(unittest.TestCase):
    def test_approved_contract_is_safe(self):
        APPROVED_PUL7SAR_BRAND_MASTER.assert_safe()
        self.assertEqual(APPROVED_PUL7SAR_BRAND_MASTER.wordmark_text, "PUL7SAR")
        self.assertTrue(APPROVED_PUL7SAR_BRAND_MASTER.pulse_seven_dynamic)
        self.assertFalse(APPROVED_PUL7SAR_BRAND_MASTER.legacy_repo_logo_is_canonical)

    def test_legacy_repo_logo_cannot_be_promoted_to_canonical(self):
        forged = replace(APPROVED_PUL7SAR_BRAND_MASTER, legacy_repo_logo_is_canonical=True)
        with self.assertRaisesRegex(ValueError, "LEGACY_REPO_LOGO_MUST_NOT_BECOME_CANONICAL"):
            forged.assert_safe()

    def test_generator_cannot_own_brand_identity(self):
        forged = replace(APPROVED_PUL7SAR_BRAND_MASTER, generator_may_invent_brand=True)
        with self.assertRaisesRegex(ValueError, "GENERATOR_MAY_NOT_INVENT_PUL7SAR_BRAND"):
            forged.assert_safe()


if __name__ == "__main__":
    unittest.main()
