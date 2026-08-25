"""Provider-neutral generation package compiler for dry-run inspection."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional

from engine.intelligence.assets import AssetBundle, AssetRole
from engine.intelligence.hybrid_base_scene_contract import HybridBaseSceneContract
from engine.intelligence.layout_planner import PlannedLayout
from engine.intelligence.scene_complexity_policy import SurfaceVisibility
from engine.intelligence.scene_spec import OriginalSceneSpecification
from engine.intelligence.visual_concept_director import VisualConceptDecision
from engine.intelligence.visual_grammar import VisualGrammarDecision


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
    """Compile approved base-scene state while preserving exact-layer ownership.

    The platform name is intentionally absent from the image-model prompt. Exact
    brand identity belongs to deterministic composition; naming the brand inside
    a diffusion prompt can itself encourage hallucinated wordmarks.
    """

    def compile(
        self,
        specification: OriginalSceneSpecification,
        assets: AssetBundle,
        *,
        planned_layout: Optional[PlannedLayout] = None,
        base_scene_contract: Optional[HybridBaseSceneContract] = None,
        visual_grammar: Optional[VisualGrammarDecision] = None,
        visual_concept: Optional[VisualConceptDecision] = None,
    ) -> GenerationPackage:
        if not isinstance(specification, OriginalSceneSpecification):
            raise TypeError("specification must be OriginalSceneSpecification")
        if not isinstance(assets, AssetBundle):
            raise TypeError("assets must be AssetBundle")
        if base_scene_contract is not None and not isinstance(base_scene_contract, HybridBaseSceneContract):
            raise TypeError("base_scene_contract must be HybridBaseSceneContract or None")
        if visual_grammar is not None and not isinstance(visual_grammar, VisualGrammarDecision):
            raise TypeError("visual_grammar must be VisualGrammarDecision or None")
        if visual_concept is not None and not isinstance(visual_concept, VisualConceptDecision):
            raise TypeError("visual_concept must be VisualConceptDecision or None")
        if planned_layout is not None:
            if not isinstance(planned_layout, PlannedLayout):
                raise TypeError("planned_layout must be PlannedLayout or None")
            if planned_layout.profile.platform is not specification.platform:
                raise ValueError("planned layout platform mismatch")
            if planned_layout.profile.width != specification.width or planned_layout.profile.height != specification.height:
                raise ValueError("planned layout canvas mismatch")

        assets.assert_team_crests_exact()
        social_assets = assets.by_role(AssetRole.SOCIAL_ICON)
        identity_assets = assets.by_role(AssetRole.VERIFIED_IDENTITY_REFERENCE)

        identity = specification.identity_reference
        if identity is not None and not identity_assets:
            raise ValueError("identity-required scene needs at least one VERIFIED_IDENTITY_REFERENCE asset")

        prompt_parts = [
            f"Create a premium global sports editorial base scene for {specification.platform.value}.",
            f"Canvas: {specification.width}x{specification.height} ({specification.aspect_ratio}).",
            f"Visual family: {specification.family}.",
            f"Concept: {specification.concept}.",
            f"Environment: {specification.environment}.",
            f"Composition: {specification.composition}.",
            f"Camera: {specification.camera_direction}.",
            f"Mood: {specification.emotional_mood}.",
            (
                "Composition grammar: one single continuous full-bleed editorial image, one physical world, one coherent camera perspective, "
                "and one unified lighting system across the entire canvas. Regional, tactical, institutional, or narrative variety must be integrated "
                "inside that same scene rather than represented as separate pictures."
            ),
            (
                "Never use collage, montage, split-screen, grid, diptych, triptych, contact-sheet, comic-panel, tiled-photo, framed-window, "
                "or image-within-image composition. Never divide the canvas with seams, borders, panel lines, or separate photographic zones."
            ),
        ]
        if specification.subject:
            prompt_parts.append(f"Hero subject: {specification.subject}.")
        if specification.palette_strategy:
            prompt_parts.append(f"Palette strategy: {specification.palette_strategy}.")
        if specification.visual_copy:
            prompt_parts.append(
                "Editorial copy exists for deterministic post-composition; reserve suitable clean space for it but do not render text into the base scene."
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

        if visual_concept is not None:
            prompt_parts.extend((
                f"Story-specific visual concept archetype: {visual_concept.archetype.value}.",
                f"Visual hero direction: {visual_concept.hero}.",
                f"Environmental role: {visual_concept.environment_role}.",
                "Treat this story-specific concept as the picture idea; the renderer is only the execution mechanism and must not replace it with a generic template.",
            ))
            safe_concept_forbidden = tuple(
                motif for motif in visual_concept.forbidden_motifs
                if "pul7sar" not in motif.casefold() and "pulsar" not in motif.casefold()
            )
            if safe_concept_forbidden:
                prompt_parts.append("Concept-specific exclusions: " + "; ".join(safe_concept_forbidden) + ".")

        if visual_grammar is not None:
            prompt_parts.extend((
                f"Art-direction camera language: {visual_grammar.camera_language.value}.",
                f"Fantasy level: {visual_grammar.fantasy_level.value}; keep any symbolism consistent with that restraint.",
                f"Environment direction: {visual_grammar.environment_direction}.",
                f"Lighting direction: {visual_grammar.lighting_direction}.",
                f"Composition direction: {visual_grammar.composition_direction}.",
            ))
            if visual_grammar.surface_visibility is SurfaceVisibility.NONE:
                prompt_parts.append(
                    "Do not make a full pitch, court, rink, track, or stadium surface the visual subject. Keep sport-surface geometry out of the generated base unless incidental and non-structural; prioritize the editorial subject or story-specific environment."
                )
            elif visual_grammar.surface_visibility is SurfaceVisibility.PARTIAL_DETERMINISTIC:
                prompt_parts.append(
                    "Use at most a restrained partial sport-surface context. Do not draw exact field/court/rink markings or tactical geometry; exact sport geometry is added later by deterministic composition."
                )
            elif visual_grammar.surface_visibility is SurfaceVisibility.FULL_DETERMINISTIC:
                prompt_parts.append(
                    "The story requires a full sport-surface layer, but the generator must not draw its exact markings or tactical geometry. Preserve a clean compatible region for deterministic sport-surface composition."
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
                "Respect supplied deterministic layout geometry by keeping all non-hero overlay regions visually calm and free of critical subject detail."
            )
            prompt_parts.append(
                "Use " + planned_layout.accent_hex + " only as a restrained environmental accent when appropriate; the exact platform 7/pulse treatment is added later by deterministic composition."
            )

        prompt_parts.extend((
            "Critical visual elements must stay inside the declared platform safe area.",
            "Generate only a clean photographic/editorial base scene. Do not draw or imitate any platform logo, heartbeat mark, stylized number mark, wordmark, club/team crest, competition mark, social icon, headline typography, score typography, footer text, watermark, signature, or other editorial overlay.",
            "Keep the image fully unbranded: no platform lettering, platform name, substitute wordmark, stylized badge, invented logo or recognizable branding treatment anywhere in the scene.",
            "Keep stadium advertising boards, banners, screens, kit sponsors, and environmental signage visually neutral and unbranded with no legible words, letters, numerals, pseudo-text, fake logos, or readable sponsor marks. Exact branding and typography are added only by deterministic post-composition.",
            "Official marks, contextual 7/pulse tint, and all final editorial typography are deterministic post-composition layers and must remain absent from the AI base scene.",
            "If club/team identity is visually implied through kit or environment, keep it editorially plausible without inventing pseudo-logos or fake text.",
        ))
        if base_scene_contract is not None:
            prompt_parts.append(base_scene_contract.prompt_suffix)
        if social_assets:
            prompt_parts.append(
                "Reserve a compact, visually quiet footer zone for a later platform icon and handle; do not render that footer yourself."
            )

        scene_prompt = " ".join(prompt_parts)
        lowered = scene_prompt.casefold()
        if "pul7sar" in lowered or "pulsar" in lowered:
            raise ValueError("generative base prompt leaked the platform name")

        metadata = {
            "dry_run": True,
            "safe_area": dict(specification.safe_area),
            "profile_version": specification.metadata.get("profile_version"),
            "crop_strategy": specification.metadata.get("crop_strategy"),
            "social_footer_policy": "compact_icon_plus_platform_handle" if social_assets else "none",
            "layout_strategy": planned_layout.strategy if planned_layout else "unspecified",
            "base_scene_overlay_policy": "no_brand_or_editorial_overlays_in_ai_scene",
            "brand_source": "deterministic_dynamic_brand_layer",
            "brand_name_redacted_from_generation_prompt": True,
            "generated_branding_allowed": False,
            "composition_grammar": "single_continuous_scene",
            "multi_panel_layout_allowed": False,
            "hybrid_base_scene_contract": base_scene_contract is not None,
            "reserved_base_scene_content": base_scene_contract.reserved_content if base_scene_contract else (),
            "identity_required": identity is not None,
            "identity_entity_name": identity.entity_name if identity else None,
            "identity_reference_confidence": identity.confidence if identity else None,
            "identity_reference_ids": tuple(asset.asset_id for asset in identity_assets),
            "visual_grammar_contract": visual_grammar.metadata.get("contract") if visual_grammar else None,
            "visual_grammar_provider_agnostic": bool(visual_grammar.metadata.get("provider_agnostic")) if visual_grammar else False,
            "visual_grammar_surface_visibility": visual_grammar.surface_visibility.value if visual_grammar else None,
            "visual_grammar_camera_language": visual_grammar.camera_language.value if visual_grammar else None,
            "visual_grammar_fantasy_level": visual_grammar.fantasy_level.value if visual_grammar else None,
            "visual_grammar_generated_elements": visual_grammar.generated_elements if visual_grammar else (),
            "visual_grammar_deterministic_elements": visual_grammar.deterministic_elements if visual_grammar else (),
            "visual_grammar_forbidden_generated_elements": visual_grammar.forbidden_generated_elements if visual_grammar else (),
            "visual_concept_contract": visual_concept.contract if visual_concept else None,
            "visual_concept_family": visual_concept.family.value if visual_concept else None,
            "visual_concept_archetype": visual_concept.archetype.value if visual_concept else None,
            "visual_concept_provider_agnostic": bool(visual_concept.metadata.get("provider_agnostic")) if visual_concept else False,
            "visual_concept_selected_before_renderer": bool(visual_concept.metadata.get("concept_selected_before_renderer")) if visual_concept else False,
            "visual_concept_asset_priority": visual_concept.asset_priority if visual_concept else (),
            "visual_concept_forbidden_motifs": visual_concept.forbidden_motifs if visual_concept else (),
            "visual_concept_publication_ready": bool(visual_concept.metadata.get("publication_ready")) if visual_concept else False,
        }

        return GenerationPackage(
            platform=specification.platform.value,
            canvas=f"{specification.width}x{specification.height}",
            scene_prompt=scene_prompt,
            negative_constraints=specification.forbidden_visual_elements,
            asset_ids=tuple(asset.asset_id for asset in assets.assets),
            factual_constraints=specification.factual_constraints,
            layout_boxes=layout_boxes,
            accent_hex=accent_hex,
            metadata=metadata,
        )
