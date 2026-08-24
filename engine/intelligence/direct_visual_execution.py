"""Direct non-generative visual execution contracts for PUL7SAR Phase 18.

This path is intentionally independent of GenerationPackage, provider selection,
model backends and GPU jobs. It is used when VisualExecutionRouter proves that an
approved story can be completed with deterministic composition or verified
assets plus deterministic editorial layers.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from engine.intelligence.assets import AssetBundle, AssetRole
from engine.intelligence.layout_planner import PlannedLayout
from engine.intelligence.layout_safety import LayoutRole
from engine.intelligence.visual_execution_route import PixelExecutionRoute, VisualExecutionDecision


class DirectBaseSource(str, Enum):
    PROGRAMMATIC_CANVAS = "programmatic_canvas"
    VERIFIED_ASSET = "verified_asset"


class DirectExecutionStage(str, Enum):
    PREPARE_BASE = "prepare_base"
    APPLY_EXACT_ASSETS = "apply_exact_assets"
    APPLY_EXACT_DATA_GEOMETRY = "apply_exact_data_geometry"
    APPLY_EDITORIAL_TEXT = "apply_editorial_text"
    QUALITY_VERIFY = "quality_verify"
    EXPORT = "export"


@dataclass(frozen=True)
class DirectExecutionStep:
    stage: DirectExecutionStage
    instructions: tuple[str, ...]
    asset_ids: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.stage, DirectExecutionStage):
            raise TypeError("stage must be DirectExecutionStage")
        object.__setattr__(self, "instructions", tuple(self.instructions))
        object.__setattr__(self, "asset_ids", tuple(self.asset_ids))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class DirectVisualExecutionPlan:
    route: PixelExecutionRoute
    base_source: DirectBaseSource
    platform: str
    canvas: str
    accent_hex: str
    steps: tuple[DirectExecutionStep, ...]
    verified_base_asset_ids: tuple[str, ...]
    exact_asset_ids: tuple[str, ...]
    headline: str
    score: Optional[str]
    exact_data: tuple[str, ...]
    deterministic_elements: tuple[str, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "steps", tuple(self.steps))
        object.__setattr__(self, "verified_base_asset_ids", tuple(self.verified_base_asset_ids))
        object.__setattr__(self, "exact_asset_ids", tuple(self.exact_asset_ids))
        object.__setattr__(self, "exact_data", tuple(self.exact_data))
        object.__setattr__(self, "deterministic_elements", tuple(self.deterministic_elements))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


class DirectVisualExecutionPlanner:
    """Build an end-to-end non-generative execution plan.

    No GenerationPackage is accepted or produced here. This guarantees that a
    deterministic/verified-asset story cannot accidentally enter provider/model
    selection merely to satisfy an old interface.
    """

    _EXACT_ROLES = {
        AssetRole.PUL7SAR_LOGO,
        AssetRole.PUL7SAR_PULSE,
        AssetRole.TEAM_CREST,
        AssetRole.COMPETITION_MARK,
        AssetRole.SOCIAL_ICON,
    }

    def compile(
        self,
        execution: VisualExecutionDecision,
        layout: PlannedLayout,
        assets: AssetBundle,
        *,
        headline: str,
        score: Optional[str] = None,
        exact_data: tuple[str, ...] = (),
    ) -> DirectVisualExecutionPlan:
        if not isinstance(execution, VisualExecutionDecision):
            raise TypeError("execution must be VisualExecutionDecision")
        if not isinstance(layout, PlannedLayout):
            raise TypeError("layout must be PlannedLayout")
        if not isinstance(assets, AssetBundle):
            raise TypeError("assets must be AssetBundle")
        if execution.generator_required or execution.provider_selection_allowed:
            raise ValueError("direct visual execution accepts only generator-bypass routes")
        if execution.route not in {PixelExecutionRoute.DETERMINISTIC_ONLY, PixelExecutionRoute.VERIFIED_ASSET_ONLY}:
            raise ValueError("unsupported direct execution route")
        if not isinstance(headline, str) or not headline.strip():
            raise ValueError("headline must be non-empty")
        if score is not None and (not isinstance(score, str) or not score.strip()):
            raise ValueError("score must be non-empty or None")

        exact_data = tuple(str(item).strip() for item in exact_data if str(item).strip())
        verified_assets = tuple(
            asset.asset_id for asset in assets.by_role(AssetRole.VERIFIED_IDENTITY_REFERENCE)
        )
        if execution.route is PixelExecutionRoute.VERIFIED_ASSET_ONLY and not verified_assets:
            raise ValueError("verified-asset route requires at least one VERIFIED_IDENTITY_REFERENCE asset")

        if layout.box_for(LayoutRole.HEADLINE) is None:
            raise ValueError("direct execution requires a headline layout box")
        if score is not None and layout.box_for(LayoutRole.SCORE) is None:
            raise ValueError("score supplied but layout has no score box")

        exact_assets = tuple(
            asset.asset_id for asset in assets.assets if asset.role in self._EXACT_ROLES
        )
        base_source = (
            DirectBaseSource.VERIFIED_ASSET
            if execution.route is PixelExecutionRoute.VERIFIED_ASSET_ONLY
            else DirectBaseSource.PROGRAMMATIC_CANVAS
        )

        prepare_instructions = (
            (
                "Prepare a clean deterministic editorial canvas from code; do not create or request an AI-generated base scene."
                if base_source is DirectBaseSource.PROGRAMMATIC_CANVAS
                else "Place only the approved verified source asset as the editorial base; do not synthesize, redraw or identity-swap the subject."
            ),
        )

        steps = (
            DirectExecutionStep(
                DirectExecutionStage.PREPARE_BASE,
                prepare_instructions,
                asset_ids=verified_assets if base_source is DirectBaseSource.VERIFIED_ASSET else (),
                metadata={"base_source": base_source.value},
            ),
            DirectExecutionStep(
                DirectExecutionStage.APPLY_EXACT_ASSETS,
                ("Composite exact approved brand, crest, competition and social assets without generative reinterpretation.",),
                asset_ids=exact_assets,
            ),
            DirectExecutionStep(
                DirectExecutionStage.APPLY_EXACT_DATA_GEOMETRY,
                (
                    "Render exact data and sport geometry from verified structured values/code only.",
                    "Never infer missing numbers, formations, scores, table positions or geometry from visual appearance.",
                ),
                metadata={
                    "exact_data": exact_data,
                    "deterministic_elements": execution.deterministic_elements,
                },
            ),
            DirectExecutionStep(
                DirectExecutionStage.APPLY_EDITORIAL_TEXT,
                ("Render the approved headline and optional score deterministically using platform-safe layout geometry.",),
                metadata={"headline": headline, "score": score},
            ),
            DirectExecutionStep(
                DirectExecutionStage.QUALITY_VERIFY,
                (
                    "Verify fact lock, asset integrity, identity ownership, geometry/data exactness, neutrality, typography and safe-area compliance.",
                    "No provider provenance or GPU proof is required because no provider was invoked; all direct-layer provenance remains mandatory.",
                ),
            ),
            DirectExecutionStep(
                DirectExecutionStage.EXPORT,
                ("Export only after direct-layer integrity and publication gates pass.",),
            ),
        )

        return DirectVisualExecutionPlan(
            route=execution.route,
            base_source=base_source,
            platform=layout.profile.platform.value,
            canvas=f"{layout.profile.width}x{layout.profile.height}",
            accent_hex=layout.accent_hex,
            steps=steps,
            verified_base_asset_ids=verified_assets,
            exact_asset_ids=exact_assets,
            headline=headline.strip(),
            score=score.strip() if score is not None else None,
            exact_data=exact_data,
            deterministic_elements=execution.deterministic_elements,
            metadata={
                "contract": "pul7sar-direct-visual-execution-v1",
                "generation_package_created": False,
                "provider_selection_performed": False,
                "gpu_job_required": False,
                "generator_bypassed": True,
                "visual_execution_contract": execution.metadata.get("contract"),
                "visual_execution_route": execution.route.value,
            },
        )
