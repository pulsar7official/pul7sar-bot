"""Canonical PUL7SAR brand-master semantics approved during Phase 18.

Legacy repository rasters are not canonical. The approved identity semantics are
locked from the user-approved visual guide while exact master geometry bytes remain
separately checksum-gated for publication.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BrandMasterPart(str, Enum):
    WORDMARK = "metallic_wordmark"
    PULSE_SEVEN = "pulse_seven_dynamic"
    FOOTBALL_SIGNATURE = "small_football_near_r"


@dataclass(frozen=True)
class BrandMasterContract:
    identity_id: str = "pul7sar-hybrid-adaptive-v1"
    wordmark_text: str = "PUL7SAR"
    wordmark_finish: str = "metallic_silver_fixed"
    seven_larger_than_letters: bool = True
    pulse_topology: str = "integrated_signature_centered_on_seven"
    pulse_long_baseline_allowed: bool = True
    pulse_active_waveform_compact_around_seven: bool = True
    small_football_near_r: bool = True
    pulse_seven_dynamic: bool = True
    pulse_seven_uses_verified_story_accent: bool = True
    only_pulse_and_seven_are_tintable: bool = True
    preferred_brand_zone: str = "lower_composition_when_clear"
    placement_adaptive: bool = True
    legacy_repo_logo_is_canonical: bool = False
    exact_geometry_required_for_publication: bool = True
    generator_may_invent_brand: bool = False

    def assert_safe(self) -> None:
        if self.wordmark_text != "PUL7SAR":
            raise ValueError("PUL7SAR_BRAND_WORDMARK_CHANGED")
        if self.wordmark_finish != "metallic_silver_fixed":
            raise ValueError("PUL7SAR_METALLIC_WORDMARK_MUST_REMAIN_FIXED")
        if not self.seven_larger_than_letters:
            raise ValueError("PUL7SAR_SEVEN_SIZE_SIGNATURE_CHANGED")
        if self.pulse_topology != "integrated_signature_centered_on_seven":
            raise ValueError("PUL7SAR_PULSE_TOPOLOGY_CHANGED")
        if not self.pulse_long_baseline_allowed:
            raise ValueError("PUL7SAR_REFERENCE_BASELINE_MUST_REMAIN_AVAILABLE")
        if not self.pulse_active_waveform_compact_around_seven:
            raise ValueError("PUL7SAR_ACTIVE_PULSE_MUST_REMAIN_COMPACT_AROUND_SEVEN")
        if not self.small_football_near_r:
            raise ValueError("PUL7SAR_FOOTBALL_SIGNATURE_MISSING")
        if not self.only_pulse_and_seven_are_tintable:
            raise ValueError("PUL7SAR_WORDMARK_MUST_NOT_BE_TINTED")
        if self.legacy_repo_logo_is_canonical:
            raise ValueError("LEGACY_REPO_LOGO_MUST_NOT_BECOME_CANONICAL")
        if self.generator_may_invent_brand:
            raise ValueError("GENERATOR_MAY_NOT_INVENT_PUL7SAR_BRAND")
        if not self.exact_geometry_required_for_publication:
            raise ValueError("PUBLICATION_REQUIRES_APPROVED_BRAND_GEOMETRY")


APPROVED_PUL7SAR_BRAND_MASTER = BrandMasterContract()
