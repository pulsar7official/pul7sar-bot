import unittest
from dataclasses import replace

from engine.intelligence.brand_master_contract import APPROVED_PUL7SAR_BRAND_MASTER


class BrandMasterContractTests(unittest.TestCase):
    def test_approved_contract_is_safe(self):
        brand = APPROVED_PUL7SAR_BRAND_MASTER
        brand.assert_safe()
        self.assertEqual(brand.wordmark_text, "PUL7SAR")
        self.assertEqual(brand.wordmark_finish, "metallic_silver_fixed")
        self.assertTrue(brand.seven_larger_than_letters)
        self.assertEqual(brand.pulse_position, "below_wordmark")
        self.assertTrue(brand.small_football_near_r)
        self.assertTrue(brand.pulse_seven_dynamic)
        self.assertTrue(brand.only_pulse_and_seven_are_tintable)
        self.assertEqual(brand.preferred_brand_zone, "lower_composition_when_clear")
        self.assertFalse(brand.legacy_repo_logo_is_canonical)

    def test_legacy_repo_logo_cannot_be_promoted_to_canonical(self):
        forged = replace(APPROVED_PUL7SAR_BRAND_MASTER, legacy_repo_logo_is_canonical=True)
        with self.assertRaisesRegex(ValueError, "LEGACY_REPO_LOGO_MUST_NOT_BECOME_CANONICAL"):
            forged.assert_safe()

    def test_generator_cannot_own_brand_identity(self):
        forged = replace(APPROVED_PUL7SAR_BRAND_MASTER, generator_may_invent_brand=True)
        with self.assertRaisesRegex(ValueError, "GENERATOR_MAY_NOT_INVENT_PUL7SAR_BRAND"):
            forged.assert_safe()

    def test_seven_size_and_pulse_position_are_identity_signatures(self):
        with self.assertRaisesRegex(ValueError, "SEVEN_SIZE_SIGNATURE"):
            replace(APPROVED_PUL7SAR_BRAND_MASTER, seven_larger_than_letters=False).assert_safe()
        with self.assertRaisesRegex(ValueError, "PULSE_POSITION_CHANGED"):
            replace(APPROVED_PUL7SAR_BRAND_MASTER, pulse_position="inside_wordmark").assert_safe()

    def test_wordmark_cannot_be_tinted_with_club_color(self):
        with self.assertRaisesRegex(ValueError, "WORDMARK_MUST_NOT_BE_TINTED"):
            replace(APPROVED_PUL7SAR_BRAND_MASTER, only_pulse_and_seven_are_tintable=False).assert_safe()


if __name__ == "__main__":
    unittest.main()
