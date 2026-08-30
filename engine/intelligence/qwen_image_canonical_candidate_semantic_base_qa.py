"""Byte-bound semantic base-scene QA for a CS263 canonical candidate.

Change Set 264 consumes the exact candidate bytes admitted by CS263 and runs the
existing pinned Qwen2.5-VL semantic inspector in BASE_SCENE mode.  Its verdict is
then evaluated by the existing SemanticVisualVerdictGate and converted through
the existing SemanticLayerEvidenceAdapter.  This module intentionally does not
claim identity approval, Human Review, Golden quality, branding, or publication
readiness.
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
from engine.intelligence.qwen_image_canonical_candidate_byte_admission import (
    CANONICAL_CANDIDATE_BYTE_ADMISSION_SCHEMA,
    verify_canonical_candidate_byte_admission,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json
from engine.intelligence.semantic_layer_evidence import SemanticLayerEvidenceAdapter
from engine.intelligence.semantic_visual_verdict import (
    InspectionState,
    SemanticCheck,
    SemanticVisualVerdict,
    SemanticVisualVerdictGate,
)

CANONICAL_CANDIDATE_SEMANTIC_BASE_QA_SCHEMA = (
    "pul7sar-phase18-qwen-image-canonical-candidate-semantic-base-qa-v1"
)
MINIMUM_CONFIDENCE = 0.85
_REQUIRED_SOURCE_TRUE = (
    "production_semantic_replay_executed",
    "fresh_story_gates_passed",
    "controlled_trial_preflight_valid",
    "canonical_generation_authorized",
    "inference_executed",
    "genuine_canonical_inference_executed",
    "candidate_bytes_admitted_for_post_generation_qa",
)
_REQUIRED_FALSE = (
    "genuine_golden_png_created",
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "publication_ready",
)


@dataclass(frozen=True)
class CanonicalCandidateSemanticBaseQA:
    output_dir: Path
    receipt_path: Path
    story_snapshot_sha256: str
    candidate_sha256: str
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


def _binding(path: Path, code: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(code)
    raw = path.read_bytes()
    if not raw:
        raise ValueError(code)
    return {"sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw)}


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
            raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_VERDICT_INCOMPLETE")
        return None
    if not isinstance(value, Mapping):
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_VERDICT_INVALID")
    try:
        state = InspectionState(str(value["state"]))
        confidence = float(value["confidence"])
        detail = str(value.get("detail") or "")
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_VERDICT_INVALID") from exc
    return SemanticCheck(state=state, confidence=confidence, detail=detail)


def _verdict_from_payload(value: Any) -> SemanticVisualVerdict:
    if not isinstance(value, Mapping):
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_VERDICT_INVALID")
    verifier_id = value.get("verifier_id")
    if not isinstance(verifier_id, str) or not verifier_id:
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_VERIFIER_INVALID")
    return SemanticVisualVerdict(
        verifier_id=verifier_id,
        readable_text_absent=_check_from_payload(value.get("readable_text_absent"), required=True),
        platform_brand_absent=_check_from_payload(value.get("platform_brand_absent"), required=True),
        fake_entity_marks_absent=_check_from_payload(value.get("fake_entity_marks_absent"), required=True),
        single_scene=_check_from_payload(value.get("single_scene"), required=True),
        severe_defects_absent=_check_from_payload(value.get("severe_defects_absent"), required=True),
        subject_framing_valid=_check_from_payload(value.get("subject_framing_valid"), required=True),
        sport_geometry_alignment_valid=_check_from_payload(value.get("sport_geometry_alignment_valid"), required=False),
        identity_valid=_check_from_payload(value.get("identity_valid"), required=False),
        exact_numbers_absent=_check_from_payload(value.get("exact_numbers_absent"), required=True),
        generated_sport_geometry_absent=_check_from_payload(value.get("generated_sport_geometry_absent"), required=True),
    )


def _assert_source_authority(source: Mapping[str, Any]) -> None:
    for field in _REQUIRED_SOURCE_TRUE:
        if source.get(field) is not True:
            raise ValueError(f"QWEN_CANDIDATE_SEMANTIC_QA_REQUIRED_GATE_MISSING:{field}")
    for field in _REQUIRED_FALSE:
        if source.get(field) is not False:
            raise ValueError(f"QWEN_CANDIDATE_SEMANTIC_QA_PREMATURE_AUTHORITY:{field}")


def _evaluate(verdict: SemanticVisualVerdict) -> tuple[bool, tuple[str, ...], Any]:
    semantic_passed, semantic_blockers = SemanticVisualVerdictGate().evaluate(
        verdict,
        identity_required=False,
        geometry_alignment_required=False,
        exact_numbers_absence_required=True,
        generated_sport_geometry_absence_required=True,
        minimum_confidence=MINIMUM_CONFIDENCE,
    )
    layer = SemanticLayerEvidenceAdapter(minimum_confidence=MINIMUM_CONFIDENCE).adapt(
        verdict,
        require_exact_number_check=True,
        require_sport_geometry_check=True,
    )
    approved = semantic_passed and layer.complete and not any(
        (
            layer.evidence.generated_text_detected,
            layer.evidence.generated_platform_brand_detected,
            layer.evidence.generated_exact_numbers_detected,
            layer.evidence.generated_entity_mark_detected,
            layer.evidence.generated_sport_geometry_detected,
        )
    )
    blockers = tuple(semantic_blockers) + tuple(layer.blockers)
    return approved, blockers, layer


def run_canonical_candidate_semantic_base_qa(
    cs263_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
    inspector: Qwen25VLSemanticInspector | None = None,
) -> CanonicalCandidateSemanticBaseQA:
    """Inspect the exact CS263 PNG using the existing pinned semantic QA stack."""
    if output_dir.exists():
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_OUTPUT_ALREADY_EXISTS")
    if not output_dir.parent.is_dir():
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_OUTPUT_PARENT_INVALID")

    source_relative = _inside_repo_file(
        repo_root,
        cs263_receipt_path,
        "QWEN_CANDIDATE_SEMANTIC_QA_CS263_OUTSIDE_REPOSITORY",
    )
    source_binding = _binding(
        cs263_receipt_path, "QWEN_CANDIDATE_SEMANTIC_QA_CS263_INVALID"
    )
    source = verify_canonical_candidate_byte_admission(
        cs263_receipt_path, repo_root=repo_root
    )
    if source.get("schema") != CANONICAL_CANDIDATE_BYTE_ADMISSION_SCHEMA:
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_CS263_SCHEMA_DRIFT")
    _assert_source_authority(source)

    story_sha = source.get("story_snapshot_sha256")
    if not _is_sha256(story_sha):
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_STORY_SHA_INVALID")
    candidate_meta = source.get("candidate_png")
    if not isinstance(candidate_meta, Mapping):
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_CANDIDATE_BINDING_INVALID")
    candidate_rel = candidate_meta.get("repository_relative_path")
    if (
        not isinstance(candidate_rel, str)
        or not candidate_rel
        or Path(candidate_rel).is_absolute()
        or ".." in Path(candidate_rel).parts
    ):
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_CANDIDATE_PATH_INVALID")
    candidate_path = repo_root.resolve() / candidate_rel
    canonical_rel = _inside_repo_file(
        repo_root,
        candidate_path,
        "QWEN_CANDIDATE_SEMANTIC_QA_CANDIDATE_OUTSIDE_REPOSITORY",
    )
    if canonical_rel != Path(candidate_rel).as_posix():
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_CANDIDATE_PATH_DRIFT")
    candidate_binding = _binding(
        candidate_path, "QWEN_CANDIDATE_SEMANTIC_QA_CANDIDATE_INVALID"
    )
    if (
        candidate_meta.get("sha256") != candidate_binding["sha256"]
        or candidate_meta.get("byte_size") != candidate_binding["byte_size"]
    ):
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_CANDIDATE_BYTE_DRIFT")

    active_inspector = inspector or Qwen25VLSemanticInspector()
    verdict = active_inspector.inspect_file(
        str(candidate_path), stage=SemanticInspectionStage.BASE_SCENE
    )
    expected_verifier_id = f"{QWEN25_VL_VERIFIER_ID}:{SemanticInspectionStage.BASE_SCENE.value}"
    if verdict.verifier_id != expected_verifier_id:
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_VERIFIER_DRIFT")
    approved, blockers, layer = _evaluate(verdict)

    layer_evidence = {
        "generated_text_detected": layer.evidence.generated_text_detected,
        "generated_platform_brand_detected": layer.evidence.generated_platform_brand_detected,
        "generated_exact_numbers_detected": layer.evidence.generated_exact_numbers_detected,
        "generated_entity_mark_detected": layer.evidence.generated_entity_mark_detected,
        "generated_unverified_identity_detected": layer.evidence.generated_unverified_identity_detected,
        "generated_sport_geometry_detected": layer.evidence.generated_sport_geometry_detected,
        "notes": list(layer.evidence.notes),
    }
    receipt = {
        "schema": CANONICAL_CANDIDATE_SEMANTIC_BASE_QA_SCHEMA,
        "status": (
            "QWEN_IMAGE_CANONICAL_CANDIDATE_SEMANTIC_BASE_QA_PASSED"
            if approved
            else "QWEN_IMAGE_CANONICAL_CANDIDATE_SEMANTIC_BASE_QA_REJECTED"
        ),
        "story_snapshot_sha256": story_sha,
        "source_cs263_receipt": {
            "repository_relative_path": source_relative,
            **source_binding,
            "receipt_sha256": source.get("receipt_sha256"),
        },
        "candidate_png": {
            "repository_relative_path": canonical_rel,
            **candidate_binding,
            "width": candidate_meta.get("width"),
            "height": candidate_meta.get("height"),
        },
        "semantic_inspector": {
            "model_id": QWEN25_VL_3B_MODEL_ID,
            "model_revision": QWEN25_VL_3B_REVISION,
            "verifier_id": expected_verifier_id,
            "inspection_stage": SemanticInspectionStage.BASE_SCENE.value,
            "minimum_confidence": MINIMUM_CONFIDENCE,
            "process_isolation_expected": True,
        },
        "semantic_verdict": _verdict_payload(verdict),
        "semantic_gate": {
            "passed": approved,
            "blockers": list(blockers),
            "identity_approval_in_scope": False,
            "exact_numbers_absence_required": True,
            "generated_sport_geometry_absence_required": True,
        },
        "semantic_layer_evidence": {
            "complete": layer.complete,
            "blockers": list(layer.blockers),
            "evidence": layer_evidence,
        },
        "semantic_inspection_executed": True,
        "semantic_base_scene_approved": approved,
        "identity_approved": False,
        "candidate_bytes_admitted_for_post_generation_qa": True,
        "genuine_golden_png_created": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
    }
    receipt["receipt_sha256"] = sha256_json(receipt)

    output_dir.mkdir(mode=0o700)
    receipt_path = output_dir / "canonical_candidate_semantic_base_qa_receipt.json"
    tmp = output_dir / ".canonical_candidate_semantic_base_qa_receipt.json.tmp"
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

    return CanonicalCandidateSemanticBaseQA(
        output_dir=output_dir,
        receipt_path=receipt_path,
        story_snapshot_sha256=story_sha,
        candidate_sha256=candidate_binding["sha256"],
        approved=approved,
    )


def verify_canonical_candidate_semantic_base_qa(
    receipt_path: Path, *, repo_root: Path
) -> dict[str, Any]:
    """Replay CS263/candidate byte bindings and recompute the semantic decision."""
    if receipt_path.is_symlink() or not receipt_path.is_file():
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_RECEIPT_INVALID")
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_RECEIPT_INVALID") from exc
    if not isinstance(receipt, dict):
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_RECEIPT_INVALID")
    if receipt.get("schema") != CANONICAL_CANDIDATE_SEMANTIC_BASE_QA_SCHEMA:
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_SCHEMA_DRIFT")
    claimed = receipt.get("receipt_sha256")
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    if not _is_sha256(claimed) or sha256_json(unsigned) != claimed:
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_RECEIPT_DIGEST_MISMATCH")
    for field in _REQUIRED_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(f"QWEN_CANDIDATE_SEMANTIC_QA_PREMATURE_AUTHORITY:{field}")
    if receipt.get("identity_approved") is not False:
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_IDENTITY_AUTHORITY_FORBIDDEN")

    inspector_meta = receipt.get("semantic_inspector")
    if not isinstance(inspector_meta, Mapping):
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_INSPECTOR_BINDING_INVALID")
    expected_verifier_id = f"{QWEN25_VL_VERIFIER_ID}:{SemanticInspectionStage.BASE_SCENE.value}"
    expected_inspector = {
        "model_id": QWEN25_VL_3B_MODEL_ID,
        "model_revision": QWEN25_VL_3B_REVISION,
        "verifier_id": expected_verifier_id,
        "inspection_stage": SemanticInspectionStage.BASE_SCENE.value,
        "minimum_confidence": MINIMUM_CONFIDENCE,
        "process_isolation_expected": True,
    }
    if dict(inspector_meta) != expected_inspector:
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_INSPECTOR_DRIFT")

    source_meta = receipt.get("source_cs263_receipt")
    candidate_meta = receipt.get("candidate_png")
    if not isinstance(source_meta, Mapping) or not isinstance(candidate_meta, Mapping):
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_BINDING_INVALID")
    source_rel = source_meta.get("repository_relative_path")
    candidate_rel = candidate_meta.get("repository_relative_path")
    for rel, label in ((source_rel, "CS263"), (candidate_rel, "CANDIDATE")):
        if (
            not isinstance(rel, str)
            or not rel
            or Path(rel).is_absolute()
            or ".." in Path(rel).parts
        ):
            raise ValueError(f"QWEN_CANDIDATE_SEMANTIC_QA_{label}_PATH_INVALID")
    source_path = repo_root.resolve() / source_rel
    candidate_path = repo_root.resolve() / candidate_rel
    if _inside_repo_file(repo_root, source_path, "QWEN_CANDIDATE_SEMANTIC_QA_CS263_OUTSIDE_REPOSITORY") != Path(source_rel).as_posix():
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_CS263_PATH_DRIFT")
    if _inside_repo_file(repo_root, candidate_path, "QWEN_CANDIDATE_SEMANTIC_QA_CANDIDATE_OUTSIDE_REPOSITORY") != Path(candidate_rel).as_posix():
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_CANDIDATE_PATH_DRIFT")
    current_source = _binding(source_path, "QWEN_CANDIDATE_SEMANTIC_QA_CS263_INVALID")
    current_candidate = _binding(candidate_path, "QWEN_CANDIDATE_SEMANTIC_QA_CANDIDATE_INVALID")
    if source_meta.get("sha256") != current_source["sha256"] or source_meta.get("byte_size") != current_source["byte_size"]:
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_CS263_BYTE_DRIFT")
    if candidate_meta.get("sha256") != current_candidate["sha256"] or candidate_meta.get("byte_size") != current_candidate["byte_size"]:
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_CANDIDATE_BYTE_DRIFT")

    source = verify_canonical_candidate_byte_admission(source_path, repo_root=repo_root)
    _assert_source_authority(source)
    if source.get("receipt_sha256") != source_meta.get("receipt_sha256"):
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_CS263_DIGEST_DRIFT")
    if source.get("story_snapshot_sha256") != receipt.get("story_snapshot_sha256"):
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_CROSS_STORY")
    source_candidate = source.get("candidate_png")
    if not isinstance(source_candidate, Mapping) or source_candidate.get("sha256") != current_candidate["sha256"]:
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_CANDIDATE_BINDING_DRIFT")

    verdict = _verdict_from_payload(receipt.get("semantic_verdict"))
    if verdict.verifier_id != expected_verifier_id:
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_VERIFIER_DRIFT")
    approved, blockers, layer = _evaluate(verdict)
    semantic_gate = receipt.get("semantic_gate")
    layer_receipt = receipt.get("semantic_layer_evidence")
    if not isinstance(semantic_gate, Mapping) or not isinstance(layer_receipt, Mapping):
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_DECISION_BINDING_INVALID")
    if semantic_gate.get("passed") is not approved or semantic_gate.get("blockers") != list(blockers):
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_DECISION_DRIFT")
    if layer_receipt.get("complete") is not layer.complete or layer_receipt.get("blockers") != list(layer.blockers):
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_LAYER_DECISION_DRIFT")
    if receipt.get("semantic_inspection_executed") is not True:
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_EXECUTION_NOT_PROVEN")
    if receipt.get("semantic_base_scene_approved") is not approved:
        raise ValueError("QWEN_CANDIDATE_SEMANTIC_QA_APPROVAL_DRIFT")
    return receipt
