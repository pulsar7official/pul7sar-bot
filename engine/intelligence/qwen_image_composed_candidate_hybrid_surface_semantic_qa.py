"""Byte-bound semantic QA for a CS272 composed hybrid visual.

Change Set 273 consumes the exact composed PNG admitted by CS272 and runs the
existing pinned Qwen2.5-VL semantic inspector in HYBRID_SURFACE mode. The
existing SemanticVisualVerdictGate and SemanticLayerEvidenceAdapter are reused
fail-closed. This stage validates post-composition visual semantics/alignment
only; it never grants global semantic-publication, Human Review, Golden, or
publication authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.approved_model_revisions import (
    QWEN25_VL_3B_MODEL_ID,
    QWEN25_VL_3B_REVISION,
)
from engine.intelligence.qwen25_vl_inspector import (
    Qwen25VLSemanticInspector,
    SemanticInspectionStage,
    VERIFIER_ID as QWEN25_VL_VERIFIER_ID,
)
from engine.intelligence.qwen_image_composed_candidate_byte_admission import (
    SCHEMA as CS272_SCHEMA,
    verify_composed_candidate_byte_admission,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json
from engine.intelligence.semantic_layer_evidence import SemanticLayerEvidenceAdapter
from engine.intelligence.semantic_visual_verdict import (
    InspectionState,
    SemanticCheck,
    SemanticVisualVerdict,
    SemanticVisualVerdictGate,
)

SCHEMA = "pul7sar-phase18-qwen-image-composed-candidate-hybrid-surface-semantic-qa-v1"
MINIMUM_CONFIDENCE = 0.85
_REQUIRED_SOURCE_TRUE = (
    "composition_executed",
    "composed_candidate_bytes_admitted_for_post_composition_qa",
)
_DOWNSTREAM_FALSE = (
    "composed_visual_approved",
    "semantic_approved",
    "human_visual_review_approved",
    "genuine_golden_png_created",
    "golden_quality_approved",
    "publication_ready",
)


@dataclass(frozen=True)
class ComposedCandidateHybridSurfaceSemanticQA:
    output_dir: Path
    receipt_path: Path
    story_snapshot_sha256: str
    composed_candidate_sha256: str
    approved: bool


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        ch in "0123456789abcdef" for ch in value.lower()
    )


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
    if (
        hashlib.sha256(raw).hexdigest() != binding.get("sha256")
        or len(raw) != binding.get("byte_size")
    ):
        raise ValueError(f"{code}_BYTE_DRIFT")
    return path


def _check_payload(check: SemanticCheck | None) -> dict[str, Any] | None:
    if check is None:
        return None
    return {
        "state": check.state.value,
        "confidence": float(check.confidence),
        "detail": check.detail,
    }


def _verdict_payload(verdict: SemanticVisualVerdict) -> dict[str, Any]:
    return {
        "verifier_id": verdict.verifier_id,
        "readable_text_absent": _check_payload(verdict.readable_text_absent),
        "platform_brand_absent": _check_payload(verdict.platform_brand_absent),
        "fake_entity_marks_absent": _check_payload(verdict.fake_entity_marks_absent),
        "single_scene": _check_payload(verdict.single_scene),
        "severe_defects_absent": _check_payload(verdict.severe_defects_absent),
        "subject_framing_valid": _check_payload(verdict.subject_framing_valid),
        "sport_geometry_alignment_valid": _check_payload(verdict.sport_geometry_alignment_valid),
        "identity_valid": _check_payload(verdict.identity_valid),
        "exact_numbers_absent": _check_payload(verdict.exact_numbers_absent),
        "generated_sport_geometry_absent": _check_payload(verdict.generated_sport_geometry_absent),
    }


def _check_from_payload(value: Any, *, required: bool) -> SemanticCheck | None:
    if value is None:
        if required:
            raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_VERDICT_INCOMPLETE")
        return None
    if not isinstance(value, Mapping):
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_VERDICT_INVALID")
    try:
        state = InspectionState(str(value["state"]))
        confidence = float(value["confidence"])
        detail = str(value.get("detail") or "")
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_VERDICT_INVALID") from exc
    return SemanticCheck(state=state, confidence=confidence, detail=detail)


def _verdict_from_payload(value: Any) -> SemanticVisualVerdict:
    if not isinstance(value, Mapping):
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_VERDICT_INVALID")
    verifier_id = value.get("verifier_id")
    if not isinstance(verifier_id, str) or not verifier_id:
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_VERIFIER_INVALID")
    return SemanticVisualVerdict(
        verifier_id=verifier_id,
        readable_text_absent=_check_from_payload(value.get("readable_text_absent"), required=True),
        platform_brand_absent=_check_from_payload(value.get("platform_brand_absent"), required=True),
        fake_entity_marks_absent=_check_from_payload(value.get("fake_entity_marks_absent"), required=True),
        single_scene=_check_from_payload(value.get("single_scene"), required=True),
        severe_defects_absent=_check_from_payload(value.get("severe_defects_absent"), required=True),
        subject_framing_valid=_check_from_payload(value.get("subject_framing_valid"), required=True),
        sport_geometry_alignment_valid=_check_from_payload(
            value.get("sport_geometry_alignment_valid"), required=True
        ),
        identity_valid=_check_from_payload(value.get("identity_valid"), required=False),
        exact_numbers_absent=_check_from_payload(value.get("exact_numbers_absent"), required=True),
        generated_sport_geometry_absent=_check_from_payload(
            value.get("generated_sport_geometry_absent"), required=True
        ),
    )


def _assert_source_authority(source: Mapping[str, Any]) -> None:
    for field in _REQUIRED_SOURCE_TRUE:
        if source.get(field) is not True:
            raise ValueError(f"QWEN_COMPOSED_SEMANTIC_QA_REQUIRED_GATE_MISSING:{field}")
    for field in _DOWNSTREAM_FALSE:
        if source.get(field) is not False:
            raise ValueError(f"QWEN_COMPOSED_SEMANTIC_QA_PREMATURE_AUTHORITY:{field}")


def _evaluate(verdict: SemanticVisualVerdict) -> tuple[bool, tuple[str, ...], Any]:
    semantic_passed, semantic_blockers = SemanticVisualVerdictGate().evaluate(
        verdict,
        identity_required=False,
        geometry_alignment_required=True,
        exact_numbers_absence_required=True,
        generated_sport_geometry_absence_required=True,
        minimum_confidence=MINIMUM_CONFIDENCE,
    )
    layer = SemanticLayerEvidenceAdapter(minimum_confidence=MINIMUM_CONFIDENCE).adapt(
        verdict,
        require_exact_number_check=True,
        require_sport_geometry_check=True,
    )
    leakage = layer.evidence
    approved = semantic_passed and layer.complete and not any(
        (
            leakage.generated_text_detected,
            leakage.generated_platform_brand_detected,
            leakage.generated_exact_numbers_detected,
            leakage.generated_entity_mark_detected,
            leakage.generated_sport_geometry_detected,
        )
    )
    blockers = tuple(semantic_blockers) + tuple(layer.blockers)
    return approved, blockers, layer


def run_composed_candidate_hybrid_surface_semantic_qa(
    cs272_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
    inspector: Qwen25VLSemanticInspector | None = None,
) -> ComposedCandidateHybridSurfaceSemanticQA:
    """Inspect the exact CS272 composed PNG using the pinned HYBRID_SURFACE stack."""
    if output_dir.exists():
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_OUTPUT_ALREADY_EXISTS")
    if not output_dir.parent.is_dir():
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_OUTPUT_PARENT_INVALID")

    cs272_binding = _bind_file(
        repo_root, cs272_receipt_path, "QWEN_COMPOSED_SEMANTIC_QA_CS272_INVALID"
    )
    source = verify_composed_candidate_byte_admission(
        cs272_receipt_path, repo_root=repo_root
    )
    if source.get("schema") != CS272_SCHEMA:
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_CS272_SCHEMA_DRIFT")
    _assert_source_authority(source)

    story_sha = source.get("story_snapshot_sha256")
    if not _is_sha256(story_sha):
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_STORY_SHA_INVALID")
    composed_meta = source.get("composed_candidate_png")
    if not isinstance(composed_meta, Mapping):
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_COMPOSED_BINDING_INVALID")
    composed_path = _reopen_binding(
        repo_root, composed_meta, "QWEN_COMPOSED_SEMANTIC_QA_COMPOSED_INVALID"
    )

    active_inspector = inspector or Qwen25VLSemanticInspector()
    verdict = active_inspector.inspect_file(
        str(composed_path), stage=SemanticInspectionStage.HYBRID_SURFACE
    )
    expected_verifier_id = (
        f"{QWEN25_VL_VERIFIER_ID}:{SemanticInspectionStage.HYBRID_SURFACE.value}"
    )
    if verdict.verifier_id != expected_verifier_id:
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_VERIFIER_DRIFT")
    approved, blockers, layer = _evaluate(verdict)

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": (
            "QWEN_IMAGE_COMPOSED_CANDIDATE_HYBRID_SURFACE_SEMANTIC_QA_PASSED"
            if approved
            else "QWEN_IMAGE_COMPOSED_CANDIDATE_HYBRID_SURFACE_SEMANTIC_QA_REJECTED"
        ),
        "story_snapshot_sha256": story_sha,
        "source_cs272_receipt": {
            **cs272_binding,
            "receipt_sha256": source.get("receipt_sha256"),
        },
        "composed_candidate_png": dict(composed_meta),
        "semantic_inspector": {
            "model_id": QWEN25_VL_3B_MODEL_ID,
            "model_revision": QWEN25_VL_3B_REVISION,
            "verifier_id": expected_verifier_id,
            "inspection_stage": SemanticInspectionStage.HYBRID_SURFACE.value,
            "minimum_confidence": MINIMUM_CONFIDENCE,
            "process_isolation_expected": True,
        },
        "semantic_verdict": _verdict_payload(verdict),
        "semantic_gate": {
            "passed": approved,
            "blockers": list(blockers),
            "identity_approval_in_scope": False,
            "geometry_alignment_required": True,
            "exact_numbers_absence_required": True,
            "generated_sport_geometry_absence_required": True,
        },
        "semantic_layer_evidence": {
            "complete": layer.complete,
            "blockers": list(layer.blockers),
            "evidence": {
                "generated_text_detected": layer.evidence.generated_text_detected,
                "generated_platform_brand_detected": layer.evidence.generated_platform_brand_detected,
                "generated_exact_numbers_detected": layer.evidence.generated_exact_numbers_detected,
                "generated_entity_mark_detected": layer.evidence.generated_entity_mark_detected,
                "generated_unverified_identity_detected": layer.evidence.generated_unverified_identity_detected,
                "generated_sport_geometry_detected": layer.evidence.generated_sport_geometry_detected,
                "notes": list(layer.evidence.notes),
            },
        },
        "semantic_inspection_executed": True,
        "hybrid_surface_semantic_qa_approved": approved,
        "composition_executed": True,
        "composed_candidate_bytes_admitted_for_post_composition_qa": True,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "genuine_golden_png_created": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "policy": {
            "existing_hybrid_surface_inspection_stage_reused": True,
            "existing_semantic_visual_verdict_gate_reused": True,
            "existing_semantic_layer_evidence_adapter_reused": True,
            "pixel_identity_approval_not_in_scope": True,
            "global_semantic_publication_authority_not_granted": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)

    output_dir.mkdir(mode=0o700)
    receipt_path = output_dir / "composed_candidate_hybrid_surface_semantic_qa.json"
    tmp = output_dir / ".composed_candidate_hybrid_surface_semantic_qa.json.tmp"
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

    return ComposedCandidateHybridSurfaceSemanticQA(
        output_dir=output_dir,
        receipt_path=receipt_path,
        story_snapshot_sha256=story_sha,
        composed_candidate_sha256=str(composed_meta.get("sha256")),
        approved=approved,
    )


def verify_composed_candidate_hybrid_surface_semantic_qa(
    receipt_path: Path, *, repo_root: Path
) -> dict[str, Any]:
    if receipt_path.is_symlink() or not receipt_path.is_file():
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_RECEIPT_INVALID")
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_RECEIPT_INVALID") from exc
    if not isinstance(receipt, dict) or receipt.get("schema") != SCHEMA:
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_SCHEMA_DRIFT")

    claimed = receipt.get("receipt_sha256")
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    if claimed != sha256_json(unsigned):
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_RECEIPT_DIGEST_MISMATCH")

    for field in _DOWNSTREAM_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(f"QWEN_COMPOSED_SEMANTIC_QA_PREMATURE_AUTHORITY:{field}")
    if receipt.get("composition_executed") is not True:
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_COMPOSITION_NOT_EXECUTED")
    if receipt.get("composed_candidate_bytes_admitted_for_post_composition_qa") is not True:
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_BYTES_NOT_ADMITTED")

    source_binding = receipt.get("source_cs272_receipt")
    if not isinstance(source_binding, Mapping):
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_CS272_BINDING_INVALID")
    source_path = _reopen_binding(
        repo_root, source_binding, "QWEN_COMPOSED_SEMANTIC_QA_CS272_INVALID"
    )
    source = verify_composed_candidate_byte_admission(source_path, repo_root=repo_root)
    if source.get("schema") != CS272_SCHEMA:
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_CS272_SCHEMA_DRIFT")
    _assert_source_authority(source)
    if source_binding.get("receipt_sha256") != source.get("receipt_sha256"):
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_CS272_RECEIPT_SHA_DRIFT")
    if receipt.get("story_snapshot_sha256") != source.get("story_snapshot_sha256"):
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_STORY_BINDING_DRIFT")
    if receipt.get("composed_candidate_png") != source.get("composed_candidate_png"):
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_COMPOSED_BINDING_DRIFT")

    composed = receipt.get("composed_candidate_png")
    if not isinstance(composed, Mapping):
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_COMPOSED_BINDING_INVALID")
    _reopen_binding(repo_root, composed, "QWEN_COMPOSED_SEMANTIC_QA_COMPOSED_INVALID")

    inspector_meta = receipt.get("semantic_inspector")
    expected_verifier_id = (
        f"{QWEN25_VL_VERIFIER_ID}:{SemanticInspectionStage.HYBRID_SURFACE.value}"
    )
    if not isinstance(inspector_meta, Mapping) or (
        inspector_meta.get("model_id") != QWEN25_VL_3B_MODEL_ID
        or inspector_meta.get("model_revision") != QWEN25_VL_3B_REVISION
        or inspector_meta.get("verifier_id") != expected_verifier_id
        or inspector_meta.get("inspection_stage") != SemanticInspectionStage.HYBRID_SURFACE.value
        or inspector_meta.get("minimum_confidence") != MINIMUM_CONFIDENCE
    ):
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_INSPECTOR_DRIFT")

    verdict = _verdict_from_payload(receipt.get("semantic_verdict"))
    if verdict.verifier_id != expected_verifier_id:
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_VERIFIER_DRIFT")
    approved, blockers, layer = _evaluate(verdict)
    semantic_gate = receipt.get("semantic_gate")
    layer_payload = receipt.get("semantic_layer_evidence")
    if not isinstance(semantic_gate, Mapping) or not isinstance(layer_payload, Mapping):
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_DECISION_INVALID")
    if (
        semantic_gate.get("passed") is not approved
        or semantic_gate.get("blockers") != list(blockers)
        or semantic_gate.get("geometry_alignment_required") is not True
        or semantic_gate.get("exact_numbers_absence_required") is not True
        or semantic_gate.get("generated_sport_geometry_absence_required") is not True
        or semantic_gate.get("identity_approval_in_scope") is not False
    ):
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_DECISION_DRIFT")
    expected_evidence = {
        "generated_text_detected": layer.evidence.generated_text_detected,
        "generated_platform_brand_detected": layer.evidence.generated_platform_brand_detected,
        "generated_exact_numbers_detected": layer.evidence.generated_exact_numbers_detected,
        "generated_entity_mark_detected": layer.evidence.generated_entity_mark_detected,
        "generated_unverified_identity_detected": layer.evidence.generated_unverified_identity_detected,
        "generated_sport_geometry_detected": layer.evidence.generated_sport_geometry_detected,
        "notes": list(layer.evidence.notes),
    }
    if (
        layer_payload.get("complete") is not layer.complete
        or layer_payload.get("blockers") != list(layer.blockers)
        or layer_payload.get("evidence") != expected_evidence
    ):
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_LAYER_EVIDENCE_DRIFT")
    if receipt.get("semantic_inspection_executed") is not True:
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_INSPECTION_NOT_EXECUTED")
    if receipt.get("hybrid_surface_semantic_qa_approved") is not approved:
        raise ValueError("QWEN_COMPOSED_SEMANTIC_QA_APPROVAL_DRIFT")

    return receipt
