"""Sports-editorial augmentation for provider-neutral generation packages."""
from __future__ import annotations

from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.sports_editorial_scene import SportsEditorialScenePlan


class SportsEditorialGenerationAugmenter:
    """Add story-family art direction without giving generators exact-layer ownership."""

    def augment(self, package: GenerationPackage, scene: SportsEditorialScenePlan) -> GenerationPackage:
        if not isinstance(package, GenerationPackage):
            raise TypeError("package must be GenerationPackage")
        if not isinstance(scene, SportsEditorialScenePlan):
            raise TypeError("scene must be SportsEditorialScenePlan")

        additions = (
            f"Sports editorial family: {scene.family.value}.",
            f"Hero priority: {scene.hero_priority}.",
            f"Story-specific environment: {scene.environment}.",
            f"Story-specific composition: {scene.composition}.",
            "Keep enough negative space for deterministic editorial typography; do not render the headline or supporting copy yourself.",
            "The verified entity accent may influence restrained environmental light/material cues only; never flood the whole scene as a generic template background.",
        )
        prompt = package.scene_prompt + " " + " ".join(additions)
        lowered = prompt.casefold()
        if "pul7sar" in lowered or "pulsar" in lowered:
            raise ValueError("sports editorial generation prompt leaked platform name")

        negatives = tuple(dict.fromkeys((*package.negative_constraints, *scene.forbidden)))
        metadata = {
            **dict(package.metadata),
            "sports_editorial_scene_contract": scene.metadata.get("contract"),
            "sports_editorial_scene_family": scene.family.value,
            "headline_max_words": scene.headline_max_words,
            "supporting_copy_max_words": scene.supporting_copy_max_words,
            "supporting_copy_allowed": scene.allow_supporting_copy,
            "brand_identity_id": scene.brand_identity_id,
            "brand_placement": scene.brand_placement,
            "sports_editorial_generated_ownership": scene.generated_ownership,
            "sports_editorial_deterministic_ownership": scene.deterministic_ownership,
            "premium_editorial_not_data_card": True,
        }
        return GenerationPackage(
            platform=package.platform,
            canvas=package.canvas,
            scene_prompt=prompt,
            negative_constraints=negatives,
            asset_ids=package.asset_ids,
            factual_constraints=package.factual_constraints,
            layout_boxes=package.layout_boxes,
            accent_hex=package.accent_hex,
            metadata=metadata,
        )
