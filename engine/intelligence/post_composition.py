"""Deterministic post-generation composition and quality contracts.

This module owns the layer after AI base-scene generation. Official assets and
editorial text are placed by PUL7SAR, not hallucinated by an image model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from engine.intelligence.assets import AssetBundle, AssetRole, AssetTreatment
from engine.intelligence.generation_package import GenerationPackage


class CompositionRole(str, Enum):
    BRAND_LOGO = "brand_logo"
    BRAND_PULSE = "brand_pulse"
    TEAM_CREST = "team_crest"
    COMPETITION_MARK = "competition_mark"
    HEADLINE = "headline"
    SCORE = "score"
    SOCIAL_FOOTER = "social_footer"


@dataclass(frozen=True)
class AssetIntegrityRecord:
    asset_id: str
    sha256: str

    def __post_init__(self) -> None:
        if not isinstance(self.asset_id, str) or not self.asset_id.strip():
            raise ValueError("asset_id must be non-empty")
        digest = self.sha256.strip().lower() if isinstance(self.sha256, str) else ""
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise ValueError("sha256 must be a 64-character hexadecimal digest")
        object.__setattr__(self, "sha256", digest)


@dataclass(frozen=True)
class CompositionElement:
    role: CompositionRole
    box_role: str
    asset_id: Optional[str] = None
    text: Optional[str] = None
    tint_hex: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.role, CompositionRole):
            raise TypeError("role must be CompositionRole")
        if not isinstance(self.box_role, str) or not self.box_role.strip():
            raise ValueError("box_role must be non-empty")
        if self.asset_id is None and self.text is None:
            raise ValueError("composition element requires asset_id or text")
        if self.asset_id is not None and (not isinstance(self.asset_id, str) or not self.asset_id.strip()):
            raise ValueError("asset_id must be non-empty or None")
        if self.text is not None and (not isinstance(self.text, str) or not self.text.strip()):
            raise ValueError("text must be non-empty or None")
        if self.tint_hex is not None:
            value = self.tint_hex.strip().upper()
            if not value.startswith("#"):
                value = "#" + value
            if len(value) != 7 or any(ch not in "0123456789ABCDEF" for ch in value[1:]):
                raise ValueError("tint_hex must be #RRGGBB")
            object.__setattr__(self, "tint_hex", value)
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class PostCompositionPlan:
    platform: str
    canvas: str
    elements: tuple[CompositionElement, ...]
    integrity_records: tuple[AssetIntegrityRecord, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.platform, str) or not self.platform.strip():
            raise ValueError("platform must be non-empty")
        if not isinstance(self.canvas, str) or not self.canvas.strip():
            raise ValueError("canvas must be non-empty")
        object.__setattr__(self, "elements", tuple(self.elements))
        object.__setattr__(self, "integrity_records", tuple(self.integrity_records))


@dataclass(frozen=True)
class CompositionQualityDecision:
    allowed: bool
    failures: tuple[str, ...] = ()


def _normalized_sha256(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    digest = value.strip().lower()
    if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
        return None
    return digest


class PostCompositionPlanner:
    """Build deterministic placement instructions from an approved package."""

    _ASSET_ROLE_TO_COMPOSITION = {
        AssetRole.PUL7SAR_LOGO: (CompositionRole.BRAND_LOGO, "logo"),
        AssetRole.PUL7SAR_PULSE: (CompositionRole.BRAND_PULSE, "logo"),
        AssetRole.TEAM_CREST: (CompositionRole.TEAM_CREST, "crest"),
        AssetRole.COMPETITION_MARK: (CompositionRole.COMPETITION_MARK, "crest"),
        AssetRole.SOCIAL_ICON: (CompositionRole.SOCIAL_FOOTER, "social_footer"),
    }

    def compile(
        self,
        package: GenerationPackage,
        assets: AssetBundle,
        *,
        headline: Optional[str] = None,
        score: Optional[str] = None,
        social_handle: Optional[str] = None,
        integrity_records: tuple[AssetIntegrityRecord, ...] = (),
    ) -> PostCompositionPlan:
        if not isinstance(package, GenerationPackage):
            raise TypeError("package must be GenerationPackage")
        if not isinstance(assets, AssetBundle):
            raise TypeError("assets must be AssetBundle")
        assets.assert_brand_ready()
        assets.assert_team_crests_exact()

        elements: list[CompositionElement] = []
        for asset in assets.assets:
            mapped = self._ASSET_ROLE_TO_COMPOSITION.get(asset.role)
            if mapped is None:
                continue
            role, box_role = mapped
            if box_role not in package.layout_boxes:
                continue
            tint = None
            if asset.role is AssetRole.PUL7SAR_PULSE and asset.treatment is AssetTreatment.TINTABLE_ACCENT:
                tint = package.accent_hex
            elements.append(
                CompositionElement(
                    role=role,
                    box_role=box_role,
                    asset_id=asset.asset_id,
                    tint_hex=tint,
                )
            )

        if headline is not None:
            if "headline" not in package.layout_boxes:
                raise ValueError("headline text supplied but headline box is absent")
            elements.append(CompositionElement(CompositionRole.HEADLINE, "headline", text=headline))
        if score is not None:
            if "score" not in package.layout_boxes:
                raise ValueError("score supplied but score box is absent")
            elements.append(CompositionElement(CompositionRole.SCORE, "score", text=score))
        if social_handle is not None:
            if "social_footer" not in package.layout_boxes:
                raise ValueError("social handle supplied but footer box is absent")
            elements.append(CompositionElement(CompositionRole.SOCIAL_FOOTER, "social_footer", text=social_handle))

        return PostCompositionPlan(
            platform=package.platform,
            canvas=package.canvas,
            elements=tuple(elements),
            integrity_records=integrity_records,
        )


class PostCompositionQualityGate:
    """Fail closed before export when deterministic composition is incomplete."""

    def evaluate(
        self,
        package: GenerationPackage,
        assets: AssetBundle,
        plan: PostCompositionPlan,
    ) -> CompositionQualityDecision:
        failures: list[str] = []
        if plan.platform != package.platform:
            failures.append("composition platform does not match generation package")
        if plan.canvas != package.canvas:
            failures.append("composition canvas does not match generation package")

        asset_map = {asset.asset_id: asset for asset in assets.assets}
        integrity_map = {record.asset_id: record.sha256 for record in plan.integrity_records}
        if len(integrity_map) != len(plan.integrity_records):
            failures.append("duplicate asset integrity record")

        # The approved PUL7SAR logo may never be accepted as a symbolic asset ID
        # alone. Final composition requires a declared immutable digest and a
        # matching runtime integrity record for the exact logo bytes.
        brand_logos = assets.by_role(AssetRole.PUL7SAR_LOGO)
        if len(brand_logos) != 1:
            failures.append("exactly one declared PUL7SAR logo asset is required")
        else:
            logo_asset = brand_logos[0]
            expected_logo_sha = _normalized_sha256(logo_asset.metadata.get("sha256"))
            if expected_logo_sha is None:
                failures.append(f"missing valid declared checksum for PUL7SAR logo: {logo_asset.asset_id}")
            else:
                actual_logo_sha = integrity_map.get(logo_asset.asset_id)
                if actual_logo_sha is None:
                    failures.append(f"missing integrity record for PUL7SAR logo: {logo_asset.asset_id}")
                elif actual_logo_sha != expected_logo_sha:
                    failures.append(f"asset checksum mismatch: {logo_asset.asset_id}")

        for element in plan.elements:
            if element.box_role not in package.layout_boxes:
                failures.append(f"missing approved layout box: {element.box_role}")
            if element.asset_id is not None:
                asset = asset_map.get(element.asset_id)
                if asset is None:
                    failures.append(f"unknown asset in composition plan: {element.asset_id}")
                    continue
                expected = _normalized_sha256(asset.metadata.get("sha256"))
                if expected and asset.role is not AssetRole.PUL7SAR_LOGO:
                    actual = integrity_map.get(element.asset_id)
                    if actual is None:
                        failures.append(f"missing integrity record for asset: {element.asset_id}")
                    elif expected != actual:
                        failures.append(f"asset checksum mismatch: {element.asset_id}")

        logos = [item for item in plan.elements if item.role is CompositionRole.BRAND_LOGO]
        if len(logos) != 1:
            failures.append("exactly one PUL7SAR logo must be composited")

        for item in plan.elements:
            if item.role is CompositionRole.TEAM_CREST and item.tint_hex is not None:
                failures.append("team crest may not be tinted")
            if item.role is CompositionRole.BRAND_LOGO and item.tint_hex is not None:
                failures.append("PUL7SAR wordmark/logo may not be tinted")

        return CompositionQualityDecision(not failures, tuple(failures))

    def assert_allowed(self, package: GenerationPackage, assets: AssetBundle, plan: PostCompositionPlan) -> None:
        decision = self.evaluate(package, assets, plan)
        if not decision.allowed:
            raise ValueError("post-composition quality gate failed: " + "; ".join(decision.failures))
