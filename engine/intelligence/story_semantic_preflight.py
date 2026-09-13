"""Deterministic story-to-visual semantic preflight for PUL7SAR Phase 18.

This gate does not re-prove factual claims, identity, sentiment, or publication safety;
those remain independent production gates. Its job is to replay the project-native
``StoryVisualEditorialEngine`` against the exact story snapshot evidence and reject a
Qwen generation request when the proposed visual grammar drifts from that deterministic
editorial policy.

The verifier also byte-binds the underlying editorial-policy source in its semantic
verification details, so a later policy-code change invalidates an older replay receipt.
Passing this gate grants no CUDA, generation, visual-quality, Golden, human-review,
brand, typography, or publication authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from engine.intelligence.story_visual_editorial import (
    EditorialEvent,
    ProductionMode,
    StoryVisualEditorialEngine,
)


STORY_SEMANTIC_PREFLIGHT_EVIDENCE_SCHEMA = (
    "pul7sar-phase18-story-semantic-preflight-evidence-v1"
)
STORY_SEMANTIC_PREFLIGHT_GATE_ID = "story_semantic_preflight"
VERIFIER_ID = "pul7sar.production.story_semantic_preflight"
VERIFIER_VERSION = "1.0.0"

_REQUIRED_EVIDENCE_FIELDS = (
    "schema",
    "gate_id",
    "story_snapshot_sha256",
    "qwen_generation_requested",
    "editorial_request",
    "proposed_visual_plan",
)
_REQUEST_FIELDS = (
    "event",
    "sport",
    "story_core",
    "editorial_angle",
    "headline_short",
    "primary_subject",
    "secondary_subjects",
    "stakes",
    "sentiment",
    "exact_assets",
    "geometry_requirements",
    "confidence",
)
_PLAN_FIELDS = (
    "visual_family",
    "production_mode",
    "scene_concept",
    "generated_elements",
    "forbidden_generated_elements",
)
_QWEN_COMPATIBLE_MODES = {
    ProductionMode.HYBRID,
    ProductionMode.GENERATIVE_SCENE,
}
_EDITORIAL_POLICY_SOURCE = Path(__file__).with_name("story_visual_editorial.py")


@dataclass(frozen=True)
class StorySemanticPreflightDecision:
    allowed: bool
    event: str
    visual_family: str
    production_mode: str
    generated_element_count: int
    forbidden_generated_element_count: int
    editorial_policy_source_sha256: str
    editorial_policy_source_byte_size: int


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value.lower())
    )


def _load_evidence(evidence_path: Path) -> tuple[dict[str, Any], bytes]:
    if not isinstance(evidence_path, Path) or not evidence_path.is_file():
        raise ValueError("QWEN_STORY_SEMANTIC_EVIDENCE_MISSING")
    raw = evidence_path.read_bytes()
    if not raw:
        raise ValueError("QWEN_STORY_SEMANTIC_EVIDENCE_EMPTY")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("QWEN_STORY_SEMANTIC_EVIDENCE_JSON_INVALID") from exc
    if not isinstance(payload, dict) or tuple(payload.keys()) != _REQUIRED_EVIDENCE_FIELDS:
        raise ValueError("QWEN_STORY_SEMANTIC_EVIDENCE_SHAPE_INVALID")
    return payload, raw


def _require_text(value: Any, code: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(code)
    return value.strip()


def _require_string_list(value: Any, code: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ValueError(code)
    cleaned: list[str] = []
    for item in value:
        text = _require_text(item, code)
        if text in cleaned:
            raise ValueError(code + "_DUPLICATE")
        cleaned.append(text)
    return tuple(cleaned)


def _require_optional_text(value: Any, code: str) -> str | None:
    if value is None:
        return None
    return _require_text(value, code)


def _policy_source_binding() -> tuple[str, int]:
    if not _EDITORIAL_POLICY_SOURCE.is_file():
        raise ValueError("QWEN_STORY_SEMANTIC_EDITORIAL_POLICY_SOURCE_MISSING")
    raw = _EDITORIAL_POLICY_SOURCE.read_bytes()
    if not raw:
        raise ValueError("QWEN_STORY_SEMANTIC_EDITORIAL_POLICY_SOURCE_EMPTY")
    return hashlib.sha256(raw).hexdigest(), len(raw)


def evaluate_story_semantic_preflight(
    *,
    qwen_generation_requested: bool,
    editorial_request: Mapping[str, Any],
    proposed_visual_plan: Mapping[str, Any],
) -> StorySemanticPreflightDecision:
    """Recompute the project-native visual grammar and require exact semantic agreement."""
    if type(qwen_generation_requested) is not bool:
        raise ValueError("PUL7SAR_STORY_SEMANTIC_QWEN_REQUEST_FLAG_INVALID")
    if qwen_generation_requested is not True:
        raise ValueError("PUL7SAR_STORY_SEMANTIC_QWEN_GENERATION_NOT_REQUESTED")
    if not isinstance(editorial_request, Mapping) or tuple(editorial_request.keys()) != _REQUEST_FIELDS:
        raise ValueError("PUL7SAR_STORY_SEMANTIC_REQUEST_SHAPE_INVALID")
    if not isinstance(proposed_visual_plan, Mapping) or tuple(proposed_visual_plan.keys()) != _PLAN_FIELDS:
        raise ValueError("PUL7SAR_STORY_SEMANTIC_PLAN_SHAPE_INVALID")

    try:
        event = EditorialEvent(editorial_request["event"])
    except (TypeError, ValueError) as exc:
        raise ValueError("PUL7SAR_STORY_SEMANTIC_EVENT_INVALID") from exc

    sport = _require_text(editorial_request["sport"], "PUL7SAR_STORY_SEMANTIC_SPORT_REQUIRED")
    story_core = _require_text(
        editorial_request["story_core"], "PUL7SAR_STORY_SEMANTIC_STORY_CORE_REQUIRED"
    )
    editorial_angle = _require_text(
        editorial_request["editorial_angle"],
        "PUL7SAR_STORY_SEMANTIC_EDITORIAL_ANGLE_REQUIRED",
    )
    headline_short = _require_text(
        editorial_request["headline_short"],
        "PUL7SAR_STORY_SEMANTIC_HEADLINE_REQUIRED",
    )
    primary_subject = _require_optional_text(
        editorial_request["primary_subject"],
        "PUL7SAR_STORY_SEMANTIC_PRIMARY_SUBJECT_INVALID",
    )
    secondary_subjects = _require_string_list(
        editorial_request["secondary_subjects"],
        "PUL7SAR_STORY_SEMANTIC_SECONDARY_SUBJECTS_INVALID",
    )
    stakes = _require_text(
        editorial_request["stakes"], "PUL7SAR_STORY_SEMANTIC_STAKES_REQUIRED"
    )
    sentiment = _require_text(
        editorial_request["sentiment"], "PUL7SAR_STORY_SEMANTIC_SENTIMENT_REQUIRED"
    )
    exact_assets = _require_string_list(
        editorial_request["exact_assets"], "PUL7SAR_STORY_SEMANTIC_EXACT_ASSETS_INVALID"
    )
    geometry_requirements = _require_string_list(
        editorial_request["geometry_requirements"],
        "PUL7SAR_STORY_SEMANTIC_GEOMETRY_REQUIREMENTS_INVALID",
    )
    confidence = editorial_request["confidence"]
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        raise ValueError("PUL7SAR_STORY_SEMANTIC_CONFIDENCE_INVALID")
    confidence = float(confidence)

    try:
        plan = StoryVisualEditorialEngine().plan(
            event=event,
            sport=sport,
            story_core=story_core,
            editorial_angle=editorial_angle,
            headline_short=headline_short,
            primary_subject=primary_subject,
            secondary_subjects=secondary_subjects,
            stakes=stakes,
            sentiment=sentiment,
            exact_assets=exact_assets,
            geometry_requirements=geometry_requirements,
            confidence=confidence,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("PUL7SAR_STORY_SEMANTIC_EDITORIAL_POLICY_REJECTED") from exc

    if plan.production_mode not in _QWEN_COMPATIBLE_MODES:
        raise ValueError("PUL7SAR_STORY_SEMANTIC_PRODUCTION_MODE_NOT_QWEN_COMPATIBLE")

    proposed_family = _require_text(
        proposed_visual_plan["visual_family"],
        "PUL7SAR_STORY_SEMANTIC_VISUAL_FAMILY_REQUIRED",
    )
    if proposed_family != plan.visual_family.value:
        raise ValueError("PUL7SAR_STORY_SEMANTIC_VISUAL_FAMILY_DRIFT")

    proposed_mode = _require_text(
        proposed_visual_plan["production_mode"],
        "PUL7SAR_STORY_SEMANTIC_PRODUCTION_MODE_REQUIRED",
    )
    if proposed_mode != plan.production_mode.value:
        raise ValueError("PUL7SAR_STORY_SEMANTIC_PRODUCTION_MODE_DRIFT")

    scene_concept = _require_text(
        proposed_visual_plan["scene_concept"],
        "PUL7SAR_STORY_SEMANTIC_SCENE_CONCEPT_REQUIRED",
    )
    if scene_concept != plan.scene_concept:
        raise ValueError("PUL7SAR_STORY_SEMANTIC_SCENE_CONCEPT_DRIFT")

    proposed_generated = _require_string_list(
        proposed_visual_plan["generated_elements"],
        "PUL7SAR_STORY_SEMANTIC_GENERATED_ELEMENTS_INVALID",
    )
    if proposed_generated != plan.generated_elements:
        raise ValueError("PUL7SAR_STORY_SEMANTIC_GENERATED_ELEMENTS_DRIFT")

    proposed_forbidden = _require_string_list(
        proposed_visual_plan["forbidden_generated_elements"],
        "PUL7SAR_STORY_SEMANTIC_FORBIDDEN_ELEMENTS_INVALID",
    )
    if proposed_forbidden != plan.forbidden_generated_elements:
        raise ValueError("PUL7SAR_STORY_SEMANTIC_FORBIDDEN_ELEMENTS_DRIFT")

    policy_sha, policy_size = _policy_source_binding()
    return StorySemanticPreflightDecision(
        allowed=True,
        event=event.value,
        visual_family=plan.visual_family.value,
        production_mode=plan.production_mode.value,
        generated_element_count=len(plan.generated_elements),
        forbidden_generated_element_count=len(plan.forbidden_generated_elements),
        editorial_policy_source_sha256=policy_sha,
        editorial_policy_source_byte_size=policy_size,
    )


def verify_story_semantic_preflight_evidence(
    evidence_path: Path,
    story_snapshot_sha256: str,
    receipt: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Replay-compatible production verifier over byte-bound story semantic evidence."""
    if not _is_sha256(story_snapshot_sha256):
        raise ValueError("QWEN_STORY_SEMANTIC_STORY_SHA_INVALID")
    if not isinstance(receipt, Mapping):
        raise ValueError("QWEN_STORY_SEMANTIC_RECEIPT_INVALID")
    if receipt.get("verifier_id") != VERIFIER_ID:
        raise ValueError("QWEN_STORY_SEMANTIC_VERIFIER_ID_MISMATCH")
    if receipt.get("verifier_version") != VERIFIER_VERSION:
        raise ValueError("QWEN_STORY_SEMANTIC_VERIFIER_VERSION_MISMATCH")

    evidence, raw = _load_evidence(evidence_path)
    if evidence["schema"] != STORY_SEMANTIC_PREFLIGHT_EVIDENCE_SCHEMA:
        raise ValueError("QWEN_STORY_SEMANTIC_EVIDENCE_SCHEMA_DRIFT")
    if evidence["gate_id"] != STORY_SEMANTIC_PREFLIGHT_GATE_ID:
        raise ValueError("QWEN_STORY_SEMANTIC_GATE_DRIFT")
    if evidence["story_snapshot_sha256"] != story_snapshot_sha256:
        raise ValueError("QWEN_STORY_SEMANTIC_CROSS_STORY_EVIDENCE")

    decision = evaluate_story_semantic_preflight(
        qwen_generation_requested=evidence["qwen_generation_requested"],
        editorial_request=evidence["editorial_request"],
        proposed_visual_plan=evidence["proposed_visual_plan"],
    )
    if decision.allowed is not True:
        raise ValueError("QWEN_STORY_SEMANTIC_REJECTED")

    details = {
        "event": decision.event,
        "visual_family": decision.visual_family,
        "production_mode": decision.production_mode,
        "generated_element_count": decision.generated_element_count,
        "forbidden_generated_element_count": decision.forbidden_generated_element_count,
        "project_native_editorial_policy_replayed": True,
        "story_to_visual_contract_matches": True,
        "qwen_generation_semantically_applicable": True,
        "exact_text_scores_statistics_logos_remain_forbidden_generated_elements": True,
        "editorial_policy_source_sha256": decision.editorial_policy_source_sha256,
        "editorial_policy_source_byte_size": decision.editorial_policy_source_byte_size,
    }
    return {
        "gate_id": STORY_SEMANTIC_PREFLIGHT_GATE_ID,
        "story_snapshot_sha256": story_snapshot_sha256,
        "source_evidence_sha256": hashlib.sha256(raw).hexdigest(),
        "source_evidence_byte_size": len(raw),
        "verifier_id": VERIFIER_ID,
        "verifier_version": VERIFIER_VERSION,
        "gate_passed": True,
        "verification_details": details,
    }
