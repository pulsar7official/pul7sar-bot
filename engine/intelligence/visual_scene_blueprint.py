"""Compile a selected cross-family archetype into a renderer-facing blueprint.

A blueprint describes visual ownership and spatial behavior without committing to
Pillow, SVG, a local diffusion model, or a paid provider. This is the bridge from
editorial art direction to actual pixel runtimes.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from engine.intelligence.cross_family_visual_system import CrossFamilyVisualDecision


@dataclass(frozen=True)
class VisualSceneBlueprint:
    family: str
    archetype_id: str
    hero_layer: str
    environment_layer: str
    identity_layers: tuple[str, ...]
    exact_layers: tuple[str, ...]
    generated_layers: tuple[str, ...]
    composition_rules: tuple[str, ...]
    forbidden: tuple[str, ...]
    metadata: Mapping[str, object]
    contract: str = "pul7sar-visual-scene-blueprint-v1"

    def __post_init__(self) -> None:
        object.__setattr__(self, "identity_layers", tuple(self.identity_layers))
        object.__setattr__(self, "exact_layers", tuple(self.exact_layers))
        object.__setattr__(self, "generated_layers", tuple(self.generated_layers))
        object.__setattr__(self, "composition_rules", tuple(self.composition_rules))
        object.__setattr__(self, "forbidden", tuple(self.forbidden))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


class VisualSceneBlueprintCompiler:
    CONTRACT = "pul7sar-visual-scene-blueprint-v1"

    _EXACT_HINTS = ("exact ", "verified ", "date", "time", "rank", "positions", "labels", "movement arrows", "zones", "passing lanes", "pressure zones", "role labels")

    def compile(self, decision: CrossFamilyVisualDecision) -> VisualSceneBlueprint:
        a = decision.archetype
        exact = []
        generated = []
        for layer in a.optional_layers:
            if any(hint in layer.casefold() for hint in self._EXACT_HINTS):
                exact.append(layer)
            else:
                generated.append(layer)
        return VisualSceneBlueprint(
            family=decision.family.value,
            archetype_id=a.id,
            hero_layer=a.hero,
            environment_layer=a.spatial_grammar,
            identity_layers=("PUL7SAR approved brand master", "verified entity identity when available"),
            exact_layers=tuple(exact),
            generated_layers=tuple(generated),
            composition_rules=(
                "hero layer must dominate before branding",
                "do not force a full pitch or stadium",
                "do not center every story by default",
                "allow negative space when it strengthens hierarchy",
                "exact identity and readable facts are post-composed deterministically",
                "generated atmosphere must remain one coherent physical/editorial world",
            ),
            forbidden=tuple(dict.fromkeys((*a.forbidden_shortcuts, "empty crest placeholder", "unexplained dot or badge placeholder", "fake readable sponsor text", "decorative pulse outside approved PUL7SAR brand"))),
            metadata={
                "source_contract": decision.contract,
                "selection_seed": decision.seed,
                "anti_repetition_applied": decision.anti_repetition_applied,
                "provider_agnostic": True,
                "renderer_agnostic": True,
            },
        )
