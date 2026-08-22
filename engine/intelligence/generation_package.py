"""Provider-neutral generation package compiler for dry-run inspection."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from engine.intelligence.assets import AssetBundle, AssetRole
from engine.intelligence.scene_spec import OriginalSceneSpecification


@dataclass(frozen=True)
class GenerationPackage:
    platform: str
    canvas: str
    scene_prompt: str
    negative_constraints: tuple[str, ...]
    asset_ids: tuple[str, ...]
    factual_constraints: tuple[str, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("platform", "canvas", "scene_prompt"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        object.__setattr__(self, "negative_constraints", tuple(self.negative_constraints))
        object.__setattr__(self, "asset_ids", tuple(self.asset_ids))
        object.__setattr__(self, "factual_constraints", tuple(self.factual_constraints))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


class GenerationPackageCompiler:
    """Compile a dry-run scene package without calling an image provider."""

    def compile(self, specification: OriginalSceneSpecification, assets: AssetBundle) -> GenerationPackage:
        if not isinstance(specification, OriginalSceneSpecification):
            raise TypeError("specification must be OriginalSceneSpecification")
        if not isinstance(assets, AssetBundle):
            raise TypeError("assets must be AssetBundle")

        assets.assert_brand_ready()
        assets.assert_team_crests_exact()
        social_assets = assets.by_role(AssetRole.SOCIAL_ICON)

        prompt_parts = [
            f"Create a premium PUL7SAR sports editorial scene for {specification.platform.value}.",
            f"Canvas: {specification.width}x{specification.height} ({specification.aspect_ratio}).",
            f"Visual family: {specification.family}.",
            f"Concept: {specification.concept}.",
            f"Environment: {specification.environment}.",
            f"Composition: {specification.composition}.",
            f"Camera: {specification.camera_direction}.",
            f"Mood: {specification.emotional_mood}.",
        ]
        if specification.subject:
            prompt_parts.append(f"Hero subject: {specification.subject}.")
        if specification.palette_strategy:
            prompt_parts.append(f"Palette strategy: {specification.palette_strategy}.")
        if specification.visual_copy:
            prompt_parts.append(f"Approved visual copy: {specification.visual_copy}.")
        if specification.identity_reference is not None:
            identity = specification.identity_reference
            prompt_parts.append(
                "Verified identity context: "
                + ", ".join(
                    value for value in (
                        identity.entity_name, identity.sport, identity.role,
                        identity.gender, identity.nationality, identity.affiliation,
                    ) if value
                )
                + "."
            )

        prompt_parts.extend((
            "Critical visual elements must stay inside the declared platform safe area.",
            "Use the exact supplied PUL7SAR wordmark and official team/competition marks; never redraw, reinterpret, or hallucinate them.",
            "The PUL7SAR wordmark itself remains exact. Only the approved number-7/pulse accent may adapt to the leading entity's primary color when its asset is explicitly marked tintable.",
            "Club/team names shown in artwork must remain in their approved English form unless explicit editorial copy says otherwise.",
        ))
        if social_assets:
            prompt_parts.append(
                "Keep the social footer compact and uncrowded: small official platform icon plus PUL7SAR handle/name only; no long URLs, email address, or dense contact row unless explicitly requested."
            )

        return GenerationPackage(
            platform=specification.platform.value,
            canvas=f"{specification.width}x{specification.height}",
            scene_prompt=" ".join(prompt_parts),
            negative_constraints=specification.forbidden_visual_elements,
            asset_ids=tuple(asset.asset_id for asset in assets.assets),
            factual_constraints=specification.factual_constraints,
            metadata={
                "dry_run": True,
                "safe_area": dict(specification.safe_area),
                "profile_version": specification.metadata.get("profile_version"),
                "crop_strategy": specification.metadata.get("crop_strategy"),
                "social_footer_policy": "compact_icon_plus_pul7sar_handle" if social_assets else "none",
            },
        )
