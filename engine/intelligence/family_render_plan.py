"""Family-aware render-stage planning for PUL7SAR Phase 18.

This module converts platform composition into ordered layer ownership. It does
not render pixels and does not invoke a generator. Its purpose is to guarantee
that each story family reaches rendering through its own stage order while exact
facts, identity, text and PUL7SAR branding remain deterministic.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from engine.intelligence.platform_editorial_composition import PlatformEditorialComposition
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


class RenderOwner(str, Enum):
    DETERMINISTIC = "deterministic"
    VERIFIED_ASSET = "verified_asset"
    OPTIONAL_ATMOSPHERE = "optional_atmosphere"


@dataclass(frozen=True)
class FamilyRenderStage:
    order: int
    stage_id: str
    owner: RenderOwner
    exact: bool


@dataclass(frozen=True)
class FamilyRenderPlan:
    family: EditorialSceneFamily
    stages: tuple[FamilyRenderStage, ...]
    brand_last_before_qa: bool
    readable_text_generator_owned: bool
    exact_data_generator_owned: bool
    exact_identity_generator_owned: bool
    publication_ready: bool = False
    contract: str = "pul7sar-family-render-plan-v1"

    def __post_init__(self) -> None:
        if not self.stages:
            raise ValueError("FAMILY_RENDER_PLAN_REQUIRES_STAGES")
        orders = tuple(stage.order for stage in self.stages)
        if orders != tuple(range(1, len(self.stages) + 1)):
            raise ValueError("FAMILY_RENDER_STAGE_ORDER_MUST_BE_CONTIGUOUS")
        if not self.brand_last_before_qa:
            raise ValueError("PUL7SAR_BRAND_MUST_BE_LAST_EXACT_LAYER_BEFORE_QA")
        if self.readable_text_generator_owned:
            raise ValueError("READABLE_TEXT_MAY_NOT_BE_GENERATOR_OWNED")
        if self.exact_data_generator_owned:
            raise ValueError("EXACT_DATA_MAY_NOT_BE_GENERATOR_OWNED")
        if self.exact_identity_generator_owned:
            raise ValueError("EXACT_IDENTITY_MAY_NOT_BE_GENERATOR_OWNED")
        if self.publication_ready:
            raise ValueError("RENDER_PLAN_ALONE_CANNOT_AUTHORIZE_PUBLICATION")
        if self.stages[-2].stage_id != "pul7sar_brand" or self.stages[-1].stage_id != "visual_qa":
            raise ValueError("RENDER_PLAN_MUST_END_WITH_BRAND_THEN_QA")
        if self.stages[-2].owner is not RenderOwner.DETERMINISTIC:
            raise ValueError("PUL7SAR_BRAND_MUST_BE_DETERMINISTIC")


class FamilyRenderPlanner:
    def plan(self, composition: PlatformEditorialComposition) -> FamilyRenderPlan:
        if not isinstance(composition, PlatformEditorialComposition):
            raise TypeError("composition must be PlatformEditorialComposition")
        family = composition.family
        specs = self._specs(family)
        stages = tuple(
            FamilyRenderStage(i + 1, stage_id, owner, exact)
            for i, (stage_id, owner, exact) in enumerate(specs)
        )
        return FamilyRenderPlan(
            family=family,
            stages=stages,
            brand_last_before_qa=True,
            readable_text_generator_owned=False,
            exact_data_generator_owned=False,
            exact_identity_generator_owned=False,
        )

    @staticmethod
    def _specs(family: EditorialSceneFamily) -> tuple[tuple[str, RenderOwner, bool], ...]:
        if family is EditorialSceneFamily.TRANSFER_SIGNATURE:
            return (
                ("story_atmosphere", RenderOwner.OPTIONAL_ATMOSPHERE, False),
                ("verified_hero", RenderOwner.VERIFIED_ASSET, True),
                ("exact_club_context", RenderOwner.DETERMINISTIC, True),
                ("editorial_copy", RenderOwner.DETERMINISTIC, True),
                ("pul7sar_brand", RenderOwner.DETERMINISTIC, True),
                ("visual_qa", RenderOwner.DETERMINISTIC, True),
            )
        if family is EditorialSceneFamily.RESULT_STATEMENT:
            return (
                ("match_atmosphere", RenderOwner.OPTIONAL_ATMOSPHERE, False),
                ("balanced_club_identities", RenderOwner.DETERMINISTIC, True),
                ("exact_score", RenderOwner.DETERMINISTIC, True),
                ("editorial_copy", RenderOwner.DETERMINISTIC, True),
                ("pul7sar_brand", RenderOwner.DETERMINISTIC, True),
                ("visual_qa", RenderOwner.DETERMINISTIC, True),
            )
        if family is EditorialSceneFamily.VERIFIED_SUBJECT_NEWS:
            return (
                ("restrained_atmosphere", RenderOwner.OPTIONAL_ATMOSPHERE, False),
                ("verified_subject", RenderOwner.VERIFIED_ASSET, True),
                ("editorial_copy", RenderOwner.DETERMINISTIC, True),
                ("pul7sar_brand", RenderOwner.DETERMINISTIC, True),
                ("visual_qa", RenderOwner.DETERMINISTIC, True),
            )
        if family is EditorialSceneFamily.TACTICAL_BOARD:
            return (
                ("deterministic_sport_geometry", RenderOwner.DETERMINISTIC, True),
                ("exact_tactical_data", RenderOwner.DETERMINISTIC, True),
                ("editorial_copy", RenderOwner.DETERMINISTIC, True),
                ("pul7sar_brand", RenderOwner.DETERMINISTIC, True),
                ("visual_qa", RenderOwner.DETERMINISTIC, True),
            )
        if family is EditorialSceneFamily.DATA_MONUMENT:
            return (
                ("data_atmosphere", RenderOwner.OPTIONAL_ATMOSPHERE, False),
                ("exact_data", RenderOwner.DETERMINISTIC, True),
                ("editorial_copy", RenderOwner.DETERMINISTIC, True),
                ("pul7sar_brand", RenderOwner.DETERMINISTIC, True),
                ("visual_qa", RenderOwner.DETERMINISTIC, True),
            )
        if family is EditorialSceneFamily.EVENT_EDITORIAL:
            return (
                ("story_atmosphere", RenderOwner.OPTIONAL_ATMOSPHERE, False),
                ("verified_story_anchor", RenderOwner.DETERMINISTIC, True),
                ("editorial_copy", RenderOwner.DETERMINISTIC, True),
                ("pul7sar_brand", RenderOwner.DETERMINISTIC, True),
                ("visual_qa", RenderOwner.DETERMINISTIC, True),
            )
        raise ValueError(f"UNSUPPORTED_RENDER_FAMILY:{family.value}")
