"""PUL7SAR brand semantics for exact assets and tintable accents."""

from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.assets import AssetBundle, AssetRole, AssetTreatment
from engine.intelligence.entity_theme import EntityTheme


@dataclass(frozen=True)
class BrandPlacementPlan:
    logo_asset_id: str
    pulse_asset_id: str
    pulse_tint_hex: str | None
    preserve_wordmark_exact: bool = True
    preserve_team_crests_exact: bool = True


class BrandPlacementPlanner:
    """Resolve exact wordmark + independently tintable pulse/7 semantics."""

    def plan(self, assets: AssetBundle, theme: EntityTheme) -> BrandPlacementPlan:
        if not isinstance(assets, AssetBundle):
            raise TypeError("assets must be AssetBundle")
        if not isinstance(theme, EntityTheme):
            raise TypeError("theme must be EntityTheme")

        assets.assert_brand_ready()
        assets.assert_team_crests_exact()
        logo = assets.by_role(AssetRole.PUL7SAR_LOGO)[0]
        pulse = assets.by_role(AssetRole.PUL7SAR_PULSE)[0]

        if logo.treatment is not AssetTreatment.EXACT:
            raise ValueError("PUL7SAR wordmark must remain exact")

        tint = None
        if pulse.treatment is AssetTreatment.TINTABLE_ACCENT:
            tint = theme.accent_hex
        elif pulse.treatment is not AssetTreatment.EXACT:
            raise ValueError("PUL7SAR pulse must be exact or tintable accent")

        return BrandPlacementPlan(
            logo_asset_id=logo.asset_id,
            pulse_asset_id=pulse.asset_id,
            pulse_tint_hex=tint,
        )
