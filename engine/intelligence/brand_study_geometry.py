"""Study-only geometry for approximating the approved PUL7SAR identity.

The pulse signature is now locked to the user-confirmed reference family: a long
horizontal baseline enters from the left, a compact pre-beat leads into a tall
central spike, a deep trough follows, then two shorter recovery beats return to
the baseline before it continues toward the football near R. This is deliberately
NOT a generic ECG waveform and must remain visually tied to the enlarged 7.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.brand_master_contract import APPROVED_PUL7SAR_BRAND_MASTER


# Normalized (x,y) points inside the pulse band. y=0.5 is baseline.
# The sequence captures the approved reference topology, not arbitrary ECG art.
REFERENCE_PULSE_WAVEFORM_V1: tuple[tuple[float, float], ...] = (
    (0.04, 0.52),
    (0.31, 0.52),
    (0.345, 0.52),
    (0.365, 0.43),   # small pre-beat
    (0.385, 0.58),
    (0.415, 0.18),   # first strong rise
    (0.455, 0.91),   # deep trough
    (0.495, 0.04),   # dominant central spike linked visually to 7
    (0.535, 0.72),
    (0.565, 0.31),   # recovery beat 1
    (0.595, 0.61),
    (0.625, 0.39),   # recovery beat 2
    (0.655, 0.53),
    (0.70, 0.52),
    (0.94, 0.52),
)


@dataclass(frozen=True)
class BrandStudyGeometry:
    seven_scale: float = 1.34
    pulse_band_start: float = 0.64
    pulse_band_height: float = 0.30
    pulse_waveform_id: str = "reference-pulse-v1"
    pulse_visual_link_to_seven: bool = True
    football_center_x: float = 0.94
    football_center_y: float = 0.54
    football_radius: float = 0.035
    metallic_wordmark: bool = True
    study_only: bool = True
    publication_ready: bool = False

    def __post_init__(self) -> None:
        brand = APPROVED_PUL7SAR_BRAND_MASTER
        brand.assert_safe()
        if self.seven_scale <= 1.0:
            raise ValueError("STUDY_SEVEN_MUST_BE_LARGER_THAN_LETTERS")
        if not 0.58 <= self.pulse_band_start <= 0.76:
            raise ValueError("STUDY_PULSE_MUST_REMAIN_BELOW_WORDMARK")
        if not 0.20 <= self.pulse_band_height <= 0.38:
            raise ValueError("STUDY_PULSE_HEIGHT_OUTSIDE_REFERENCE_FAMILY")
        if self.pulse_waveform_id != "reference-pulse-v1":
            raise ValueError("STUDY_PULSE_MUST_USE_APPROVED_REFERENCE_WAVEFORM")
        if not self.pulse_visual_link_to_seven:
            raise ValueError("STUDY_PULSE_MUST_REMAIN_VISUALLY_LINKED_TO_SEVEN")
        if not 0.86 <= self.football_center_x <= 1.0:
            raise ValueError("STUDY_FOOTBALL_MUST_REMAIN_NEAR_R")
        if not 0.30 <= self.football_center_y <= 0.78:
            raise ValueError("STUDY_FOOTBALL_VERTICAL_POSITION_INVALID")
        if not 0.015 <= self.football_radius <= 0.08:
            raise ValueError("STUDY_FOOTBALL_RADIUS_INVALID")
        if not self.metallic_wordmark:
            raise ValueError("STUDY_WORDMARK_MUST_PRESERVE_METALLIC_TREATMENT")
        if not self.study_only or self.publication_ready:
            raise ValueError("APPROXIMATE_BRAND_GEOMETRY_MAY_NOT_AUTHORIZE_PUBLICATION")


APPROVED_BRAND_STUDY_GEOMETRY = BrandStudyGeometry()
