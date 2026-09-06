"""Concept-level renderer routing for PUL7SAR original visuals.

The registry is now ORIGINAL-FIRST. Legacy photo-led renderers remain visible as
contract-only reference/study capabilities so they cannot silently become final
publication pixel routes. Deterministic information renderers remain implemented.
Identity-conditioned and local generative scene runtimes stay contract-only until
a measured runtime is qualified.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from engine.intelligence.visual_concept_director import VisualConceptArchetype


class ConceptRendererStatus(str, Enum):
    IMPLEMENTED = "implemented"
    CONTRACT_ONLY = "contract_only"


class ConceptSurfaceClass(str, Enum):
    PHOTO_LED = "photo_led"
    PREMIUM_HYBRID = "premium_hybrid"
    VERIFIED_ASSET_LED = "verified_asset_led"
    DETERMINISTIC_INFORMATION = "deterministic_information"
    MINIMAL_EDITORIAL = "minimal_editorial"
    LOCAL_GENERATIVE_ATMOSPHERE = "local_generative_atmosphere"
    IDENTITY_CONDITIONED_GENERATIVE = "identity_conditioned_generative"


@dataclass(frozen=True)
class ConceptRendererCapability:
    archetype: VisualConceptArchetype
    status: ConceptRendererStatus
    surface_class: ConceptSurfaceClass
    renderer_module: str | None
    renderer_class: str | None
    renderer_contract: str | None
    required_asset_roles: tuple[str, ...]
    generator_required: bool = False
    network_required: bool = False
    reference_only: bool = False
    original_pixels: bool = True
    publication_ready: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.archetype, VisualConceptArchetype):
            raise TypeError("archetype must be VisualConceptArchetype")
        if not isinstance(self.status, ConceptRendererStatus):
            raise TypeError("status must be ConceptRendererStatus")
        if not isinstance(self.surface_class, ConceptSurfaceClass):
            raise TypeError("surface_class must be ConceptSurfaceClass")
        object.__setattr__(self, "required_asset_roles", tuple(self.required_asset_roles))
        if self.status is ConceptRendererStatus.IMPLEMENTED:
            if not all((self.renderer_module, self.renderer_class, self.renderer_contract)):
                raise ValueError("IMPLEMENTED_CONCEPT_REQUIRES_EXPLICIT_RENDERER")
            if self.reference_only:
                raise ValueError("REFERENCE_ONLY_CONCEPT_MAY_NOT_BE_IMPLEMENTED_FOR_PUBLICATION_ROUTING")
        elif any((self.renderer_module, self.renderer_class, self.renderer_contract)):
            raise ValueError("CONTRACT_ONLY_CONCEPT_MAY_NOT_CLAIM_RENDERER")
        if self.network_required:
            raise ValueError("CONCEPT_REGISTRY_MAY_NOT_REQUIRE_NETWORK_PROVIDER")
        if self.generator_required and self.status is not ConceptRendererStatus.CONTRACT_ONLY:
            raise ValueError("GENERATOR_CONCEPT_MUST_REMAIN_CONTRACT_ONLY_UNTIL_RUNTIME_QUALIFIED")
        if self.reference_only and self.original_pixels:
            raise ValueError("REFERENCE_ONLY_ROUTE_CANNOT_CLAIM_ORIGINAL_PIXELS")
        if self.publication_ready:
            raise ValueError("CONCEPT_CAPABILITY_ALONE_CANNOT_AUTHORIZE_PUBLICATION")


class ConceptRendererRegistry:
    VERSION = "pul7sar-concept-renderer-registry-v5-original-first"

    def __init__(self) -> None:
        implemented = ConceptRendererStatus.IMPLEMENTED
        contract = ConceptRendererStatus.CONTRACT_ONLY
        entries = {
            # Person-led concepts require a future qualified identity-conditioned
            # generator. Verified portraits are references, never default pixels.
            VisualConceptArchetype.HERO_ARRIVAL: ConceptRendererCapability(
                VisualConceptArchetype.HERO_ARRIVAL, contract, ConceptSurfaceClass.IDENTITY_CONDITIONED_GENERATIVE,
                None, None, None, ("verified_subject_reference", "exact_club_assets", "qualified_identity_runtime"),
                generator_required=True,
            ),
            VisualConceptArchetype.SYMBOLIC_SIGNING_REVEAL: ConceptRendererCapability(
                VisualConceptArchetype.SYMBOLIC_SIGNING_REVEAL, implemented, ConceptSurfaceClass.MINIMAL_EDITORIAL,
                "engine.intelligence.verified_detail_editorial_renderer", "VerifiedDetailEditorialRenderer",
                "pul7sar-verified-detail-editorial-renderer-v1", ("exact_club_assets", "embedded_pul7sar_brand_master"),
            ),
            # These old photographic concepts are deliberately quarantined. They
            # may remain useful for visual verification studies, but not final pixels.
            VisualConceptArchetype.DECISIVE_MOMENT: ConceptRendererCapability(
                VisualConceptArchetype.DECISIVE_MOMENT, contract, ConceptSurfaceClass.PHOTO_LED,
                None, None, None, ("verified_story_moment_reference",), reference_only=True, original_pixels=False,
            ),
            VisualConceptArchetype.CELEBRATION_MOMENT: ConceptRendererCapability(
                VisualConceptArchetype.CELEBRATION_MOMENT, contract, ConceptSurfaceClass.PHOTO_LED,
                None, None, None, ("verified_story_moment_reference",), reference_only=True, original_pixels=False,
            ),
            VisualConceptArchetype.VERIFIED_MATCH_MOMENT: ConceptRendererCapability(
                VisualConceptArchetype.VERIFIED_MATCH_MOMENT, contract, ConceptSurfaceClass.PHOTO_LED,
                None, None, None, ("verified_match_reference",), reference_only=True, original_pixels=False,
            ),
            VisualConceptArchetype.SCORE_MONUMENT: ConceptRendererCapability(
                VisualConceptArchetype.SCORE_MONUMENT, implemented, ConceptSurfaceClass.DETERMINISTIC_INFORMATION,
                "engine.intelligence.result_statement_study_renderer", "ResultStatementStudyRenderer",
                "pul7sar-result-statement-study-renderer-v2-score-monument", ("exact_score", "exact_club_assets"),
            ),
            VisualConceptArchetype.VERIFIED_PORTRAIT: ConceptRendererCapability(
                VisualConceptArchetype.VERIFIED_PORTRAIT, contract, ConceptSurfaceClass.PHOTO_LED,
                None, None, None, ("verified_subject_reference",), reference_only=True, original_pixels=False,
            ),
            VisualConceptArchetype.VERIFIED_EVIDENCE_DETAIL: ConceptRendererCapability(
                VisualConceptArchetype.VERIFIED_EVIDENCE_DETAIL, implemented, ConceptSurfaceClass.MINIMAL_EDITORIAL,
                "engine.intelligence.verified_detail_editorial_renderer", "VerifiedDetailEditorialRenderer",
                "pul7sar-verified-detail-editorial-renderer-v1", ("verified_detail_reference", "embedded_pul7sar_brand_master"),
            ),
            VisualConceptArchetype.TACTICAL_SPATIAL_MAP: ConceptRendererCapability(
                VisualConceptArchetype.TACTICAL_SPATIAL_MAP, implemented, ConceptSurfaceClass.DETERMINISTIC_INFORMATION,
                "engine.intelligence.tactical_intelligence_study_renderer", "TacticalIntelligenceStudyRenderer",
                "pul7sar-tactical-intelligence-study-renderer-v1", ("exact_tactical_data",),
            ),
            VisualConceptArchetype.DATA_MONOLITH: ConceptRendererCapability(
                VisualConceptArchetype.DATA_MONOLITH, implemented, ConceptSurfaceClass.DETERMINISTIC_INFORMATION,
                "engine.intelligence.data_monument_study_renderer", "DataMonumentStudyRenderer",
                "pul7sar-data-monument-study-renderer-v1-premium", ("exact_data_anchor",),
            ),
            VisualConceptArchetype.PHOTOGRAPHIC_EVENT: ConceptRendererCapability(
                VisualConceptArchetype.PHOTOGRAPHIC_EVENT, contract, ConceptSurfaceClass.PHOTO_LED,
                None, None, None, ("verified_context_reference",), reference_only=True, original_pixels=False,
            ),
            VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE: ConceptRendererCapability(
                VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE, contract, ConceptSurfaceClass.LOCAL_GENERATIVE_ATMOSPHERE,
                None, None, None, ("qualified_local_gpu_runtime", "semantic_inspection"), generator_required=True,
            ),
            VisualConceptArchetype.MINIMAL_EVENT_SYMBOL: ConceptRendererCapability(
                VisualConceptArchetype.MINIMAL_EVENT_SYMBOL, implemented, ConceptSurfaceClass.MINIMAL_EDITORIAL,
                "engine.intelligence.event_editorial_runtime_v2", "EventEditorialStudyRenderer",
                "pul7sar-event-editorial-study-renderer-v1-premium-anchor", (),
            ),
        }
        if set(entries) != set(VisualConceptArchetype):
            raise RuntimeError("CONCEPT_RENDERER_REGISTRY_COVERAGE_DRIFT")
        self._entries: Mapping[VisualConceptArchetype, ConceptRendererCapability] = MappingProxyType(entries)

    def get(self, archetype: VisualConceptArchetype) -> ConceptRendererCapability:
        if not isinstance(archetype, VisualConceptArchetype):
            raise TypeError("archetype must be VisualConceptArchetype")
        return self._entries[archetype]

    def require_implemented(self, archetype: VisualConceptArchetype) -> ConceptRendererCapability:
        capability = self.get(archetype)
        if capability.status is not ConceptRendererStatus.IMPLEMENTED:
            raise ValueError(f"VISUAL_CONCEPT_RENDERER_NOT_IMPLEMENTED:{archetype.value}")
        if capability.reference_only or not capability.original_pixels:
            raise ValueError(f"VISUAL_CONCEPT_NOT_ORIGINAL_PUBLICATION_ROUTE:{archetype.value}")
        return capability

    def snapshot(self) -> tuple[ConceptRendererCapability, ...]:
        return tuple(self._entries[item] for item in VisualConceptArchetype)
