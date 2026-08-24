"""Canonical PUL7SAR brand-master semantics approved during Phase 18 visual direction.

This contract deliberately does NOT bind legacy repository logo.png/pulsar7.PNG.
The approved identity is semantic and compositional until exact master geometry
bytes are registered: metallic PUL7SAR wordmark + independently dynamic pulse/7.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BrandMasterPart(str, Enum):
    WORDMARK = "metallic_wordmark"
    PULSE_SEVEN = "pulse_seven_dynamic"


@dataclass(frozen=True)
class BrandMasterContract:
    identity_id: str = "pul7sar-hybrid-adaptive-v1"
    wordmark_text: str = "PUL7SAR"
    wordmark_finish: str = "metallic_silver"
    pulse_seven_dynamic: bool = True
    pulse_seven_uses_verified_story_accent: bool = True
    placement_adaptive: bool = True
    legacy_repo_logo_is_canonical: bool = False
    exact_geometry_required_for_publication: bool = True
    generator_may_invent_brand: bool = False

    def assert_safe(self) -> None:
        if self.wordmark_text != "PUL7SAR":
            raise ValueError("PUL7SAR_BRAND_WORDMARK_CHANGED")
        if self.legacy_repo_logo_is_canonical:
            raise ValueError("LEGACY_REPO_LOGO_MUST_NOT_BECOME_CANONICAL")
        if self.generator_may_invent_brand:
            raise ValueError("GENERATOR_MAY_NOT_INVENT_PUL7SAR_BRAND")
        if not self.exact_geometry_required_for_publication:
            raise ValueError("PUBLICATION_REQUIRES_APPROVED_BRAND_GEOMETRY")


APPROVED_PUL7SAR_BRAND_MASTER = BrandMasterContract()
