import unittest
from dataclasses import replace

from engine.intelligence.brand_pulse_signature import APPROVED_PUL7SAR_PULSE_SIGNATURE


class BrandPulseSignatureTests(unittest.TestCase):
    def test_approved_signature_is_safe(self):
        APPROVED_PUL7SAR_PULSE_SIGNATURE.assert_safe()
        self.assertEqual(APPROVED_PUL7SAR_PULSE_SIGNATURE.signature_id, "pul7sar-reference-pulse-v2-compact")
        self.assertEqual(APPROVED_PUL7SAR_PULSE_SIGNATURE.recovery_beats, 2)
        self.assertTrue(APPROVED_PUL7SAR_PULSE_SIGNATURE.compact_horizontal_shoulders)
        self.assertTrue(APPROVED_PUL7SAR_PULSE_SIGNATURE.full_wordmark_underline_forbidden)
        self.assertTrue(APPROVED_PUL7SAR_PULSE_SIGNATURE.visually_linked_to_enlarged_seven)
        self.assertTrue(APPROVED_PUL7SAR_PULSE_SIGNATURE.waveform_centered_on_seven_zone)
        self.assertFalse(APPROVED_PUL7SAR_PULSE_SIGNATURE.generic_ecg_allowed)

    def test_generic_ecg_cannot_replace_pul7sar_signature(self):
        forged = replace(APPROVED_PUL7SAR_PULSE_SIGNATURE, generic_ecg_allowed=True)
        with self.assertRaisesRegex(ValueError, "GENERIC_ECG_IS_NOT_PUL7SAR_IDENTITY"):
            forged.assert_safe()

    def test_full_wordmark_underline_is_forbidden(self):
        forged = replace(APPROVED_PUL7SAR_PULSE_SIGNATURE, full_wordmark_underline_forbidden=False)
        with self.assertRaisesRegex(ValueError, "MAY_NOT_UNDERLINE_FULL_WORDMARK"):
            forged.assert_safe()
        forged = replace(APPROVED_PUL7SAR_PULSE_SIGNATURE, compact_horizontal_shoulders=False)
        with self.assertRaisesRegex(ValueError, "SHOULDERS_MUST_REMAIN_COMPACT"):
            forged.assert_safe()

    def test_seven_link_and_recovery_pattern_are_locked(self):
        forged = replace(APPROVED_PUL7SAR_PULSE_SIGNATURE, visually_linked_to_enlarged_seven=False)
        with self.assertRaisesRegex(ValueError, "PULSE_SEVEN_LINK_BROKEN"):
            forged.assert_safe()
        forged = replace(APPROVED_PUL7SAR_PULSE_SIGNATURE, waveform_centered_on_seven_zone=False)
        with self.assertRaisesRegex(ValueError, "PULSE_SEVEN_LINK_BROKEN"):
            forged.assert_safe()
        forged = replace(APPROVED_PUL7SAR_PULSE_SIGNATURE, recovery_beats=3)
        with self.assertRaisesRegex(ValueError, "RECOVERY_BEAT_COUNT_CHANGED"):
            forged.assert_safe()


if __name__ == "__main__":
    unittest.main()
