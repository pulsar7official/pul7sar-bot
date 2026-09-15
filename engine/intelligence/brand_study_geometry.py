"""Study-only geometry approximating the user-approved PUL7SAR identity board.

The reference contains a broad horizontal baseline, while the ACTIVE waveform is
compact around the enlarged 7. Vertical excursion is deliberately constrained;
the earlier study dropped the pulse too far below the wordmark.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.brand_master_contract import APPROVED_PUL7SAR_BRAND_MASTER
from engine.intelligence.brand_pulse_signature import APPROVED_PUL7SAR_PULSE_SIGNATURE


# Normalized against the full brand placement. Long baseline shoulders are real;
# the non-flat waveform stays in the 7 zone and uses reduced vertical excursion.
REFERENCE_PULSE_WAVEFORM_V3: tuple[tuple[float, float], ...] = (
    (0.040, 0.52),
    (0.335, 0.52),
    (0.350, 0.52),
    (0.367, 0.46),
    (0.384, 0.58),
    (0.405, 0.33),
    (0.430, 0.68),
    (0.456, 0.08),
    (0.487, 0.88),
    (0.520, 0.37),
    (0.548, 0.63),
    (0.575, 0.42),
    (0.603, 0.58),
    (0.632, 0.47),
    (0.662, 0.52),
    (0.960, 0.52),
)


@dataclass(frozen=True)
class BrandStudyGeometry:
    seven_scale: float = 1.36
    pulse_band_start: float = 0.33
    pulse_band_height: float = 0.36
    pulse_waveform_id: str = "reference-pulse-v3-measured"
    pulse_visual_link_to_seven: bool = True
    pulse_baseline_left_extent: float = 0.040
    pulse_baseline_right_extent: float = 0.960
    pulse_active_left_extent: float = 0.350
    pulse_active_right_extent: float = 0.662
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
        if not 0.28 <= self.pulse_band_start <= 0.38:
            raise ValueError("STUDY_PULSE_VERTICAL_POSITION_DRIFTED_FROM_REFERENCE")
        if not 0.30 <= self.pulse_band_height <= 0.42:
            raise ValueError("STUDY_PULSE_VERTICAL_EXCURSION_TOO_DEEP")
        if self.pulse_waveform_id != "reference-pulse-v3-measured":
            raise ValueError("STUDY_PULSE_MUST_USE_MEASURED_REFERENCE")
        if not self.pulse_visual_link_to_seven:
            raise ValueError("STUDY_PULSE_MUST_REMAIN_VISUALLY_LINKED_TO_SEVEN")
        if not 0.02 <= self.pulse_baseline_left_extent <= 0.08:
            raise ValueError("STUDY_PULSE_BASELINE_LEFT_DRIFT")
        if not 0.92 <= self.pulse_baseline_right_extent <= 0.98:
            raise ValueError("STUDY_PULSE_BASELINE_RIGHT_DRIFT")
        if not 0.32 <= self.pulse_active_left_extent <= 0.38:
            raise ValueError("STUDY_PULSE_ACTIVE_LEFT_DRIFT")
        if not 0.63 <= self.pulse_active_right_extent <= 0.70:
            raise ValueError("STUDY_PULSE_ACTIVE_RIGHT_DRIFT")
        if self.pulse_active_right_extent - self.pulse_active_left_extent > 0.36:
            raise ValueError("STUDY_ACTIVE_PULSE_TOO_WIDE")
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
