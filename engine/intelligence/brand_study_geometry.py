"""Study-only geometry for approximating the approved PUL7SAR identity.

The pulse is not a footer decoration. In the approved reference family its long
baseline lives immediately beneath the metallic wordmark while the central beat
rises into the enlarged 7 zone and drops below the baseline before recovering.
Numerical values remain study parameters until exact master geometry is supplied.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.brand_master_contract import APPROVED_PUL7SAR_BRAND_MASTER
from engine.intelligence.brand_pulse_signature import APPROVED_PUL7SAR_PULSE_SIGNATURE


REFERENCE_PULSE_WAVEFORM_V1: tuple[tuple[float, float], ...] = (
    (0.035, 0.52),
    (0.305, 0.52),
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
    (0.720, 0.52),
    (0.965, 0.52),
)


@dataclass(frozen=True)
class BrandStudyGeometry:
    seven_scale: float = 1.36
    pulse_band_start: float = 0.22
    pulse_band_height: float = 0.55
    pulse_waveform_id: str = "reference-pulse-v1"
    pulse_visual_link_to_seven: bool = True
    pulse_baseline_under_wordmark: bool = True
    football_center_x: float = 0.94
    football_center_y: float = 0.54
    football_radius: float = 0.035
    metallic_wordmark: bool = True
    study_only: bool = True
    publication_ready: bool = False

    def __post_init__(self) -> None:
        brand = APPROVED_PUL7SAR_BRAND_MASTER
        brand.assert_safe()
        APPROVED_PUL7SAR_PULSE_SIGNATURE.assert_safe()
        if self.seven_scale <= 1.0:
            raise ValueError("STUDY_SEVEN_MUST_BE_LARGER_THAN_LETTERS")
        if not 0.14 <= self.pulse_band_start <= 0.34:
            raise ValueError("STUDY_PULSE_MUST_INTERSECT_LOWER_WORDMARK_ZONE")
        if not 0.44 <= self.pulse_band_height <= 0.68:
            raise ValueError("STUDY_PULSE_HEIGHT_OUTSIDE_REFERENCE_FAMILY")
        if self.pulse_waveform_id != "reference-pulse-v1":
            raise ValueError("STUDY_PULSE_MUST_USE_APPROVED_REFERENCE_WAVEFORM")
        if not self.pulse_visual_link_to_seven:
            raise ValueError("STUDY_PULSE_MUST_REMAIN_VISUALLY_LINKED_TO_SEVEN")
        if not self.pulse_baseline_under_wordmark:
            raise ValueError("STUDY_PULSE_BASELINE_MUST_RUN_UNDER_WORDMARK")
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
