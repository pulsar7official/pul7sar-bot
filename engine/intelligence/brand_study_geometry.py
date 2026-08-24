"""Study-only geometry for approximating the approved PUL7SAR identity.

This contract exists so visual studies can test composition before exact master
bytes are registered. It is explicitly incapable of authorizing publication.
Relative identity signatures are locked from the approved guide; numerical
placement values are study parameters, not claimed canonical geometry.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.brand_master_contract import APPROVED_PUL7SAR_BRAND_MASTER


@dataclass(frozen=True)
class BrandStudyGeometry:
    seven_scale: float = 1.28
    pulse_band_start: float = 0.70
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
        if not 0.62 <= self.pulse_band_start <= 0.82:
            raise ValueError("STUDY_PULSE_MUST_REMAIN_BELOW_WORDMARK")
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
