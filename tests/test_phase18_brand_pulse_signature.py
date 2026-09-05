import unittest
from dataclasses import replace

from engine.intelligence.brand_pulse_signature import APPROVED_PUL7SAR_PULSE_SIGNATURE


class BrandPulseSignatureTests(unittest.TestCase):
    def test_approved_signature_is_safe(self):
        APPROVED_PUL7SAR_PULSE_SIGNATURE.assert_safe()
        self.assertEqual(APPROVED_PUL7SAR_PULSE_SIGNATURE.signature_id, "pul7sar-reference-pulse-v3-measured")
        self.assertEqual(APPROVED_PUL7SAR_PULSE_SIGNATURE.recovery_beats, 2)
        self.assertTrue(APPROVED_PUL7SAR_PULSE_SIGNATURE.long_horizontal_baseline)
        self.assertTrue(APPROVED_PUL7SAR_PULSE_SIGNATURE.active_waveform_compact)
        self.assertTrue(APPROVED_PUL7SAR_PULSE_SIGNATURE.excessive_vertical_excursion_forbidden)
        self.assertTrue(APPROVED_PUL7SAR_PULSE_SIGNATURE.visually_linked_to_enlarged_seven)
        self.assertTrue(APPROVED_PUL7SAR_PULSE_SIGNATURE.waveform_centered_on_seven_zone)
        self.assertFalse(APPROVED_PUL7SAR_PULSE_SIGNATURE.generic_ecg_allowed)

    def test_generic_ecg_cannot_replace_pul7sar_signature(self):
        forged = replace(APPROVED_PUL7SAR_PULSE_SIGNATURE, generic_ecg_allowed=True)
        with self.assertRaisesRegex(ValueError, "GENERIC_ECG_IS_NOT_PUL7SAR_IDENTITY"):
            forged.assert_safe()

    def test_reference_keeps_long_baseline_but_compact_active_waveform(self):
        forged = replace(APPROVED_PUL7SAR_PULSE_SIGNATURE, long_horizontal_baseline=False)
        with self.assertRaisesRegex(ValueError, "REQUIRES_HORIZONTAL_BASELINE"):
            forged.assert_safe()
        forged = replace(APPROVED_PUL7SAR_PULSE_SIGNATURE, active_waveform_compact=False)
        with self.assertRaisesRegex(ValueError, "ACTIVE_WAVEFORM_MUST_REMAIN_COMPACT"):
            forged.assert_safe()
        forged = replace(APPROVED_PUL7SAR_PULSE_SIGNATURE, excessive_vertical_excursion_forbidden=False)
        with self.assertRaisesRegex(ValueError, "VERTICAL_DEPTH_MAY_NOT_DRIFT"):
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
