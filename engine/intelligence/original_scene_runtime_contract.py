"""Provider-agnostic contract for original PUL7SAR scene synthesis.

This is the seam between PUL7SAR's editorial/visual intelligence and a future
qualified image model runtime. It deliberately contains no Colab, FLUX, API or
vendor assumption. The runtime may create atmosphere and non-factual scene
pixels, while deterministic layers continue to own exact text, score, crests,
PUL7SAR identity and other facts.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from engine.intelligence.visual_concept_director import VisualConceptArchetype


class OriginalSceneRuntimeKind(str, Enum):
    ATMOSPHERE = "atmosphere"
    IDENTITY_CONDITIONED = "identity_conditioned"


@dataclass(frozen=True)
class OriginalSceneRequest:
    archetype: VisualConceptArchetype
    runtime_kind: OriginalSceneRuntimeKind
    scene_intent: str
    emotional_tone: str
    safe_negative_space: str
    forbidden_visual_claims: tuple[str, ...]
    exact_fact_roles_reserved_for_compositor: tuple[str, ...]
    identity_reference_ids: tuple[str, ...] = ()
    context_reference_ids: tuple[str, ...] = ()
    width: int = 1080
    height: int = 1350
    seed: int = 0
    contract: str = "pul7sar-original-scene-request-v1"

    def __post_init__(self) -> None:
        if not isinstance(self.archetype, VisualConceptArchetype):
            raise TypeError("archetype must be VisualConceptArchetype")
        if not isinstance(self.runtime_kind, OriginalSceneRuntimeKind):
            raise TypeError("runtime_kind must be OriginalSceneRuntimeKind")
        if not self.scene_intent.strip() or not self.emotional_tone.strip() or not self.safe_negative_space.strip():
            raise ValueError("original scene request strings must be non-empty")
        if self.width < 512 or self.height < 512:
            raise ValueError("original scene canvas is too small")
        if self.seed < 0:
            raise ValueError("seed must be non-negative")
        object.__setattr__(self, "forbidden_visual_claims", tuple(self.forbidden_visual_claims))
        object.__setattr__(self, "exact_fact_roles_reserved_for_compositor", tuple(self.exact_fact_roles_reserved_for_compositor))
        object.__setattr__(self, "identity_reference_ids", tuple(self.identity_reference_ids))
        object.__setattr__(self, "context_reference_ids", tuple(self.context_reference_ids))
        mandatory = {"readable_text", "pul7sar_brand", "exact_score", "club_crest"}
        if not mandatory.issubset(set(self.exact_fact_roles_reserved_for_compositor)):
            raise ValueError("ORIGINAL_SCENE_MUST_RESERVE_EXACT_FACT_LAYERS_FOR_COMPOSITOR")
        if self.runtime_kind is OriginalSceneRuntimeKind.IDENTITY_CONDITIONED and not self.identity_reference_ids:
            raise ValueError("IDENTITY_CONDITIONED_SCENE_REQUIRES_VERIFIED_IDENTITY_REFERENCE")


@dataclass(frozen=True)
class OriginalSceneRuntimeQualification:
    runtime_id: str
    runtime_kind: OriginalSceneRuntimeKind
    local_or_self_hosted: bool
    provider_agnostic_adapter: bool
    original_pixels: bool
    accepts_seed: bool
    semantic_inspection_required: bool
    identity_fidelity_gate_required: bool
    network_dependency_required: bool = False
    paid_provider_required: bool = False
    qualified: bool = False
    contract: str = "pul7sar-original-scene-runtime-qualification-v1"

    def __post_init__(self) -> None:
        if not self.runtime_id.strip():
            raise ValueError("runtime_id must be non-empty")
        if not isinstance(self.runtime_kind, OriginalSceneRuntimeKind):
            raise TypeError("runtime_kind must be OriginalSceneRuntimeKind")
        if self.network_dependency_required or self.paid_provider_required:
            raise ValueError("PHASE18_ORIGINAL_RUNTIME_MAY_NOT_REQUIRE_NETWORK_OR_PAID_PROVIDER")
        if self.qualified:
            if not all((self.local_or_self_hosted, self.provider_agnostic_adapter, self.original_pixels, self.accepts_seed, self.semantic_inspection_required)):
                raise ValueError("QUALIFIED_RUNTIME_MISSING_REQUIRED_CAPABILITY")
            if self.runtime_kind is OriginalSceneRuntimeKind.IDENTITY_CONDITIONED and not self.identity_fidelity_gate_required:
                raise ValueError("IDENTITY_RUNTIME_REQUIRES_IDENTITY_FIDELITY_GATE")


UNQUALIFIED_ATMOSPHERE_RUNTIME = OriginalSceneRuntimeQualification(
    runtime_id="pending-local-original-atmosphere-runtime",
    runtime_kind=OriginalSceneRuntimeKind.ATMOSPHERE,
    local_or_self_hosted=True,
    provider_agnostic_adapter=True,
    original_pixels=True,
    accepts_seed=True,
    semantic_inspection_required=True,
    identity_fidelity_gate_required=False,
    qualified=False,
)

UNQUALIFIED_IDENTITY_RUNTIME = OriginalSceneRuntimeQualification(
    runtime_id="pending-local-identity-conditioned-runtime",
    runtime_kind=OriginalSceneRuntimeKind.IDENTITY_CONDITIONED,
    local_or_self_hosted=True,
    provider_agnostic_adapter=True,
    original_pixels=True,
    accepts_seed=True,
    semantic_inspection_required=True,
    identity_fidelity_gate_required=True,
    qualified=False,
)
