"""Byte-bound generated-layer ownership QA for a canonical Qwen candidate.

Change Set 268 binds the exact CS264 semantic inspection, the exact CS265
identity-requirement classification, and (when a human identity is required)
the exact CS267 identity-review evidence to the existing HybridLayerQualityGate.
Change Set 306 strengthens that contract by requiring exact receipt lineage
coherence: CS265 must bind the same CS264 receipt supplied to this gate, and a
required CS267 review must trace through a CS266 request that binds the same
CS265 receipt supplied to this gate. This prevents same-story/same-candidate
cross-run receipt substitution.

The gate deliberately evaluates only the generated/base layer. It does not
claim that deterministic typography, score/data, sport geometry, verified
marks or PUL7SAR branding have been composed yet, and it grants no
Golden/publication authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.hybrid_layer_planner import HybridLayerPlan, LayerSource, VisualLayer
from engine.intelligence.qwen_image_canonical_candidate_identity_requirement import (
    SCHEMA as IDENTITY_REQUIREMENT_SCHEMA,
    verify_identity_requirement,
)
from engine.intelligence.qwen_image_canonical_candidate_pixel_identity_review_evidence import (
    SCHEMA as PIXEL_IDENTITY_EVIDENCE_SCHEMA,
    verify_pixel_identity_review_evidence,
)
from engine.intelligence.qwen_image_canonical_candidate_pixel_identity_review_request import (
    verify_pixel_identity_review_request,
)
from engine.intelligence.qwen_image_canonical_candidate_semantic_base_qa import (
    CANONICAL_CANDIDATE_SEMANTIC_BASE_QA_SCHEMA,
    verify_canonical_candidate_semantic_base_qa,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json
from engine.intelligence.visual_layer_qa import HybridLayerQualityGate, LayerLeakageEvidence

SCHEMA = "pul7sar-phase18-qwen-image-canonical-candidate-generated-layer-qa-v1"
_DOWNSTREAM_FALSE = (
    "semantic_approved",
    "human_visual_review_approved",
    "genuine_golden_png_created",
    "golden_quality_approved",
    "publication_ready",
)


@dataclass(frozen=True)
class CanonicalCandidateGeneratedLayerQARun:
    receipt_path: Path
    generated_layer_qa_approved: bool


def _read_json(path: Path, code: str) -> tuple[dict[str, Any], bytes]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(code)
    raw = path.read_bytes()
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(code) from exc
    if not isinstance(value, dict):
        raise ValueError(code)
    return value, raw


def _inside_repo_file(repo_root: Path, path: Path, code: str) -> str:
    if path.is_symlink():
        raise ValueError(code)
    root = repo_root.resolve()
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError(code) from exc
    if not resolved.is_file():
        raise ValueError(code)
    return relative


def _bind_file(repo_root: Path, path: Path, code: str) -> dict[str, Any]:
    relative = _inside_repo_file(repo_root, path, code)
    raw = path.read_bytes()
    if not raw:
        raise ValueError(code)
    return {
        "repository_relative_path": relative,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
    }


def _reopen_binding(repo_root: Path, binding: Mapping[str, Any], code: str) -> Path:
    relative = binding.get("repository_relative_path")
    if (
        not isinstance(relative, str)
        or not relative
        or Path(relative).is_absolute()
        or ".." in Path(relative).parts
    ):
        raise ValueError(code)
    path = repo_root.resolve() / relative
    canonical = _inside_repo_file(repo_root, path, code)
    if canonical != Path(relative).as_posix():
        raise ValueError(code)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != binding.get("sha256") or len(raw) != binding.get("byte_size"):
        raise ValueError(f"{code}_BYTE_DRIFT")
    return path


def _exact_receipt_binding(binding: Mapping[str, Any], receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "repository_relative_path": binding.get("repository_relative_path"),
        "sha256": binding.get("sha256"),
        "byte_size": binding.get("byte_size"),
        "receipt_sha256": receipt.get("receipt_sha256"),
    }


def _assert_exact_receipt_binding(
    claimed: Any,
    actual_binding: Mapping[str, Any],
    actual_receipt: Mapping[str, Any],
    code: str,
) -> None:
    if not isinstance(claimed, Mapping) or dict(claimed) != _exact_receipt_binding(actual_binding, actual_receipt):
        raise ValueError(code)


def _verify_required_identity_lineage(
    *,
    repo_root: Path,
    cs267: Mapping[str, Any],
    cs265_binding: Mapping[str, Any],
    cs265: Mapping[str, Any],
) -> None:
    cs266_binding = cs267.get("source_cs266_request")
    if not isinstance(cs266_binding, Mapping):
        raise ValueError("QWEN_GENERATED_LAYER_QA_CS267_CS266_LINEAGE_INVALID")
    cs266_path = _reopen_binding(repo_root, cs266_binding, "QWEN_GENERATED_LAYER_QA_CS266_INVALID")
    cs266 = verify_pixel_identity_review_request(cs266_path, repo_root=repo_root)
    if cs266_binding.get("receipt_sha256") != cs266.get("receipt_sha256"):
        raise ValueError("QWEN_GENERATED_LAYER_QA_CS267_CS266_RECEIPT_DRIFT")
    _assert_exact_receipt_binding(
        cs266.get("source_cs265_receipt"),
        cs265_binding,
        cs265,
        "QWEN_GENERATED_LAYER_QA_CS265_CS267_LINEAGE_DRIFT",
    )


def _assert_downstream_closed(receipt: Mapping[str, Any], prefix: str) -> None:
    for field in _DOWNSTREAM_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(f"{prefix}_PREMATURE_AUTHORITY:{field}")


def _canonical_candidate_plan(*, identity_required: bool) -> HybridLayerPlan:
    """Conservative base-candidate ownership plan using the existing layer contract."""
    layers = [
        VisualLayer(
            "atmosphere_base",
            LayerSource.GENERATIVE,
            "lighting, depth, environment mood and non-factual texture only",
        ),
        VisualLayer(
            "sport_surface_geometry",
            LayerSource.DETERMINISTIC,
            "exact sport geometry is never trusted to the base generative candidate",
            required=False,
        ),
    ]
    if identity_required:
        layers.append(
            VisualLayer(
                "hero_identity",
                LayerSource.VERIFIED_ASSET,
                "verified real subject asset or separately identity-verified depiction",
            )
        )
    layers.extend(
        (
            VisualLayer(
                "exact_entity_marks",
                LayerSource.VERIFIED_ASSET,
                "official club/team/competition marks when required",
                required=False,
            ),
            VisualLayer(
                "data_and_score",
                LayerSource.DETERMINISTIC,
                "scores, statistics, dates and exact numbers",
                required=False,
            ),
            VisualLayer(
                "editorial_typography",
                LayerSource.DETERMINISTIC,
                "headline and supporting editorial copy",
            ),
            VisualLayer(
                "pul7sar_brand",
                LayerSource.VERIFIED_ASSET,
                "exact approved PUL7SAR brand treatment",
            ),
        )
    )
    return HybridLayerPlan(tuple(layers))


def _layer_evidence_from_cs264(
    source: Mapping[str, Any], *, identity_required: bool, identity_approved: bool
) -> LayerLeakageEvidence:
    semantic_layer = source.get("semantic_layer_evidence")
    if not isinstance(semantic_layer, Mapping) or semantic_layer.get("complete") is not True:
        raise ValueError("QWEN_GENERATED_LAYER_QA_SEMANTIC_LAYER_EVIDENCE_INCOMPLETE")
    raw = semantic_layer.get("evidence")
    if not isinstance(raw, Mapping):
        raise ValueError("QWEN_GENERATED_LAYER_QA_SEMANTIC_LAYER_EVIDENCE_INVALID")
    bool_fields = (
        "generated_text_detected",
        "generated_platform_brand_detected",
        "generated_exact_numbers_detected",
        "generated_entity_mark_detected",
        "generated_unverified_identity_detected",
        "generated_sport_geometry_detected",
    )
    values: dict[str, bool] = {}
    for field in bool_fields:
        value = raw.get(field)
        if not isinstance(value, bool):
            raise ValueError(f"QWEN_GENERATED_LAYER_QA_EVIDENCE_INVALID:{field}")
        values[field] = value
    notes = raw.get("notes")
    if not isinstance(notes, list) or any(not isinstance(item, str) for item in notes):
        raise ValueError("QWEN_GENERATED_LAYER_QA_NOTES_INVALID")
    return LayerLeakageEvidence(
        generated_text_detected=values["generated_text_detected"],
        generated_platform_brand_detected=values["generated_platform_brand_detected"],
        generated_exact_numbers_detected=values["generated_exact_numbers_detected"],
        generated_entity_mark_detected=values["generated_entity_mark_detected"],
        generated_unverified_identity_detected=(
            values["generated_unverified_identity_detected"]
            or (identity_required and not identity_approved)
        ),
        generated_sport_geometry_detected=values["generated_sport_geometry_detected"],
        notes=tuple(notes),
    )


def _plan_payload(plan: HybridLayerPlan) -> list[dict[str, Any]]:
    return [
        {
            "name": layer.name,
            "source": layer.source.value,
            "purpose": layer.purpose,
            "required": layer.required,
        }
        for layer in plan.layers
    ]


def _evidence_payload(evidence: LayerLeakageEvidence) -> dict[str, Any]:
    return {
        "generated_text_detected": evidence.generated_text_detected,
        "generated_platform_brand_detected": evidence.generated_platform_brand_detected,
        "generated_exact_numbers_detected": evidence.generated_exact_numbers_detected,
        "generated_entity_mark_detected": evidence.generated_entity_mark_detected,
        "generated_unverified_identity_detected": evidence.generated_unverified_identity_detected,
        "generated_sport_geometry_detected": evidence.generated_sport_geometry_detected,
        "notes": list(evidence.notes),
    }


def run_canonical_candidate_generated_layer_qa(
    cs264_receipt_path: Path,
    cs265_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
    cs267_receipt_path: Path | None = None,
) -> CanonicalCandidateGeneratedLayerQARun:
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("QWEN_GENERATED_LAYER_QA_OUTPUT_INVALID")

    cs264_binding = _bind_file(repo_root, cs264_receipt_path, "QWEN_GENERATED_LAYER_QA_CS264_INVALID")
    cs265_binding = _bind_file(repo_root, cs265_receipt_path, "QWEN_GENERATED_LAYER_QA_CS265_INVALID")
    cs264 = verify_canonical_candidate_semantic_base_qa(cs264_receipt_path, repo_root=repo_root)
    cs265 = verify_identity_requirement(cs265_receipt_path, repo_root=repo_root)
    if cs264.get("schema") != CANONICAL_CANDIDATE_SEMANTIC_BASE_QA_SCHEMA or cs264.get("semantic_base_scene_approved") is not True:
        raise ValueError("QWEN_GENERATED_LAYER_QA_CS264_NOT_APPROVED")
    if cs265.get("schema") != IDENTITY_REQUIREMENT_SCHEMA or cs265.get("identity_requirement_classified") is not True:
        raise ValueError("QWEN_GENERATED_LAYER_QA_CS265_INVALID")
    _assert_downstream_closed(cs264, "QWEN_GENERATED_LAYER_QA_CS264")
    _assert_downstream_closed(cs265, "QWEN_GENERATED_LAYER_QA_CS265")
    _assert_exact_receipt_binding(
        cs265.get("source_cs264_receipt"),
        cs264_binding,
        cs264,
        "QWEN_GENERATED_LAYER_QA_CS264_CS265_LINEAGE_DRIFT",
    )

    story_sha = cs264.get("story_snapshot_sha256")
    candidate = cs264.get("candidate_png")
    if story_sha != cs265.get("story_snapshot_sha256") or candidate != cs265.get("candidate_png"):
        raise ValueError("QWEN_GENERATED_LAYER_QA_UPSTREAM_BINDING_DRIFT")
    if not isinstance(candidate, Mapping):
        raise ValueError("QWEN_GENERATED_LAYER_QA_CANDIDATE_INVALID")
    _reopen_binding(repo_root, candidate, "QWEN_GENERATED_LAYER_QA_CANDIDATE_INVALID")

    identity_required = cs265.get("pixel_identity_review_required") is True
    identity_approved = False
    cs267_binding: dict[str, Any] | None = None
    cs267_receipt_sha: str | None = None
    if identity_required:
        if cs267_receipt_path is None:
            raise ValueError("QWEN_GENERATED_LAYER_QA_PIXEL_IDENTITY_EVIDENCE_REQUIRED")
        cs267_binding = _bind_file(repo_root, cs267_receipt_path, "QWEN_GENERATED_LAYER_QA_CS267_INVALID")
        cs267 = verify_pixel_identity_review_evidence(cs267_receipt_path, repo_root=repo_root)
        if cs267.get("schema") != PIXEL_IDENTITY_EVIDENCE_SCHEMA:
            raise ValueError("QWEN_GENERATED_LAYER_QA_CS267_SCHEMA_DRIFT")
        _assert_downstream_closed(cs267, "QWEN_GENERATED_LAYER_QA_CS267")
        _verify_required_identity_lineage(
            repo_root=repo_root,
            cs267=cs267,
            cs265_binding=cs265_binding,
            cs265=cs265,
        )
        if (
            cs267.get("story_snapshot_sha256") != story_sha
            or cs267.get("candidate_png") != candidate
            or cs267.get("identity_approved") is not True
            or cs267.get("pixel_identity_review_executed") is not True
        ):
            raise ValueError("QWEN_GENERATED_LAYER_QA_IDENTITY_NOT_APPROVED")
        identity_approved = True
        cs267_receipt_sha = cs267.get("receipt_sha256")
    elif cs267_receipt_path is not None:
        raise ValueError("QWEN_GENERATED_LAYER_QA_UNEXPECTED_PIXEL_IDENTITY_EVIDENCE")

    plan = _canonical_candidate_plan(identity_required=identity_required)
    evidence = _layer_evidence_from_cs264(
        cs264, identity_required=identity_required, identity_approved=identity_approved
    )
    decision = HybridLayerQualityGate().evaluate(plan, evidence)
    approved = decision.passed and (not identity_required or identity_approved)

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": (
            "QWEN_IMAGE_CANONICAL_CANDIDATE_GENERATED_LAYER_QA_PASSED"
            if approved
            else "QWEN_IMAGE_CANONICAL_CANDIDATE_GENERATED_LAYER_QA_REJECTED"
        ),
        "story_snapshot_sha256": story_sha,
        "source_cs264_receipt": {**cs264_binding, "receipt_sha256": cs264.get("receipt_sha256")},
        "source_cs265_receipt": {**cs265_binding, "receipt_sha256": cs265.get("receipt_sha256")},
        "source_cs267_receipt": (
            {**cs267_binding, "receipt_sha256": cs267_receipt_sha}
            if cs267_binding is not None
            else None
        ),
        "candidate_png": dict(candidate),
        "pixel_identity_review_required": identity_required,
        "identity_approved": identity_approved if identity_required else False,
        "hybrid_layer_plan": _plan_payload(plan),
        "layer_leakage_evidence": _evidence_payload(evidence),
        "hybrid_layer_gate": {
            "passed": decision.passed,
            "blockers": list(decision.blockers),
            "notes": list(decision.notes),
        },
        "generated_layer_qa_approved": approved,
        "composition_executed": False,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "genuine_golden_png_created": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "policy": {
            "existing_hybrid_layer_quality_gate_reused": True,
            "base_candidate_only_not_composed_visual": True,
            "deterministic_and_verified_layers_not_yet_claimed_present": True,
            "missing_required_identity_review_fails_closed": True,
            "upstream_unverified_identity_evidence_is_never_suppressed": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)

    output_dir.mkdir(mode=0o700)
    receipt_path = output_dir / "canonical_candidate_generated_layer_qa.json"
    tmp = output_dir / ".canonical_candidate_generated_layer_qa.json.tmp"
    try:
        with tmp.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, receipt_path)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        if output_dir.exists() and not any(output_dir.iterdir()):
            output_dir.rmdir()
        raise
    return CanonicalCandidateGeneratedLayerQARun(receipt_path, approved)


def verify_canonical_candidate_generated_layer_qa(
    receipt_path: Path, *, repo_root: Path
) -> dict[str, Any]:
    receipt, _ = _read_json(receipt_path, "QWEN_GENERATED_LAYER_QA_RECEIPT_INVALID")
    if receipt.get("schema") != SCHEMA:
        raise ValueError("QWEN_GENERATED_LAYER_QA_SCHEMA_DRIFT")
    claimed = receipt.get("receipt_sha256")
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    if claimed != sha256_json(unsigned):
        raise ValueError("QWEN_GENERATED_LAYER_QA_RECEIPT_DIGEST_MISMATCH")
    for field in (
        "composition_executed",
        "composed_visual_approved",
        *_DOWNSTREAM_FALSE,
    ):
        if receipt.get(field) is not False:
            raise ValueError(f"QWEN_GENERATED_LAYER_QA_PREMATURE_AUTHORITY:{field}")

    b264 = receipt.get("source_cs264_receipt")
    b265 = receipt.get("source_cs265_receipt")
    if not isinstance(b264, Mapping) or not isinstance(b265, Mapping):
        raise ValueError("QWEN_GENERATED_LAYER_QA_UPSTREAM_BINDING_INVALID")
    p264 = _reopen_binding(repo_root, b264, "QWEN_GENERATED_LAYER_QA_CS264_INVALID")
    p265 = _reopen_binding(repo_root, b265, "QWEN_GENERATED_LAYER_QA_CS265_INVALID")
    cs264 = verify_canonical_candidate_semantic_base_qa(p264, repo_root=repo_root)
    cs265 = verify_identity_requirement(p265, repo_root=repo_root)
    if b264.get("receipt_sha256") != cs264.get("receipt_sha256") or b265.get("receipt_sha256") != cs265.get("receipt_sha256"):
        raise ValueError("QWEN_GENERATED_LAYER_QA_UPSTREAM_RECEIPT_DRIFT")
    if cs264.get("semantic_base_scene_approved") is not True or cs265.get("identity_requirement_classified") is not True:
        raise ValueError("QWEN_GENERATED_LAYER_QA_UPSTREAM_STATE_INVALID")
    _assert_downstream_closed(cs264, "QWEN_GENERATED_LAYER_QA_CS264")
    _assert_downstream_closed(cs265, "QWEN_GENERATED_LAYER_QA_CS265")
    _assert_exact_receipt_binding(
        cs265.get("source_cs264_receipt"),
        b264,
        cs264,
        "QWEN_GENERATED_LAYER_QA_CS264_CS265_LINEAGE_DRIFT",
    )
    if (
        receipt.get("story_snapshot_sha256") != cs264.get("story_snapshot_sha256")
        or cs264.get("story_snapshot_sha256") != cs265.get("story_snapshot_sha256")
        or receipt.get("candidate_png") != cs264.get("candidate_png")
        or cs264.get("candidate_png") != cs265.get("candidate_png")
    ):
        raise ValueError("QWEN_GENERATED_LAYER_QA_UPSTREAM_BINDING_DRIFT")
    candidate = receipt.get("candidate_png")
    if not isinstance(candidate, Mapping):
        raise ValueError("QWEN_GENERATED_LAYER_QA_CANDIDATE_INVALID")
    _reopen_binding(repo_root, candidate, "QWEN_GENERATED_LAYER_QA_CANDIDATE_INVALID")

    identity_required = cs265.get("pixel_identity_review_required") is True
    identity_approved = False
    b267 = receipt.get("source_cs267_receipt")
    if identity_required:
        if not isinstance(b267, Mapping):
            raise ValueError("QWEN_GENERATED_LAYER_QA_PIXEL_IDENTITY_EVIDENCE_REQUIRED")
        p267 = _reopen_binding(repo_root, b267, "QWEN_GENERATED_LAYER_QA_CS267_INVALID")
        cs267 = verify_pixel_identity_review_evidence(p267, repo_root=repo_root)
        _assert_downstream_closed(cs267, "QWEN_GENERATED_LAYER_QA_CS267")
        _verify_required_identity_lineage(
            repo_root=repo_root,
            cs267=cs267,
            cs265_binding=b265,
            cs265=cs265,
        )
        if (
            b267.get("receipt_sha256") != cs267.get("receipt_sha256")
            or cs267.get("story_snapshot_sha256") != receipt.get("story_snapshot_sha256")
            or cs267.get("candidate_png") != candidate
            or cs267.get("identity_approved") is not True
            or cs267.get("pixel_identity_review_executed") is not True
        ):
            raise ValueError("QWEN_GENERATED_LAYER_QA_IDENTITY_NOT_APPROVED")
        identity_approved = True
    elif b267 is not None:
        raise ValueError("QWEN_GENERATED_LAYER_QA_UNEXPECTED_PIXEL_IDENTITY_EVIDENCE")

    plan = _canonical_candidate_plan(identity_required=identity_required)
    evidence = _layer_evidence_from_cs264(
        cs264, identity_required=identity_required, identity_approved=identity_approved
    )
    decision = HybridLayerQualityGate().evaluate(plan, evidence)
    approved = decision.passed and (not identity_required or identity_approved)
    if receipt.get("hybrid_layer_plan") != _plan_payload(plan):
        raise ValueError("QWEN_GENERATED_LAYER_QA_PLAN_DRIFT")
    if receipt.get("layer_leakage_evidence") != _evidence_payload(evidence):
        raise ValueError("QWEN_GENERATED_LAYER_QA_EVIDENCE_DRIFT")
    expected_gate = {
        "passed": decision.passed,
        "blockers": list(decision.blockers),
        "notes": list(decision.notes),
    }
    if receipt.get("hybrid_layer_gate") != expected_gate:
        raise ValueError("QWEN_GENERATED_LAYER_QA_GATE_DRIFT")
    if receipt.get("generated_layer_qa_approved") is not approved:
        raise ValueError("QWEN_GENERATED_LAYER_QA_VERDICT_DRIFT")
    expected_status = (
        "QWEN_IMAGE_CANONICAL_CANDIDATE_GENERATED_LAYER_QA_PASSED"
        if approved
        else "QWEN_IMAGE_CANONICAL_CANDIDATE_GENERATED_LAYER_QA_REJECTED"
    )
    if receipt.get("status") != expected_status:
        raise ValueError("QWEN_GENERATED_LAYER_QA_STATUS_DRIFT")
    if receipt.get("identity_approved") is not (identity_approved if identity_required else False):
        raise ValueError("QWEN_GENERATED_LAYER_QA_IDENTITY_STATE_DRIFT")
    policy = receipt.get("policy")
    if not isinstance(policy, Mapping) or any(
        policy.get(key) is not True
        for key in (
            "existing_hybrid_layer_quality_gate_reused",
            "base_candidate_only_not_composed_visual",
            "deterministic_and_verified_layers_not_yet_claimed_present",
            "missing_required_identity_review_fails_closed",
            "upstream_unverified_identity_evidence_is_never_suppressed",
        )
    ):
        raise ValueError("QWEN_GENERATED_LAYER_QA_POLICY_DRIFT")
    return receipt
