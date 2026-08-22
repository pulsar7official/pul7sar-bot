"""Provider-neutral generation package compiler for dry-run inspection."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional

from engine.intelligence.assets import AssetBundle, AssetRole
from engine.intelligence.layout_planner import PlannedLayout
from engine.intelligence.scene_spec import OriginalSceneSpecification


@dataclass(frozen=True)
class GenerationPackage:
    platform: str
    canvas: str
    scene_prompt: str
    negative_constraints: tuple[str, ...]
    asset_ids: tuple[str, ...]
    factual_constraints: tuple[str, ...]
    layout_boxes: Mapping[str, Mapping[str, int]] = field(default_factory=dict)
    accent_hex: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("platform", "canvas", "scene_prompt"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        if self.accent_hex is not None and (
            not isinstance(self.accent_hex, str) or not self.accent_hex.startswith("#")
        ):
            raise ValueError("accent_hex must be #RRGGBB or None")
        normalized_layout = {
            str(role): MappingProxyType(dict(box)) for role, box in dict(self.layout_boxes).items()
        }
        object.__setattr__(self, "negative_constraints", tuple(self.negative_constraints))
        object.__setattr__(self, "asset_ids", tuple(self.asset_ids))
        object.__setattr__(self, "factual_constraints", tuple(self.factual_constraints))
        object.__setattr__(self, "layout_boxes", MappingProxyType(normalized_layout))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


class GenerationPackageCompiler:
    """Compile a dry-run scene package without calling an image provider."""

    def compile(
        self,
        specification: OriginalSceneSpecification,
        assets: AssetBundle,
        *,
        planned_layout: Optional[PlannedLayout] = None,
    ) -> GenerationPackage:
        if not isinstance(specification, OriginalSceneSpecification):
            raise TypeError("specification must be OriginalSceneSpecification")
        if not isinstance(assets, AssetBundle):
            raise TypeError("assets must be AssetBundle")
        if planned_layout is not None:
            if not isinstance(planned_layout, PlannedLayout):
                raise TypeError("planned_layout must be PlannedLayout or None")
            if planned_layout.profile.platform is not specification.platform:
                raise ValueError("planned layout platform mismatch")
            if planned_layout.profile.width != specification.width or planned_layout.profile.height != specification.height:
                raise ValueError("planned layout canvas mismatch")

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

        layout_boxes: dict[str, dict[str, int]] = {}
        accent_hex = None
        if planned_layout is not None:
            accent_hex = planned_layout.accent_hex
            for box in planned_layout.boxes:
                layout_boxes[box.role.value] = {
                    "x": box.x, "y": box.y, "width": box.width, "height": box.height,
                }
            prompt_parts.append("Follow the supplied deterministic layout geometry exactly for protected editorial elements.")
            prompt_parts.append("Accent color for the approved number-7/pulse element: " + planned_layout.accent_hex + ".")

        prompt_parts.extend((
            "Critical visual elements must stay inside the declared platform safe area.",
            "Use the exact supplied PUL7SAR wordmark and official team/competition marks; never redraw, reinterpret, or hallucinate them.",
            "The PUL7SAR wordmark itself remains exact. Only the approved number-7/pulse accent may adapt to the leading entity's primary color when its asset is explicitly marked tintable.",
            "Club/team names shown in artwork must remain in their approved English form unless explicit editorial copy says otherwise.",
        ))
        if social_assets:
            prompt_parts.append("Keep the social footer compact and uncrowded: small official platform icon plus PUL7SAR handle/name only; no long URLs, email address, or dense contact row unless explicitly requested.")

        identity = specification.identity_reference
        metadata = {
            "dry_run": True,
            "safe_area": dict(specification.safe_area),
            "profile_version": specification.metadata.get("profile_version"),
            "crop_strategy": specification.metadata.get("crop_strategy"),
            "social_footer_policy": "compact_icon_plus_pul7sar_handle" if social_assets else "none",
            "layout_strategy": planned_layout.strategy if planned_layout else "unspecified",
            "identity_required": identity is not None,
            "identity_entity_name": identity.entity_name if identity else None,
            "identity_reference_confidence": identity.confidence if identity else None,
        }

        return GenerationPackage(
            platform=specification.platform.value,
            canvas=f"{specification.width}x{specification.height}",
            scene_prompt=" ".join(prompt_parts),
            negative_constraints=specification.forbidden_visual_elements,
            asset_ids=tuple(asset.asset_id for asset in assets.assets),
            factual_constraints=specification.factual_constraints,
            layout_boxes=layout_boxes,
            accent_hex=accent_hex,
            metadata=metadata,
        )
