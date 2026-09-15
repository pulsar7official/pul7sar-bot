"""Deterministic semantic/layer ownership policy for PUL7SAR Phase 18.

Qwen-Image may own atmosphere, depth, mood and non-factual texture. Exact facts,
typography, PUL7SAR branding, entity marks, identity-sensitive subjects and exact
sport geometry remain deterministic or verified-asset responsibilities. This policy
replays byte-bound ownership evidence and delegates leakage rejection to the existing
``HybridLayerQualityGate``.

Passing this gate grants no factual, identity, sentiment, generation, visual-quality,
human-review, Golden, brand-placement, or publication authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from engine.intelligence.hybrid_layer_planner import (
    HybridLayerPlan,
    LayerSource,
    VisualLayer,
)
from engine.intelligence.visual_layer_qa import (
    HybridLayerQualityGate,
    LayerLeakageEvidence,
)


SEMANTIC_LAYER_OWNERSHIP_EVIDENCE_SCHEMA = (
    "pul7sar-phase18-semantic-layer-ownership-evidence-v1"
)
SEMANTIC_LAYER_OWNERSHIP_GATE_ID = "semantic_layer_ownership"
VERIFIER_ID = "pul7sar.production.semantic_layer_ownership"
VERIFIER_VERSION = "1.0.0"

_REQUIRED_EVIDENCE_FIELDS = (
    "schema",
    "gate_id",
    "story_snapshot_sha256",
    "identity_sensitive_subject_present",
    "exact_sport_geometry_required",
    "layer_plan",
    "leakage_evidence",
)
_LAYER_FIELDS = ("name", "source", "required")
_LEAKAGE_FIELDS = (
    "generated_text_detected",
    "generated_platform_brand_detected",
    "generated_exact_numbers_detected",
    "generated_entity_mark_detected",
    "generated_unverified_identity_detected",
    "generated_sport_geometry_detected",
    "notes",
)

_BASE_LAYER_ORDER = (
    "atmosphere_base",
    "sport_surface_geometry",
    "exact_entity_marks",
    "data_and_score",
    "editorial_typography",
    "pul7sar_brand",
)
_LAYER_PURPOSES = {
    "atmosphere_base": "lighting, depth, crowd/environment mood and non-factual texture only",
    "sport_surface_geometry": "regulation playing-surface geometry rendered by code under perspective",
    "hero_identity": "verified real subject asset or separately identity-verified depiction",
    "exact_entity_marks": "official club/team/competition marks when required",
    "data_and_score": "scores, statistics, tables, dates and exact numbers",
    "editorial_typography": "headline and supporting editorial copy",
    "pul7sar_brand": "exact approved PUL7SAR logo, number-7/pulse treatment and social footer",
}


@dataclass(frozen=True)
class SemanticLayerOwnershipDecision:
    allowed: bool
    layer_count: int
    generated_layer_count: int
    deterministic_layer_count: int
    verified_asset_layer_count: int
    optional_layer_count: int
    leakage_blocker_count: int


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value.lower())
    )


def _load_evidence(evidence_path: Path) -> tuple[dict[str, Any], bytes]:
    if not isinstance(evidence_path, Path) or not evidence_path.is_file():
        raise ValueError("QWEN_LAYER_OWNERSHIP_EVIDENCE_MISSING")
    raw = evidence_path.read_bytes()
    if not raw:
        raise ValueError("QWEN_LAYER_OWNERSHIP_EVIDENCE_EMPTY")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("QWEN_LAYER_OWNERSHIP_EVIDENCE_JSON_INVALID") from exc
    if not isinstance(payload, dict) or tuple(payload.keys()) != _REQUIRED_EVIDENCE_FIELDS:
        raise ValueError("QWEN_LAYER_OWNERSHIP_EVIDENCE_SHAPE_INVALID")
    return payload, raw


def _require_bool(value: Any, code: str) -> bool:
    if type(value) is not bool:
        raise ValueError(code)
    return value


def _build_layer_plan(
    layer_plan: Sequence[Mapping[str, Any]],
    *,
    identity_sensitive_subject_present: bool,
    exact_sport_geometry_required: bool,
) -> HybridLayerPlan:
    if not isinstance(layer_plan, list):
        raise ValueError("PUL7SAR_LAYER_OWNERSHIP_PLAN_INVALID")

    expected_order = list(_BASE_LAYER_ORDER)
    if identity_sensitive_subject_present:
        expected_order.insert(2, "hero_identity")

    if len(layer_plan) != len(expected_order):
        raise ValueError("PUL7SAR_LAYER_OWNERSHIP_LAYER_SET_INVALID")

    layers: list[VisualLayer] = []
    seen: set[str] = set()
    for index, raw_layer in enumerate(layer_plan):
        if not isinstance(raw_layer, Mapping) or tuple(raw_layer.keys()) != _LAYER_FIELDS:
            raise ValueError("PUL7SAR_LAYER_OWNERSHIP_LAYER_SHAPE_INVALID")
        name = raw_layer["name"]
        source = raw_layer["source"]
        required = raw_layer["required"]
        if not isinstance(name, str) or not name.strip():
            raise ValueError("PUL7SAR_LAYER_OWNERSHIP_LAYER_NAME_INVALID")
        if name in seen:
            raise ValueError("PUL7SAR_LAYER_OWNERSHIP_LAYER_DUPLICATE")
        seen.add(name)
        if name != expected_order[index]:
            raise ValueError("PUL7SAR_LAYER_OWNERSHIP_LAYER_ORDER_OR_SET_INVALID")
        if type(required) is not bool:
            raise ValueError("PUL7SAR_LAYER_OWNERSHIP_REQUIRED_FLAG_INVALID")
        try:
            layer_source = LayerSource(source)
        except (TypeError, ValueError) as exc:
            raise ValueError("PUL7SAR_LAYER_OWNERSHIP_SOURCE_UNKNOWN") from exc

        expected_source: LayerSource
        expected_required: bool
        if name == "atmosphere_base":
            expected_source = LayerSource.GENERATIVE
            expected_required = True
        elif name == "sport_surface_geometry":
            expected_source = (
                LayerSource.DETERMINISTIC
                if exact_sport_geometry_required
                else LayerSource.OPTIONAL
            )
            expected_required = exact_sport_geometry_required
        elif name == "hero_identity":
            expected_source = LayerSource.VERIFIED_ASSET
            expected_required = True
        elif name == "exact_entity_marks":
            expected_source = LayerSource.VERIFIED_ASSET
            expected_required = False
        elif name == "data_and_score":
            expected_source = LayerSource.DETERMINISTIC
            expected_required = False
        elif name == "editorial_typography":
            expected_source = LayerSource.DETERMINISTIC
            expected_required = True
        elif name == "pul7sar_brand":
            expected_source = LayerSource.VERIFIED_ASSET
            expected_required = True
        else:  # Defensive: expected_order is closed above.
            raise ValueError("PUL7SAR_LAYER_OWNERSHIP_LAYER_UNKNOWN")

        if layer_source is not expected_source:
            raise ValueError(f"PUL7SAR_LAYER_OWNERSHIP_SOURCE_INVALID:{name}")
        if required is not expected_required:
            raise ValueError(f"PUL7SAR_LAYER_OWNERSHIP_REQUIRED_INVALID:{name}")

        layers.append(
            VisualLayer(
                name=name,
                source=layer_source,
                purpose=_LAYER_PURPOSES[name],
                required=required,
            )
        )

    return HybridLayerPlan(tuple(layers))


def _build_leakage_evidence(payload: Mapping[str, Any]) -> LayerLeakageEvidence:
    if not isinstance(payload, Mapping) or tuple(payload.keys()) != _LEAKAGE_FIELDS:
        raise ValueError("PUL7SAR_LAYER_OWNERSHIP_LEAKAGE_SHAPE_INVALID")

    bool_values = {
        field: _require_bool(
            payload[field],
            f"PUL7SAR_LAYER_OWNERSHIP_LEAKAGE_BOOL_INVALID:{field}",
        )
        for field in _LEAKAGE_FIELDS[:-1]
    }
    notes = payload["notes"]
    if not isinstance(notes, list) or any(not isinstance(note, str) for note in notes):
        raise ValueError("PUL7SAR_LAYER_OWNERSHIP_NOTES_INVALID")

    return LayerLeakageEvidence(notes=tuple(notes), **bool_values)


def evaluate_semantic_layer_ownership(
    *,
    layer_plan: Sequence[Mapping[str, Any]],
    leakage_evidence: Mapping[str, Any],
    identity_sensitive_subject_present: bool,
    exact_sport_geometry_required: bool,
) -> SemanticLayerOwnershipDecision:
    """Validate canonical ownership and reject generative leakage into exact layers."""
    identity_sensitive_subject_present = _require_bool(
        identity_sensitive_subject_present,
        "PUL7SAR_LAYER_OWNERSHIP_IDENTITY_FLAG_INVALID",
    )
    exact_sport_geometry_required = _require_bool(
        exact_sport_geometry_required,
        "PUL7SAR_LAYER_OWNERSHIP_GEOMETRY_FLAG_INVALID",
    )
    plan = _build_layer_plan(
        layer_plan,
        identity_sensitive_subject_present=identity_sensitive_subject_present,
        exact_sport_geometry_required=exact_sport_geometry_required,
    )
    leakage = _build_leakage_evidence(leakage_evidence)
    qa_decision = HybridLayerQualityGate().evaluate(plan, leakage)
    if not qa_decision.passed:
        raise ValueError(
            "QWEN_LAYER_OWNERSHIP_SEMANTIC_REJECTED: "
            + "; ".join(qa_decision.blockers)
        )

    counts = {source: 0 for source in LayerSource}
    for layer in plan.layers:
        counts[layer.source] += 1

    return SemanticLayerOwnershipDecision(
        allowed=True,
        layer_count=len(plan.layers),
        generated_layer_count=counts[LayerSource.GENERATIVE],
        deterministic_layer_count=counts[LayerSource.DETERMINISTIC],
        verified_asset_layer_count=counts[LayerSource.VERIFIED_ASSET],
        optional_layer_count=counts[LayerSource.OPTIONAL],
        leakage_blocker_count=0,
    )


def verify_semantic_layer_ownership_evidence(
    evidence_path: Path,
    story_snapshot_sha256: str,
    receipt: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Replay-compatible verifier over byte-bound semantic/layer ownership evidence."""
    if not _is_sha256(story_snapshot_sha256):
        raise ValueError("QWEN_LAYER_OWNERSHIP_STORY_SHA_INVALID")
    if not isinstance(receipt, Mapping):
        raise ValueError("QWEN_LAYER_OWNERSHIP_RECEIPT_INVALID")
    if receipt.get("verifier_id") != VERIFIER_ID:
        raise ValueError("QWEN_LAYER_OWNERSHIP_VERIFIER_ID_MISMATCH")
    if receipt.get("verifier_version") != VERIFIER_VERSION:
        raise ValueError("QWEN_LAYER_OWNERSHIP_VERIFIER_VERSION_MISMATCH")

    evidence, raw = _load_evidence(evidence_path)
    if evidence["schema"] != SEMANTIC_LAYER_OWNERSHIP_EVIDENCE_SCHEMA:
        raise ValueError("QWEN_LAYER_OWNERSHIP_EVIDENCE_SCHEMA_DRIFT")
    if evidence["gate_id"] != SEMANTIC_LAYER_OWNERSHIP_GATE_ID:
        raise ValueError("QWEN_LAYER_OWNERSHIP_GATE_DRIFT")
    if evidence["story_snapshot_sha256"] != story_snapshot_sha256:
        raise ValueError("QWEN_LAYER_OWNERSHIP_CROSS_STORY_EVIDENCE")

    decision = evaluate_semantic_layer_ownership(
        layer_plan=evidence["layer_plan"],
        leakage_evidence=evidence["leakage_evidence"],
        identity_sensitive_subject_present=evidence["identity_sensitive_subject_present"],
        exact_sport_geometry_required=evidence["exact_sport_geometry_required"],
    )
    if decision.allowed is not True:
        raise ValueError("QWEN_LAYER_OWNERSHIP_REJECTED")

    details = {
        "layer_count": decision.layer_count,
        "generated_layer_count": decision.generated_layer_count,
        "deterministic_layer_count": decision.deterministic_layer_count,
        "verified_asset_layer_count": decision.verified_asset_layer_count,
        "optional_layer_count": decision.optional_layer_count,
        "leakage_blocker_count": decision.leakage_blocker_count,
        "generated_content_limited_to_non_factual_atmosphere": True,
        "exact_text_owned_by_deterministic_layer": True,
        "exact_data_owned_by_deterministic_layer": True,
        "exact_brand_and_entity_marks_owned_by_verified_assets": True,
        "identity_sensitive_subject_owned_by_verified_asset_if_present": True,
        "exact_sport_geometry_owned_by_deterministic_layer_if_required": True,
    }
    return {
        "gate_id": SEMANTIC_LAYER_OWNERSHIP_GATE_ID,
        "story_snapshot_sha256": story_snapshot_sha256,
        "source_evidence_sha256": hashlib.sha256(raw).hexdigest(),
        "source_evidence_byte_size": len(raw),
        "verifier_id": VERIFIER_ID,
        "verifier_version": VERIFIER_VERSION,
        "gate_passed": True,
        "verification_details": details,
    }
