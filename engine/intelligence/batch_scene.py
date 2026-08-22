"""Compile one approved story concept into platform-specific dry-run packages."""

from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.assets import AssetBundle
from engine.intelligence.concept_director import ConceptBrief, ProposedConcept
from engine.intelligence.generation_package import GenerationPackage, GenerationPackageCompiler
from engine.intelligence.models import LockedClaim, VisualIntent
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.scene_spec import OriginalSceneSpecification, SceneSpecCompiler


@dataclass(frozen=True)
class PlatformScenePackage:
    specification: OriginalSceneSpecification
    generation_package: GenerationPackage


class MultiPlatformSceneCompiler:
    """Art-direct one story separately for each requested publishing surface."""

    def __init__(
        self,
        *,
        registry: PlatformProfileRegistry | None = None,
        scene_compiler: SceneSpecCompiler | None = None,
        package_compiler: GenerationPackageCompiler | None = None,
    ) -> None:
        self._registry = registry or PlatformProfileRegistry()
        self._scene_compiler = scene_compiler or SceneSpecCompiler()
        self._package_compiler = package_compiler or GenerationPackageCompiler()

    def compile(
        self,
        *,
        platforms: tuple[SocialPlatform, ...],
        intent: VisualIntent,
        concept_brief: ConceptBrief,
        proposed_concept: ProposedConcept,
        assets: AssetBundle,
        locked_claims: tuple[LockedClaim, ...] = (),
        extra_forbidden_elements: tuple[str, ...] = (),
    ) -> tuple[PlatformScenePackage, ...]:
        platforms = tuple(platforms)
        if not platforms:
            raise ValueError("at least one platform is required")
        if len(platforms) != len(set(platforms)):
            raise ValueError("platforms must be unique")

        output: list[PlatformScenePackage] = []
        asset_ids = tuple(asset.asset_id for asset in assets.assets)
        for platform in platforms:
            profile = self._registry.get(platform)
            specification = self._scene_compiler.compile(
                profile=profile,
                intent=intent,
                concept_brief=concept_brief,
                proposed_concept=proposed_concept,
                locked_claims=locked_claims,
                required_assets=asset_ids,
                extra_forbidden_elements=extra_forbidden_elements,
            )
            package = self._package_compiler.compile(specification, assets)
            output.append(PlatformScenePackage(specification, package))
        return tuple(output)
