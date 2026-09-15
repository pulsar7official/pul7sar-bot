"""Final structural gate before any Phase 18 family renderer may execute.

This gate is intentionally pixel-agnostic. It proves that story-family selection,
platform composition, layer ownership and deterministic brand ordering agree.
Passing this gate authorizes rendering work only; it never authorizes publication.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from engine.intelligence.family_render_plan import FamilyRenderPlan, RenderOwner
from engine.intelligence.platform_editorial_composition import PlatformEditorialComposition


class FamilyRenderReadiness(str, Enum):
    BLOCKED = "blocked"
    RENDER_STRUCTURE_READY = "render_structure_ready"


@dataclass(frozen=True)
class FamilyRenderReadinessDecision:
    status: FamilyRenderReadiness
    render_allowed: bool
    publication_allowed: bool
    failures: tuple[str, ...]
    contract: str = "pul7sar-family-render-readiness-v1"


class FamilyRenderReadinessGate:
    PLATFORM_CONTRACT = "pul7sar-platform-editorial-composition-v4"
    RENDER_PLAN_CONTRACT = "pul7sar-family-render-plan-v1"

    def evaluate(
        self,
        composition: PlatformEditorialComposition,
        render_plan: FamilyRenderPlan,
    ) -> FamilyRenderReadinessDecision:
        if not isinstance(composition, PlatformEditorialComposition):
            raise TypeError("composition must be PlatformEditorialComposition")
        if not isinstance(render_plan, FamilyRenderPlan):
            raise TypeError("render_plan must be FamilyRenderPlan")
        failures: list[str] = []

        if composition.contract != self.PLATFORM_CONTRACT:
            failures.append("platform composition contract is stale")
        if render_plan.contract != self.RENDER_PLAN_CONTRACT:
            failures.append("family render plan contract is stale")
        if composition.family is not render_plan.family:
            failures.append("composition and render plan story families differ")
        if composition.inherits_transfer_layout:
            failures.append("story family illegally inherits transfer layout")
        if render_plan.publication_ready:
            failures.append("render plan may not self-authorize publication")
        if render_plan.readable_text_generator_owned:
            failures.append("readable text is generator-owned")
        if render_plan.exact_data_generator_owned:
            failures.append("exact data is generator-owned")
        if render_plan.exact_identity_generator_owned:
            failures.append("exact identity is generator-owned")
        if not render_plan.brand_last_before_qa:
            failures.append("brand is not last exact layer before QA")
        if len(render_plan.stages) < 2:
            failures.append("render plan has insufficient stages")
        else:
            brand, qa = render_plan.stages[-2], render_plan.stages[-1]
            if brand.stage_id != "pul7sar_brand" or brand.owner is not RenderOwner.DETERMINISTIC or not brand.exact:
                failures.append("PUL7SAR brand stage is not exact deterministic")
            if qa.stage_id != "visual_qa" or qa.owner is not RenderOwner.DETERMINISTIC:
                failures.append("visual QA stage is missing or non-deterministic")

        if failures:
            return FamilyRenderReadinessDecision(
                status=FamilyRenderReadiness.BLOCKED,
                render_allowed=False,
                publication_allowed=False,
                failures=tuple(failures),
            )
        return FamilyRenderReadinessDecision(
            status=FamilyRenderReadiness.RENDER_STRUCTURE_READY,
            render_allowed=True,
            publication_allowed=False,
            failures=(),
        )

    def assert_renderable(self, composition: PlatformEditorialComposition, render_plan: FamilyRenderPlan) -> None:
        decision = self.evaluate(composition, render_plan)
        if not decision.render_allowed:
            raise ValueError("FAMILY_RENDER_NOT_READY:" + ";".join(decision.failures))
