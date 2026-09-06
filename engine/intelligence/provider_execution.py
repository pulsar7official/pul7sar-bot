"""Provider-neutral execution planning for PUL7SAR original scenes.

The execution plan deliberately separates AI scene generation from exact asset
compositing. Image providers create only generator-owned scene content; PUL7SAR-
owned composition keeps logos, crests, social icons, scores, text and exact sport
geometry deterministic and exact.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from engine.intelligence.assets import AssetBundle, AssetRole
from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.provider_capabilities import ProviderFeature, ProviderRequirements
from engine.intelligence.provider_selection import ProviderSelection
from engine.intelligence.visual_execution_route import VisualExecutionDecision


class ExecutionStage(str, Enum):
    GENERATE_BASE_SCENE = "generate_base_scene"
    APPLY_EXACT_ASSETS = "apply_exact_assets"
    APPLY_EDITORIAL_TEXT = "apply_editorial_text"
    QUALITY_VERIFY = "quality_verify"
    EXPORT = "export"


@dataclass(frozen=True)
class ExecutionStep:
    stage: ExecutionStage
    asset_ids: tuple[str, ...] = ()
    instructions: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.stage, ExecutionStage):
            raise TypeError("stage must be ExecutionStage")
        object.__setattr__(self, "asset_ids", tuple(self.asset_ids))
        object.__setattr__(self, "instructions", tuple(self.instructions))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class ProviderExecutionPlan:
    provider_id: str
    provider_requirements: ProviderRequirements
    steps: tuple[ExecutionStep, ...]
    generated_reference_asset_ids: tuple[str, ...]
    post_composite_asset_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.provider_id, str) or not self.provider_id.strip():
            raise ValueError("provider_id must be non-empty")
        object.__setattr__(self, "steps", tuple(self.steps))
        object.__setattr__(self, "generated_reference_asset_ids", tuple(self.generated_reference_asset_ids))
        object.__setattr__(self, "post_composite_asset_ids", tuple(self.post_composite_asset_ids))


class ProviderExecutionPlanner:
    """Compile a provider execution plan only when story routing authorizes one."""

    _POST_COMPOSITE_ROLES = {
        AssetRole.PUL7SAR_LOGO,
        AssetRole.PUL7SAR_PULSE,
        AssetRole.TEAM_CREST,
        AssetRole.COMPETITION_MARK,
        AssetRole.SOCIAL_ICON,
    }

    def build_requirements(self, package: GenerationPackage, assets: AssetBundle, *, aspect_ratio: str) -> ProviderRequirements:
        if not isinstance(package, GenerationPackage):
            raise TypeError("package must be GenerationPackage")
        if not isinstance(assets, AssetBundle):
            raise TypeError("assets must be AssetBundle")
        width, height = self._canvas(package.canvas)

        references = assets.by_role(AssetRole.VERIFIED_IDENTITY_REFERENCE)
        required = {ProviderFeature.TEXT_TO_IMAGE}
        if references:
            required.add(ProviderFeature.REFERENCE_IMAGE)
        if len(references) > 1:
            required.add(ProviderFeature.MULTIPLE_REFERENCES)
        if package.negative_constraints:
            required.add(ProviderFeature.NEGATIVE_INSTRUCTIONS)

        return ProviderRequirements(
            width=width,
            height=height,
            aspect_ratio=aspect_ratio,
            required_features=frozenset(required),
            reference_image_count=len(references),
        )

    def compile(
        self,
        package: GenerationPackage,
        assets: AssetBundle,
        selection: ProviderSelection,
        *,
        aspect_ratio: str,
        execution_route: VisualExecutionDecision,
    ) -> ProviderExecutionPlan:
        if not isinstance(execution_route, VisualExecutionDecision):
            raise TypeError("execution_route must be VisualExecutionDecision")
        if not execution_route.provider_selection_allowed or not execution_route.generator_required:
            raise ValueError(
                "provider execution is forbidden by VisualExecutionRouter; use deterministic/verified-asset pipeline"
            )
        if not execution_route.generated_elements:
            raise ValueError("provider execution requires explicitly declared generator-owned elements")
        if not selection.found or selection.selected_provider_id is None:
            raise ValueError("cannot compile execution plan without an eligible provider")
        requirements = self.build_requirements(package, assets, aspect_ratio=aspect_ratio)

        provider_refs = tuple(
            asset.asset_id
            for asset in assets.by_role(AssetRole.VERIFIED_IDENTITY_REFERENCE)
        )
        post_assets = tuple(
            asset.asset_id
            for asset in assets.assets
            if asset.role in self._POST_COMPOSITE_ROLES
        )

        steps = (
            ExecutionStep(
                ExecutionStage.GENERATE_BASE_SCENE,
                asset_ids=provider_refs,
                instructions=(
                    "Generate only the approved generator-owned scene elements: "
                    + ", ".join(execution_route.generated_elements)
                    + ".",
                    "Do not render official logos, crests, social icons, score typography, final headline text, exact data, or exact sport geometry into the base image.",
                    "Respect factual and negative constraints from the approved generation package.",
                ),
                metadata={
                    "canvas": package.canvas,
                    "layout_boxes": dict(package.layout_boxes),
                    "visual_execution_route": execution_route.route.value,
                    "generator_owned_elements": execution_route.generated_elements,
                    "visual_execution_contract": execution_route.metadata.get("contract"),
                },
            ),
            ExecutionStep(
                ExecutionStage.APPLY_EXACT_ASSETS,
                asset_ids=post_assets,
                instructions=(
                    "Composite exact supplied official assets after base-scene generation.",
                    "Never redraw, reinterpret, or hallucinate PUL7SAR marks, team crests, competition marks, or social icons.",
                ),
            ),
            ExecutionStep(
                ExecutionStage.APPLY_EDITORIAL_TEXT,
                instructions=(
                    "Render approved headline, score, English club/team names, exact data, and compact destination footer deterministically outside the image model.",
                ),
            ),
            ExecutionStep(
                ExecutionStage.QUALITY_VERIFY,
                instructions=(
                    "Verify protected geometry, exact assets, factual constraints, identity, neutrality, text legibility, and platform safe area before export.",
                ),
            ),
            ExecutionStep(
                ExecutionStage.EXPORT,
                instructions=("Export only the platform-specific approved canvas.",),
            ),
        )
        return ProviderExecutionPlan(
            provider_id=selection.selected_provider_id,
            provider_requirements=requirements,
            steps=steps,
            generated_reference_asset_ids=provider_refs,
            post_composite_asset_ids=post_assets,
        )

    @staticmethod
    def _canvas(value: str) -> tuple[int, int]:
        try:
            width_text, height_text = value.lower().split("x", 1)
            width, height = int(width_text), int(height_text)
        except (ValueError, AttributeError) as exc:
            raise ValueError("canvas must use WIDTHxHEIGHT") from exc
        if width <= 0 or height <= 0:
            raise ValueError("canvas dimensions must be positive")
        return width, height
