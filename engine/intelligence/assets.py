"""Exact asset contracts for PUL7SAR original-scene generation.

Assets are references, not guessed visual descriptions. A generator may create
background atmosphere, but official brand marks, team crests and social icons
must enter through explicit asset references so they are not hallucinated.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional


class AssetRole(str, Enum):
    PUL7SAR_LOGO = "pul7sar_logo"
    PUL7SAR_PULSE = "pul7sar_pulse"
    TEAM_CREST = "team_crest"
    COMPETITION_MARK = "competition_mark"
    SOCIAL_ICON = "social_icon"
    VERIFIED_IDENTITY_REFERENCE = "verified_identity_reference"
    OTHER = "other"


class AssetTreatment(str, Enum):
    EXACT = "exact"
    TINTABLE_ACCENT = "tintable_accent"
    REFERENCE_ONLY = "reference_only"


@dataclass(frozen=True)
class AssetReference:
    asset_id: str
    role: AssetRole
    treatment: AssetTreatment = AssetTreatment.EXACT
    display_name: Optional[str] = None
    source_reference: Optional[str] = None
    accent_color: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.asset_id, str) or not self.asset_id.strip():
            raise ValueError("asset_id must be non-empty")
        if not isinstance(self.role, AssetRole):
            raise TypeError("role must be AssetRole")
        if not isinstance(self.treatment, AssetTreatment):
            raise TypeError("treatment must be AssetTreatment")
        for name in ("display_name", "source_reference", "accent_color"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be non-empty or None")
        if self.accent_color is not None and self.treatment is not AssetTreatment.TINTABLE_ACCENT:
            raise ValueError("accent_color is only valid for TINTABLE_ACCENT assets")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


class AssetBundle:
    """Validate the exact assets required by one PUL7SAR scene."""

    def __init__(self, assets: tuple[AssetReference, ...]):
        assets = tuple(assets)
        ids = [asset.asset_id for asset in assets]
        if len(ids) != len(set(ids)):
            raise ValueError("asset_id values must be unique")
        self._assets = assets

    @property
    def assets(self) -> tuple[AssetReference, ...]:
        return self._assets

    def by_role(self, role: AssetRole) -> tuple[AssetReference, ...]:
        return tuple(asset for asset in self._assets if asset.role is role)

    def assert_brand_ready(self) -> None:
        logos = self.by_role(AssetRole.PUL7SAR_LOGO)
        pulses = self.by_role(AssetRole.PUL7SAR_PULSE)
        if len(logos) != 1:
            raise ValueError("exactly one PUL7SAR logo asset is required")
        if logos[0].treatment is not AssetTreatment.EXACT:
            raise ValueError("PUL7SAR wordmark/logo must remain exact")
        if len(pulses) != 1:
            raise ValueError("exactly one PUL7SAR pulse asset is required")
        if pulses[0].treatment not in {AssetTreatment.EXACT, AssetTreatment.TINTABLE_ACCENT}:
            raise ValueError("PUL7SAR pulse must be exact or tintable accent")

    def assert_team_crests_exact(self) -> None:
        for crest in self.by_role(AssetRole.TEAM_CREST):
            if crest.treatment is not AssetTreatment.EXACT:
                raise ValueError("team crests must be exact assets and may not be regenerated")
