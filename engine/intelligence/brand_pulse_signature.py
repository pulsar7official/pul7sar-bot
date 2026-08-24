"""Canonical semantic contract for the PUL7SAR pulse signature.

The user-confirmed reference uses a compact pulse signature concentrated around
the enlarged 7. It is NOT a full-width underline. Short horizontal shoulders
enter and leave the waveform; the dominant spike/trough lives directly in the 7
zone, followed by two compact recovery beats. Renderers must preserve these
proportions instead of stretching the pulse across the whole wordmark.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BrandPulseSignature:
    signature_id: str = "pul7sar-reference-pulse-v2-compact"
    compact_horizontal_shoulders: bool = True
    full_wordmark_underline_forbidden: bool = True
    compact_prebeat: bool = True
    dominant_central_spike: bool = True
    deep_post_spike_trough: bool = True
    recovery_beats: int = 2
    visually_linked_to_enlarged_seven: bool = True
    waveform_centered_on_seven_zone: bool = True
    generic_ecg_allowed: bool = False

    def assert_safe(self) -> None:
        if self.signature_id != "pul7sar-reference-pulse-v2-compact":
            raise ValueError("PUL7SAR_PULSE_SIGNATURE_CHANGED")
        if not self.compact_horizontal_shoulders:
            raise ValueError("PUL7SAR_PULSE_SHOULDERS_MUST_REMAIN_COMPACT")
        if not self.full_wordmark_underline_forbidden:
            raise ValueError("PUL7SAR_PULSE_MAY_NOT_UNDERLINE_FULL_WORDMARK")
        if not self.compact_prebeat:
            raise ValueError("PUL7SAR_PULSE_PREBEAT_MISSING")
        if not self.dominant_central_spike:
            raise ValueError("PUL7SAR_PULSE_DOMINANT_SPIKE_MISSING")
        if not self.deep_post_spike_trough:
            raise ValueError("PUL7SAR_PULSE_TROUGH_MISSING")
        if self.recovery_beats != 2:
            raise ValueError("PUL7SAR_PULSE_RECOVERY_BEAT_COUNT_CHANGED")
        if not self.visually_linked_to_enlarged_seven or not self.waveform_centered_on_seven_zone:
            raise ValueError("PUL7SAR_PULSE_SEVEN_LINK_BROKEN")
        if self.generic_ecg_allowed:
            raise ValueError("GENERIC_ECG_IS_NOT_PUL7SAR_IDENTITY")


APPROVED_PUL7SAR_PULSE_SIGNATURE = BrandPulseSignature()
