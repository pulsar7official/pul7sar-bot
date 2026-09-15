"""Locked human visual-study handoff for Phase 18 PUL7SAR scenes.

The handoff is a review/generation contract, not an image and never a publication
claim. It binds one verified story decision to its story-family benchmark, copy
budget, approved identity semantics and accepted visual-reference qualities.
"""
from __future__ import annotations

from dataclasses import dataclass, fields
from hashlib import sha256
import json
from types import MappingProxyType
from typing import Mapping

from engine.intelligence.brand_approval_evidence import APPROVED_BRAND_GUIDE_EVIDENCE
from engine.intelligence.brand_master_contract import APPROVED_PUL7SAR_BRAND_MASTER
from engine.intelligence.brand_master_geometry import BrandMasterGeometryState
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualDecision
from engine.intelligence.visual_benchmark_suite import benchmark_for
from engine.intelligence.visual_reference_evidence import CHELSEA_REFERENCE_7_OF_10
from engine.intelligence.visual_review_readiness import VisualReviewReadinessGate


@dataclass(frozen=True)
class VisualStudyHandoff:
    handoff_version: str
    story_event: str
    scene_family: str
    headline: str
    supporting_copy: str | None
    hero_priority: str
    environment: str
    composition: str
    club_accent_role: str
    brand_identity_id: str
    brand_placement: str
    deterministic_ownership: tuple[str, ...]
    generated_ownership: tuple[str, ...]
    forbidden: tuple[str, ...]
    benchmark_id: str
    benchmark_goal: str
    benchmark_must_show: tuple[str, ...]
    benchmark_must_avoid: tuple[str, ...]
    visual_reference_id: str
    visual_reference_preserve: tuple[str, ...]
    visual_reference_improve_or_avoid: tuple[str, ...]
    brand_guide_evidence_id: str
    brand_guide_sha256: str
    exact_brand_geometry_ready: bool
    publication_ready: bool
    human_review_allowed: bool
    readiness_status: str
    metadata: Mapping[str, object]
    payload_sha256: str = ""

    def __post_init__(self) -> None:
        for field_name in (
            "deterministic_ownership", "generated_ownership", "forbidden",
            "benchmark_must_show", "benchmark_must_avoid",
            "visual_reference_preserve", "visual_reference_improve_or_avoid",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name)))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


class VisualStudyHandoffCompiler:
    VERSION = "pul7sar-visual-study-handoff-v1"

    def __init__(self) -> None:
        self._readiness = VisualReviewReadinessGate()

    @staticmethod
    def _payload_from_handoff(handoff: VisualStudyHandoff) -> dict[str, object]:
        payload: dict[str, object] = {}
        for item in fields(handoff):
            if item.name == "payload_sha256":
                continue
            value = getattr(handoff, item.name)
            if item.name == "metadata":
                value = dict(value)
            payload[item.name] = value
        return payload

    def compile(
        self,
        decision: StoryToVisualDecision,
        *,
        headline: str,
        supporting_copy: str | None = None,
        brand_geometry: BrandMasterGeometryState | None = None,
    ) -> VisualStudyHandoff:
        if not isinstance(decision, StoryToVisualDecision):
            raise TypeError("decision must be StoryToVisualDecision")
        brand = APPROVED_PUL7SAR_BRAND_MASTER
        brand.assert_safe()
        scene = decision.sports_editorial_scene
        benchmark = benchmark_for(decision.plan.event)
        readiness = self._readiness.evaluate(
            decision,
            headline=headline,
            supporting_copy=supporting_copy,
            brand_geometry=brand_geometry,
        )
        if not readiness.human_review_allowed:
            raise ValueError("VISUAL_STUDY_NOT_READY_FOR_HUMAN_REVIEW: " + "; ".join(readiness.failures))

        payload = {
            "handoff_version": self.VERSION,
            "story_event": decision.plan.event.value,
            "scene_family": scene.family.value,
            "headline": headline.strip(),
            "supporting_copy": supporting_copy.strip() if supporting_copy else None,
            "hero_priority": scene.hero_priority,
            "environment": scene.environment,
            "composition": scene.composition,
            "club_accent_role": scene.club_accent_role,
            "brand_identity_id": scene.brand_identity_id,
            "brand_placement": scene.brand_placement,
            "deterministic_ownership": scene.deterministic_ownership,
            "generated_ownership": scene.generated_ownership,
            "forbidden": scene.forbidden,
            "benchmark_id": benchmark.benchmark_id,
            "benchmark_goal": benchmark.goal,
            "benchmark_must_show": benchmark.must_show,
            "benchmark_must_avoid": benchmark.must_avoid,
            "visual_reference_id": CHELSEA_REFERENCE_7_OF_10.reference_id,
            "visual_reference_preserve": CHELSEA_REFERENCE_7_OF_10.preserve,
            "visual_reference_improve_or_avoid": CHELSEA_REFERENCE_7_OF_10.improve_or_avoid,
            "brand_guide_evidence_id": APPROVED_BRAND_GUIDE_EVIDENCE.evidence_id,
            "brand_guide_sha256": APPROVED_BRAND_GUIDE_EVIDENCE.sha256,
            "exact_brand_geometry_ready": readiness.publication_geometry_ready,
            "publication_ready": False,
            "human_review_allowed": readiness.human_review_allowed,
            "readiness_status": readiness.status.value,
            "metadata": {
                "contract": "pul7sar-visual-study-v1",
                "story_specific": True,
                "provider_agnostic": True,
                "zero_cost_compatible": True,
                "legacy_repo_logo_allowed": False,
                "generated_readable_brand_allowed": False,
                "generated_exact_club_marks_allowed": False,
                "publication_claim_allowed": False,
            },
        }
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        digest = sha256(canonical.encode("utf-8")).hexdigest()
        return VisualStudyHandoff(**payload, payload_sha256=digest)

    @classmethod
    def verify(cls, handoff: VisualStudyHandoff) -> None:
        if not isinstance(handoff, VisualStudyHandoff):
            raise TypeError("handoff must be VisualStudyHandoff")
        payload = cls._payload_from_handoff(handoff)
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        actual = sha256(canonical.encode("utf-8")).hexdigest()
        if actual != handoff.payload_sha256:
            raise ValueError("VISUAL_STUDY_HANDOFF_CHECKSUM_MISMATCH")
        if handoff.publication_ready:
            raise ValueError("VISUAL_STUDY_HANDOFF_MAY_NOT_CLAIM_PUBLICATION_READY")
        if handoff.metadata.get("legacy_repo_logo_allowed") is not False:
            raise ValueError("VISUAL_STUDY_HANDOFF_LEGACY_LOGO_POLICY_DRIFT")
