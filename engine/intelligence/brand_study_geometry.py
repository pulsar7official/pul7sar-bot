"""Study-only geometry for approximating the approved PUL7SAR identity.

The pulse is compact and centered around the enlarged 7. It must not read as a
full-width underline beneath PUL7SAR. Numerical values remain study parameters
until exact master geometry is registered.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.brand_master_contract import APPROVED_PUL7SAR_BRAND_MASTER
from engine.intelligence.brand_pulse_signature import APPROVED_PUL7SAR_PULSE_SIGNATURE


REFERENCE_PULSE_WAVEFORM_V2: tuple[tuple[float, float], ...] = (
    (0.215, 0.52),
    (0.315, 0.52),
    (0.345, 0.52),
    (0.365, 0.45),
    (0.385, 0.58),
    (0.415, 0.30),
    (0.445, 0.72),
    (0.475, 0.035),
    (0.515, 0.94),
    (0.555, 0.34),
    (0.590, 0.66),
    (0.620, 0.41),
    (0.650, 0.57),
    (0.685, 0.48),
    (0.715, 0.52),
    (0.790, 0.52),
)


@dataclass(frozen=True)
class BrandStudyGeometry:
    seven_scale: float = 1.36
    pulse_band_start: float = 0.22
    pulse_band_height: float = 0.55
    pulse_waveform_id: str = "reference-pulse-v2-compact"
    pulse_visual_link_to_seven: bool = True
    pulse_full_wordmark_underline: bool = False
    pulse_left_extent: float = 0.215
    pulse_right_extent: float = 0.790
    football_center_x: float = 0.94
    football_center_y: float = 0.54
    football_radius: float = 0.035
    metallic_wordmark: bool = True
    study_only: bool = True
    publication_ready: bool = False

    def __post_init__(self) -> None:
        APPROVED_PUL7SAR_BRAND_MASTER.assert_safe()
        APPROVED_PUL7SAR_PULSE_SIGNATURE.assert_safe()
        if self.seven_scale <= 1.0:
            raise ValueError("STUDY_SEVEN_MUST_BE_LARGER_THAN_LETTERS")
        if not 0.14 <= self.pulse_band_start <= 0.34:
            raise ValueError("STUDY_PULSE_MUST_INTERSECT_LOWER_WORDMARK_ZONE")
        if not 0.44 <= self.pulse_band_height <= 0.68:
            raise ValueError("STUDY_PULSE_HEIGHT_OUTSIDE_REFERENCE_FAMILY")
        if self.pulse_waveform_id != "reference-pulse-v2-compact":
            raise ValueError("STUDY_PULSE_MUST_USE_APPROVED_COMPACT_REFERENCE")
        if not self.pulse_visual_link_to_seven:
            raise ValueError("STUDY_PULSE_MUST_REMAIN_VISUALLY_LINKED_TO_SEVEN")
        if self.pulse_full_wordmark_underline:
            raise ValueError("STUDY_PULSE_MAY_NOT_EXTEND_AS_FULL_WORDMARK_UNDERLINE")
        if not 0.18 <= self.pulse_left_extent <= 0.28:
            raise ValueError("STUDY_PULSE_LEFT_SHOULDER_OUTSIDE_REFERENCE")
        if not 0.74 <= self.pulse_right_extent <= 0.83:
            raise ValueError("STUDY_PULSE_RIGHT_SHOULDER_OUTSIDE_REFERENCE")
        if self.pulse_right_extent - self.pulse_left_extent > 0.62:
            raise ValueError("STUDY_PULSE_IS_TOO_WIDE_FOR_REFERENCE")
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
