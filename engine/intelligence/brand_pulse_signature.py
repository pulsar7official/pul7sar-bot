"""Canonical semantic contract for the PUL7SAR pulse signature.

Measured against the user-approved identity board: the horizontal baseline may
span broadly beneath the wordmark, but the ACTIVE waveform excursions are compact
and centered on the enlarged 7. The earlier study error was excessive waveform
vertical depth/width, not the mere existence of the baseline.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BrandPulseSignature:
    signature_id: str = "pul7sar-reference-pulse-v3-measured"
    long_horizontal_baseline: bool = True
    active_waveform_compact: bool = True
    compact_prebeat: bool = True
    dominant_central_spike: bool = True
    controlled_post_spike_trough: bool = True
    recovery_beats: int = 2
    visually_linked_to_enlarged_seven: bool = True
    waveform_centered_on_seven_zone: bool = True
    excessive_vertical_excursion_forbidden: bool = True
    generic_ecg_allowed: bool = False

    def assert_safe(self) -> None:
        if self.signature_id != "pul7sar-reference-pulse-v3-measured":
            raise ValueError("PUL7SAR_PULSE_SIGNATURE_CHANGED")
        if not self.long_horizontal_baseline:
            raise ValueError("PUL7SAR_REFERENCE_REQUIRES_HORIZONTAL_BASELINE")
        if not self.active_waveform_compact:
            raise ValueError("PUL7SAR_ACTIVE_WAVEFORM_MUST_REMAIN_COMPACT")
        if not self.compact_prebeat:
            raise ValueError("PUL7SAR_PULSE_PREBEAT_MISSING")
        if not self.dominant_central_spike:
            raise ValueError("PUL7SAR_PULSE_DOMINANT_SPIKE_MISSING")
        if not self.controlled_post_spike_trough:
            raise ValueError("PUL7SAR_PULSE_TROUGH_SIGNATURE_CHANGED")
        if self.recovery_beats != 2:
            raise ValueError("PUL7SAR_PULSE_RECOVERY_BEAT_COUNT_CHANGED")
        if not self.visually_linked_to_enlarged_seven or not self.waveform_centered_on_seven_zone:
            raise ValueError("PUL7SAR_PULSE_SEVEN_LINK_BROKEN")
        if not self.excessive_vertical_excursion_forbidden:
            raise ValueError("PUL7SAR_PULSE_VERTICAL_DEPTH_MAY_NOT_DRIFT")
        if self.generic_ecg_allowed:
            raise ValueError("GENERIC_ECG_IS_NOT_PUL7SAR_IDENTITY")


APPROVED_PUL7SAR_PULSE_SIGNATURE = BrandPulseSignature()
