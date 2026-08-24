"""Explicit renderer capability registry for PUL7SAR Phase 18 editorial families.

No family may silently fall back to another family's renderer. A family is either
implemented with its own pixel contract or remains contract-only and must fail
closed at render time until its renderer is built.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


class FamilyRendererStatus(str, Enum):
    IMPLEMENTED = "implemented"
    CONTRACT_ONLY = "contract_only"


@dataclass(frozen=True)
class FamilyRendererCapability:
    family: EditorialSceneFamily
    status: FamilyRendererStatus
    renderer_module: str | None
    renderer_class: str | None
    renderer_contract: str | None
    exact_assets_required: tuple[str, ...]
    generator_required: bool
    network_required: bool
    may_inherit_other_family_renderer: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.family, EditorialSceneFamily):
            raise TypeError("family must be EditorialSceneFamily")
        if not isinstance(self.status, FamilyRendererStatus):
            raise TypeError("status must be FamilyRendererStatus")
        object.__setattr__(self, "exact_assets_required", tuple(self.exact_assets_required))
        if self.may_inherit_other_family_renderer:
            raise ValueError("EDITORIAL_FAMILY_RENDERER_INHERITANCE_FORBIDDEN")
        if self.status is FamilyRendererStatus.IMPLEMENTED:
            if not self.renderer_module or not self.renderer_class or not self.renderer_contract:
                raise ValueError("IMPLEMENTED_FAMILY_REQUIRES_EXPLICIT_RENDERER_CONTRACT")
        else:
            if any((self.renderer_module, self.renderer_class, self.renderer_contract)):
                raise ValueError("CONTRACT_ONLY_FAMILY_MAY_NOT_CLAIM_RENDERER_IMPLEMENTATION")
        if self.generator_required or self.network_required:
            raise ValueError("PHASE18_FAMILY_RENDERER_REGISTRY_MUST_REMAIN_ZERO_COST_CORE")


class FamilyRendererRegistry:
    VERSION = "pul7sar-family-renderer-registry-v1"

    def __init__(self) -> None:
        capabilities = {
            EditorialSceneFamily.TRANSFER_SIGNATURE: FamilyRendererCapability(
                family=EditorialSceneFamily.TRANSFER_SIGNATURE,
                status=FamilyRendererStatus.IMPLEMENTED,
                renderer_module="engine.intelligence.editorial_reference_scene_study_renderer",
                renderer_class="EditorialReferenceSceneStudyRenderer",
                renderer_contract="pul7sar-editorial-reference-scene-study-renderer-v6-adaptive-brand",
                exact_assets_required=("verified_subject_asset_for_real_person", "embedded_pul7sar_brand_master"),
                generator_required=False,
                network_required=False,
            ),
            EditorialSceneFamily.RESULT_STATEMENT: FamilyRendererCapability(
                family=EditorialSceneFamily.RESULT_STATEMENT,
                status=FamilyRendererStatus.IMPLEMENTED,
                renderer_module="engine.intelligence.result_statement_study_renderer",
                renderer_class="ResultStatementStudyRenderer",
                renderer_contract="pul7sar-result-statement-study-renderer-v2-score-monument",
                exact_assets_required=("verified_club_identity_assets_for_publication", "embedded_pul7sar_brand_master"),
                generator_required=False,
                network_required=False,
            ),
            EditorialSceneFamily.VERIFIED_SUBJECT_NEWS: FamilyRendererCapability(
                family=EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,
                status=FamilyRendererStatus.IMPLEMENTED,
                renderer_module="engine.intelligence.verified_subject_news_study_renderer",
                renderer_class="VerifiedSubjectNewsStudyRenderer",
                renderer_contract="pul7sar-verified-subject-news-study-renderer-v1-asset-first",
                exact_assets_required=("verified_subject_asset", "verified_identity_plan", "embedded_pul7sar_brand_master"),
                generator_required=False,
                network_required=False,
            ),
            EditorialSceneFamily.TACTICAL_BOARD: FamilyRendererCapability(
                family=EditorialSceneFamily.TACTICAL_BOARD,
                status=FamilyRendererStatus.IMPLEMENTED,
                renderer_module="engine.intelligence.tactical_intelligence_study_renderer",
                renderer_class="TacticalIntelligenceStudyRenderer",
                renderer_contract="pul7sar-tactical-intelligence-study-renderer-v1",
                exact_assets_required=("exact_tactical_data", "embedded_pul7sar_brand_master"),
                generator_required=False,
                network_required=False,
            ),
            EditorialSceneFamily.DATA_MONUMENT: FamilyRendererCapability(
                family=EditorialSceneFamily.DATA_MONUMENT,
                status=FamilyRendererStatus.CONTRACT_ONLY,
                renderer_module=None,
                renderer_class=None,
                renderer_contract=None,
                exact_assets_required=("fact_locked_data", "embedded_pul7sar_brand_master"),
                generator_required=False,
                network_required=False,
            ),
            EditorialSceneFamily.EVENT_EDITORIAL: FamilyRendererCapability(
                family=EditorialSceneFamily.EVENT_EDITORIAL,
                status=FamilyRendererStatus.CONTRACT_ONLY,
                renderer_module=None,
                renderer_class=None,
                renderer_contract=None,
                exact_assets_required=("fact_locked_event_context", "embedded_pul7sar_brand_master"),
                generator_required=False,
                network_required=False,
            ),
        }
        if set(capabilities) != set(EditorialSceneFamily):
            raise RuntimeError("FAMILY_RENDERER_REGISTRY_COVERAGE_DRIFT")
        self._capabilities: Mapping[EditorialSceneFamily, FamilyRendererCapability] = MappingProxyType(capabilities)

    def get(self, family: EditorialSceneFamily) -> FamilyRendererCapability:
        if not isinstance(family, EditorialSceneFamily):
            raise TypeError("family must be EditorialSceneFamily")
        return self._capabilities[family]

    def require_implemented(self, family: EditorialSceneFamily) -> FamilyRendererCapability:
        capability = self.get(family)
        if capability.status is not FamilyRendererStatus.IMPLEMENTED:
            raise ValueError(f"FAMILY_RENDERER_NOT_IMPLEMENTED: {family.value}")
        return capability

    def snapshot(self) -> tuple[FamilyRendererCapability, ...]:
        return tuple(self._capabilities[family] for family in EditorialSceneFamily)
