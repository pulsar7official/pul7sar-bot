"""Compile strict base-scene instructions from hybrid layer ownership.

The generative model is asked only for what it owns. Exact surfaces, text,
branding, scores, crests and identity-sensitive layers are explicitly reserved
for later deterministic/verified composition.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.hybrid_layer_planner import HybridLayerPlan, LayerSource


@dataclass(frozen=True)
class HybridBaseSceneContract:
    allowed_content: tuple[str, ...]
    reserved_content: tuple[str, ...]
    prompt_suffix: str


class HybridBaseSceneContractCompiler:
    def compile(self, plan: HybridLayerPlan) -> HybridBaseSceneContract:
        source = {item.name: item.source for item in plan.layers}
        allowed = [
            "one continuous editorial scene",
            "lighting and atmospheric depth",
            "crowd or environmental mood when contextually appropriate",
            "non-factual texture",
        ]
        reserved = [
            "all readable text",
            "PUL7SAR branding and wordmark",
            "scores, dates, statistics and exact numbers",
            "team, club and competition marks",
        ]

        if source.get("sport_surface_geometry") is LayerSource.DETERMINISTIC:
            reserved.append("all exact playing-surface geometry and markings")
            allowed.append("an unmarked neutral sport-surface region reserved for deterministic overlay")
        if source.get("hero_identity") is LayerSource.VERIFIED_ASSET:
            reserved.append("recognizable hero identity")
            allowed.append("negative space and lighting that can receive a verified hero asset")

        suffix = (
            "Create only the generative atmosphere layer of one continuous editorial image. "
            "Do not render readable words, letters, numbers, scoreboards, logos, crests, watermarks or PUL7SAR branding. "
        )
        if source.get("sport_surface_geometry") is LayerSource.DETERMINISTIC:
            suffix += (
                "If a playing surface is visible, keep the reserved surface region plain and unmarked: no field/court/rink lines, "
                "no centre circle, no penalty boxes, no goals painted into the surface and no invented sport geometry. "
                "The exact surface will be replaced by deterministic code after generation. "
            )
        if source.get("hero_identity") is LayerSource.VERIFIED_ASSET:
            suffix += "Do not invent a recognizable real-person face; preserve clean composition space for a verified subject layer. "
        suffix += "Keep a single coherent camera, perspective, lighting system and physical world."

        return HybridBaseSceneContract(tuple(allowed), tuple(reserved), suffix)
