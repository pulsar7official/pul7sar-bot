"""Tamper-evident concept lock for the Phase 18 Dynamic Visual Brain.

The Dynamic Visual Brain may propose multiple materially different editorial
concepts, but the concept that enters rendering must be selected and frozen
*before* any pixels are generated.  This module makes that decision replayable
without granting generation or publication authority.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from typing import Any

from engine.intelligence.dynamic_visual_brain import DynamicVisualBrainPlan
from engine.intelligence.visual_brain import VisualConceptCandidate


_CONTRACT = "pul7sar-dynamic-visual-brain-concept-lock-v1"
_PLAN_CONTRACT = "pul7sar-dynamic-visual-brain-v1"
_REQUIRED_SAFETY_MARKERS = (
    "text",
    "logo",
    "real-person",
    "real venue",
    "collage",
)


def _canonical_json(payload: Any) -> bytes:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _candidate_payload(candidate: VisualConceptCandidate) -> dict[str, Any]:
    return {
        "concept_id": candidate.concept_id,
        "title": candidate.title,
        "editorial_metaphor": candidate.editorial_metaphor,
        "scene_prompt": candidate.scene_prompt,
        "camera_language": candidate.camera_language,
        "focal_strategy": candidate.focal_strategy,
        "negative_space_strategy": candidate.negative_space_strategy,
        "signature_elements": list(candidate.signature_elements),
        "forbidden_elements": list(candidate.forbidden_elements),
        "preflight_score": candidate.preflight_score,
        "metadata": dict(candidate.metadata),
    }


def candidate_sha256(candidate: VisualConceptCandidate) -> str:
    return sha256(_canonical_json(_candidate_payload(candidate))).hexdigest()


def competition_sha256(plan: DynamicVisualBrainPlan) -> str:
    payload = {
        "plan_contract": plan.contract,
        "story_fingerprint": plan.story_fingerprint,
        "event": plan.event.value,
        "concepts": [_candidate_payload(item) for item in plan.concepts],
    }
    return sha256(_canonical_json(payload)).hexdigest()


@dataclass(frozen=True)
class DynamicVisualBrainConceptLockReceipt:
    contract: str
    status: str
    story_fingerprint: str
    event: str
    concept_count: int
    competition_sha256: str
    selected_concept_id: str
    selected_concept_sha256: str
    scene_prompt_sha256: str
    preflight_score: float
    provider_agnostic: bool
    selection_locked_before_rendering: bool
    generation_authorized: bool
    human_visual_review_approved: bool
    golden_quality_approved: bool
    publication_ready: bool
    seeds_2_to_4_authorized: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DynamicVisualBrainConceptLock:
    """Freeze one explicit concept from one immutable story-specific competition."""

    CONTRACT = _CONTRACT

    @staticmethod
    def lock(plan: DynamicVisualBrainPlan, concept_id: str) -> DynamicVisualBrainConceptLockReceipt:
        if plan.contract != _PLAN_CONTRACT:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_PLAN_CONTRACT_MISMATCH")
        if plan.publication_ready:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_PLAN_CANNOT_AUTHORIZE_PUBLICATION")
        if not isinstance(plan.story_fingerprint, str) or len(plan.story_fingerprint) != 64:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_STORY_FINGERPRINT_INVALID")
        if len(plan.concepts) < 3:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_COMPETITION_TOO_SMALL")
        if not isinstance(concept_id, str) or not concept_id.strip():
            raise ValueError("DYNAMIC_VISUAL_BRAIN_CONCEPT_ID_REQUIRED")

        matches = [item for item in plan.concepts if item.concept_id == concept_id]
        if len(matches) != 1:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_CONCEPT_NOT_UNIQUE_OR_MISSING")
        selected = matches[0]

        if bool(selected.metadata.get("publication_ready")):
            raise ValueError("DYNAMIC_VISUAL_BRAIN_CONCEPT_CANNOT_AUTHORIZE_PUBLICATION")
        if selected.metadata.get("provider_agnostic") is not True:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_CONCEPT_MUST_BE_PROVIDER_AGNOSTIC")

        prompt_folded = selected.scene_prompt.casefold()
        if "pul7sar" in prompt_folded or "pulsar" in prompt_folded:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_PLATFORM_NAME_LEAK")

        forbidden = " ".join(selected.forbidden_elements).casefold()
        missing = [marker for marker in _REQUIRED_SAFETY_MARKERS if marker not in forbidden]
        if missing:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_SAFETY_MARKERS_MISSING:" + ",".join(missing))

        return DynamicVisualBrainConceptLockReceipt(
            contract=_CONTRACT,
            status="DYNAMIC_VISUAL_BRAIN_CONCEPT_LOCKED",
            story_fingerprint=plan.story_fingerprint,
            event=plan.event.value,
            concept_count=len(plan.concepts),
            competition_sha256=competition_sha256(plan),
            selected_concept_id=selected.concept_id,
            selected_concept_sha256=candidate_sha256(selected),
            scene_prompt_sha256=sha256(selected.scene_prompt.encode("utf-8")).hexdigest(),
            preflight_score=selected.preflight_score,
            provider_agnostic=True,
            selection_locked_before_rendering=True,
            generation_authorized=False,
            human_visual_review_approved=False,
            golden_quality_approved=False,
            publication_ready=False,
            seeds_2_to_4_authorized=False,
        )
