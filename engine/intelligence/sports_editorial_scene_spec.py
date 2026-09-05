"""Bind Story-to-Visual sports editorial direction into OriginalSceneSpecification."""
from __future__ import annotations

from engine.intelligence.scene_spec import OriginalSceneSpecification
from engine.intelligence.sports_editorial_scene import SportsEditorialScenePlan


class SportsEditorialSceneSpecAugmenter:
    def augment(self, specification: OriginalSceneSpecification, scene: SportsEditorialScenePlan) -> OriginalSceneSpecification:
        if not isinstance(specification, OriginalSceneSpecification):
            raise TypeError("specification must be OriginalSceneSpecification")
        if not isinstance(scene, SportsEditorialScenePlan):
            raise TypeError("scene must be SportsEditorialScenePlan")

        forbidden = tuple(dict.fromkeys((*specification.forbidden_visual_elements, *scene.forbidden)))
        metadata = {
            **dict(specification.metadata),
            "sports_editorial_scene_contract": scene.metadata.get("contract"),
            "sports_editorial_scene_family": scene.family.value,
            "brand_identity_id": scene.brand_identity_id,
            "brand_placement": scene.brand_placement,
            "headline_max_words": scene.headline_max_words,
            "supporting_copy_max_words": scene.supporting_copy_max_words,
            "supporting_copy_allowed": scene.allow_supporting_copy,
            "premium_editorial_not_data_card": True,
        }

        return OriginalSceneSpecification(
            platform=specification.platform,
            width=specification.width,
            height=specification.height,
            aspect_ratio=specification.aspect_ratio,
            safe_area=specification.safe_area,
            family=scene.family.value,
            concept=specification.concept,
            subject=specification.subject,
            identity_reference=specification.identity_reference,
            environment=scene.environment,
            composition=scene.composition,
            camera_direction=specification.camera_direction,
            emotional_mood=specification.emotional_mood,
            palette_strategy=(
                (specification.palette_strategy or "")
                + "; entity color is contextual accent only, never a universal full-background template"
            ).strip("; "),
            required_assets=specification.required_assets,
            visual_copy=specification.visual_copy,
            factual_constraints=specification.factual_constraints,
            forbidden_visual_elements=forbidden,
            metadata=metadata,
        )
