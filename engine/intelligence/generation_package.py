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
    """Compile approved scene state while preserving identity provenance."""

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
        identity_assets = assets.by_role(AssetRole.VERIFIED_IDENTITY_REFERENCE)

        identity = specification.identity_reference
        if identity is not None and not identity_assets:
            raise ValueError("identity-required scene needs at least one VERIFIED_IDENTITY_REFERENCE asset")

        prompt_parts = [
            f"Create a premium PUL7SAR sports editorial base scene for {specification.platform.value}.",
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
            prompt_parts.append(
                "Editorial copy exists for deterministic post-composition; reserve suitable clean space for it but do not render the text into the base scene."
            )
        if identity is not None:
            prompt_parts.append(
                "Verified identity context: "
                + ", ".join(
                    value for value in (
                        identity.entity_name,
                        identity.sport,
                        identity.role,
                        identity.gender,
                        identity.nationality,
                        identity.affiliation,
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
                    "x": box.x,
                    "y": box.y,
                    "width": box.width,
                    "height": box.height,
                }
            prompt_parts.append(
                "Respect the supplied deterministic layout geometry by keeping all non-hero overlay regions visually calm and free of critical subject detail."
            )
            prompt_parts.append(
                "Use " + planned_layout.accent_hex + " only as a contextual environmental accent when visually appropriate; the exact PUL7SAR number-7/pulse treatment is added later by deterministic composition."
            )

        prompt_parts.extend((
            "Critical visual elements must stay inside the declared platform safe area.",
            "Generate only the clean photographic/editorial base scene. Do not draw or imitate the PUL7SAR logo, heartbeat mark, club/team crests, competition marks, social icons, headline typography, score typography, or footer text.",
            "Official marks, PUL7SAR branding, the contextual number-7/pulse tint, and all final editorial typography are deterministic post-composition assets and must remain absent from the AI base scene.",
            "If a club/team identity is visually implied through kit or environment, keep it editorially plausible without inventing unreadable pseudo-logos or fake text.",
        ))
        if social_assets:
            prompt_parts.append(
                "Reserve a compact, visually quiet footer zone for a later small platform icon plus PUL7SAR handle; do not render that footer yourself."
            )

        metadata = {
            "dry_run": True,
            "safe_area": dict(specification.safe_area),
            "profile_version": specification.metadata.get("profile_version"),
            "crop_strategy": specification.metadata.get("crop_strategy"),
            "social_footer_policy": "compact_icon_plus_pul7sar_handle" if social_assets else "none",
            "layout_strategy": planned_layout.strategy if planned_layout else "unspecified",
            "base_scene_overlay_policy": "no_brand_or_editorial_overlays_in_ai_scene",
            "identity_required": identity is not None,
            "identity_entity_name": identity.entity_name if identity else None,
            "identity_reference_confidence": identity.confidence if identity else None,
            "identity_reference_ids": tuple(asset.asset_id for asset in identity_assets),
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
