"""Enforced Story-to-Generation production bridge for PUL7SAR Phase 18.

Generative/hybrid stories must pass through the story-specific editorial scene
before a provider-neutral GenerationPackage can exist. Generator-bypass stories
are rejected here and must use DirectVisualExecutionPlanner instead.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.assets import AssetBundle
from engine.intelligence.generation_package import GenerationPackage, GenerationPackageCompiler
from engine.intelligence.hybrid_base_scene_contract import HybridBaseSceneContract
from engine.intelligence.layout_planner import PlannedLayout
from engine.intelligence.scene_spec import OriginalSceneSpecification
from engine.intelligence.sports_editorial_generation import SportsEditorialGenerationAugmenter
from engine.intelligence.sports_editorial_scene_spec import SportsEditorialSceneSpecAugmenter
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualDecision


@dataclass(frozen=True)
class SportsEditorialProductionArtifact:
    scene_specification: OriginalSceneSpecification
    generation_package: GenerationPackage
    contract: str = "pul7sar-sports-editorial-production-v1"


class SportsEditorialProductionCompiler:
    def __init__(self) -> None:
        self._scene_spec = SportsEditorialSceneSpecAugmenter()
        self._package = GenerationPackageCompiler()
        self._generation = SportsEditorialGenerationAugmenter()

    def compile(
        self,
        decision: StoryToVisualDecision,
        specification: OriginalSceneSpecification,
        assets: AssetBundle,
        *,
        planned_layout: PlannedLayout | None = None,
        base_scene_contract: HybridBaseSceneContract | None = None,
    ) -> SportsEditorialProductionArtifact:
        if not isinstance(decision, StoryToVisualDecision):
            raise TypeError("decision must be StoryToVisualDecision")
        if not decision.execution_route.generator_required:
            raise ValueError("GENERATOR_BYPASS_STORY_MUST_USE_DIRECT_EXECUTION")

        scene_spec = self._scene_spec.augment(specification, decision.sports_editorial_scene)
        package = self._package.compile(
            scene_spec,
            assets,
            planned_layout=planned_layout,
            base_scene_contract=base_scene_contract,
            visual_grammar=decision.visual_grammar,
        )
        package = self._generation.augment(package, decision.sports_editorial_scene)

        if package.metadata.get("sports_editorial_scene_contract") is None:
            raise RuntimeError("sports editorial scene contract was lost during package compilation")
        if package.metadata.get("brand_identity_id") != decision.sports_editorial_scene.brand_identity_id:
            raise RuntimeError("brand identity contract was lost during package compilation")
        if package.metadata.get("premium_editorial_not_data_card") is not True:
            raise RuntimeError("premium sports editorial policy was lost during package compilation")

        return SportsEditorialProductionArtifact(scene_spec, package)
