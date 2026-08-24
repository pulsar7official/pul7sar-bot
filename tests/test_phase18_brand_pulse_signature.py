import unittest
from dataclasses import replace

from engine.intelligence.brand_pulse_signature import APPROVED_PUL7SAR_PULSE_SIGNATURE


class BrandPulseSignatureTests(unittest.TestCase):
    def test_approved_signature_is_safe(self):
        APPROVED_PUL7SAR_PULSE_SIGNATURE.assert_safe()
        self.assertEqual(APPROVED_PUL7SAR_PULSE_SIGNATURE.recovery_beats, 2)
        self.assertTrue(APPROVED_PUL7SAR_PULSE_SIGNATURE.visually_linked_to_enlarged_seven)
        self.assertFalse(APPROVED_PUL7SAR_PULSE_SIGNATURE.generic_ecg_allowed)

    def test_generic_ecg_cannot_replace_pul7sar_signature(self):
        forged = replace(APPROVED_PUL7SAR_PULSE_SIGNATURE, generic_ecg_allowed=True)
        with self.assertRaisesRegex(ValueError, "GENERIC_ECG_IS_NOT_PUL7SAR_IDENTITY"):
            forged.assert_safe()

    def test_seven_link_and_recovery_pattern_are_locked(self):
        forged = replace(APPROVED_PUL7SAR_PULSE_SIGNATURE, visually_linked_to_enlarged_seven=False)
        with self.assertRaisesRegex(ValueError, "PULSE_SEVEN_LINK_BROKEN"):
            forged.assert_safe()
        forged = replace(APPROVED_PUL7SAR_PULSE_SIGNATURE, recovery_beats=3)
        with self.assertRaisesRegex(ValueError, "RECOVERY_BEAT_COUNT_CHANGED"):
            forged.assert_safe()


if __name__ == "__main__":
    unittest.main()
