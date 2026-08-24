"""Canonical semantic contract for the PUL7SAR pulse signature.

This is intentionally renderer-independent. The user-approved identity does not
permit an arbitrary ECG line: the pulse must read as a long baseline, compact
pre-beat, dominant central rise/deep trough visually tied to the enlarged 7,
two shorter recovery beats, then a return to baseline.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BrandPulseSignature:
    signature_id: str = "pul7sar-reference-pulse-v1"
    baseline_enters_from_left: bool = True
    compact_prebeat: bool = True
    dominant_central_spike: bool = True
    deep_post_spike_trough: bool = True
    recovery_beats: int = 2
    baseline_exits_right: bool = True
    visually_linked_to_enlarged_seven: bool = True
    generic_ecg_allowed: bool = False

    def assert_safe(self) -> None:
        if self.signature_id != "pul7sar-reference-pulse-v1":
            raise ValueError("PUL7SAR_PULSE_SIGNATURE_CHANGED")
        if not self.baseline_enters_from_left or not self.baseline_exits_right:
            raise ValueError("PUL7SAR_PULSE_BASELINE_SIGNATURE_CHANGED")
        if not self.compact_prebeat:
            raise ValueError("PUL7SAR_PULSE_PREBEAT_MISSING")
        if not self.dominant_central_spike:
            raise ValueError("PUL7SAR_PULSE_DOMINANT_SPIKE_MISSING")
        if not self.deep_post_spike_trough:
            raise ValueError("PUL7SAR_PULSE_TROUGH_MISSING")
        if self.recovery_beats != 2:
            raise ValueError("PUL7SAR_PULSE_RECOVERY_BEAT_COUNT_CHANGED")
        if not self.visually_linked_to_enlarged_seven:
            raise ValueError("PUL7SAR_PULSE_SEVEN_LINK_BROKEN")
        if self.generic_ecg_allowed:
            raise ValueError("GENERIC_ECG_IS_NOT_PUL7SAR_IDENTITY")


APPROVED_PUL7SAR_PULSE_SIGNATURE = BrandPulseSignature()
