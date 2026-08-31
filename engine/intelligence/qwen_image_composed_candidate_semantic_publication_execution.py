"""CS284: execute the repository SemanticPublicationGate from explicit, byte-bound evidence.

This stage never accepts an externally supplied publication verdict. It re-verifies CS283,
reconstructs the exact GenerationPackage, BaseSceneEvidence and zero-cost VisionVerifierProfile
from an external JSON evidence file, executes SemanticPublicationGate, and records the real
decision while keeping Genuine-Golden creation/publication readiness closed for downstream authority.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.base_scene_quality import (
    BaseSceneEvidence, GenerationDefectEvidence, IdentityVisualEvidence,
    ProtectedRegionEvidence, SubjectFramingEvidence,
)
from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.qwen_image_composed_candidate_semantic_publication_execution_request import (
    SCHEMA as CS283_SCHEMA, verify_semantic_publication_execution_request,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json
from engine.intelligence.semantic_publication_gate import SemanticPublicationGate
from engine.intelligence.vision_verification_policy import VisionVerificationCapability, VisionVerifierProfile

SCHEMA = "pul7sar-phase18-qwen-image-composed-candidate-semantic-publication-execution-v1"
STATUS = "QWEN_IMAGE_COMPOSED_CANDIDATE_SEMANTIC_PUBLICATION_GATE_EXECUTED"


def _json(path: Path, code: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file(): raise ValueError(code)
    try: value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc: raise ValueError(code) from exc
    if not isinstance(value, dict): raise ValueError(code)
    return value


def _bind(root: Path, path: Path, code: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file(): raise ValueError(code)
    resolved = path.resolve()
    try: relative = resolved.relative_to(root.resolve()).as_posix()
    except ValueError as exc: raise ValueError(code) from exc
    raw = resolved.read_bytes()
    if not raw: raise ValueError(code)
    return {"repository_relative_path": relative, "sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw)}


def _reopen(root: Path, binding: Mapping[str, Any], code: str) -> Path:
    relative = binding.get("repository_relative_path")
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or ".." in Path(relative).parts: raise ValueError(code)
    path = root.resolve() / relative
    current = _bind(root, path, code)
    for field in ("repository_relative_path", "sha256", "byte_size"):
        if current[field] != binding.get(field): raise ValueError(f"{code}_BYTE_DRIFT")
    return path


def _package(raw: Mapping[str, Any]) -> GenerationPackage:
    return GenerationPackage(
        platform=str(raw["platform"]), canvas=str(raw["canvas"]), scene_prompt=str(raw["scene_prompt"]),
        negative_constraints=tuple(raw.get("negative_constraints", ())), asset_ids=tuple(raw.get("asset_ids", ())),
        factual_constraints=tuple(raw.get("factual_constraints", ())), layout_boxes=dict(raw.get("layout_boxes", {})),
        accent_hex=raw.get("accent_hex"), metadata=dict(raw.get("metadata", {})),
    )


def _evidence(raw: Mapping[str, Any]) -> BaseSceneEvidence:
    framing = raw["framing"]; identity = raw["identity"]; defects = raw["defects"]
    return BaseSceneEvidence(
        provider_id=str(raw["provider_id"]), output_ref=str(raw["output_ref"]), width=int(raw["width"]), height=int(raw["height"]),
        aspect_ratio=str(raw["aspect_ratio"]),
        framing=SubjectFramingEvidence(bool(framing["subject_present"]), bool(framing["fully_visible_as_required"]), bool(framing["hero_region_clear"]), float(framing["confidence"])),
        identity=IdentityVisualEvidence(bool(identity["required"]), bool(identity["matched"]), float(identity["confidence"]), tuple(identity.get("reference_ids", ()))),
        protected_regions=tuple(ProtectedRegionEvidence(str(item["role"]), bool(item["sufficiently_clear"]), float(item["occupancy_ratio"])) for item in raw.get("protected_regions", ())),
        defects=GenerationDefectEvidence(bool(defects["defect_free"]), tuple(defects.get("defects", ()))),
        forbidden_visuals_detected=tuple(raw.get("forbidden_visuals_detected", ())), safe_crop_possible=bool(raw.get("safe_crop_possible", True)),
        provenance=dict(raw.get("provenance", {})),
    )


def _verifier(raw: Mapping[str, Any]) -> VisionVerifierProfile:
    try: capabilities = frozenset(VisionVerificationCapability(item) for item in raw.get("capabilities", ()))
    except ValueError as exc: raise ValueError("QWEN_SEMANTIC_PUBLICATION_EXECUTION_VERIFIER_CAPABILITY_INVALID") from exc
    return VisionVerifierProfile(str(raw["verifier_id"]), bool(raw["local_zero_cost"]), capabilities, bool(raw.get("requires_network", False)), tuple(raw.get("notes", ())))


def execute_semantic_publication_gate(cs283_receipt_path: Path, evidence_path: Path, output_dir: Path, *, repo_root: Path) -> Path:
    if output_dir.exists() or not output_dir.parent.is_dir(): raise ValueError("QWEN_SEMANTIC_PUBLICATION_EXECUTION_OUTPUT_INVALID")
    cs283_binding = _bind(repo_root, cs283_receipt_path, "QWEN_SEMANTIC_PUBLICATION_EXECUTION_CS283_INVALID")
    cs283 = verify_semantic_publication_execution_request(cs283_receipt_path, repo_root=repo_root)
    if cs283.get("schema") != CS283_SCHEMA or cs283.get("semantic_publication_execution_requested") is not True: raise ValueError("QWEN_SEMANTIC_PUBLICATION_EXECUTION_CS283_STATE_INVALID")
    evidence_binding = _bind(repo_root, evidence_path, "QWEN_SEMANTIC_PUBLICATION_EXECUTION_EVIDENCE_INVALID")
    raw = _json(evidence_path, "QWEN_SEMANTIC_PUBLICATION_EXECUTION_EVIDENCE_INVALID")
    if raw.get("story_snapshot_sha256") != cs283.get("story_snapshot_sha256"): raise ValueError("QWEN_SEMANTIC_PUBLICATION_EXECUTION_STORY_DRIFT")
    if raw.get("composed_candidate_png_sha256") != cs283["composed_candidate_png"].get("sha256"): raise ValueError("QWEN_SEMANTIC_PUBLICATION_EXECUTION_PNG_DRIFT")
    package_raw, base_raw, verifier_raw = raw.get("generation_package"), raw.get("base_scene_evidence"), raw.get("vision_verifier_profile")
    if not all(isinstance(item, Mapping) for item in (package_raw, base_raw, verifier_raw)): raise ValueError("QWEN_SEMANTIC_PUBLICATION_EXECUTION_INPUTS_INVALID")
    package, base, verifier = _package(package_raw), _evidence(base_raw), _verifier(verifier_raw)
    decision = SemanticPublicationGate().evaluate(package, base, verifier)
    receipt: dict[str, Any] = {
        "schema": SCHEMA, "status": STATUS, "story_snapshot_sha256": cs283["story_snapshot_sha256"],
        "source_cs283_semantic_publication_request": {**cs283_binding, "receipt_sha256": cs283.get("receipt_sha256")},
        "semantic_publication_execution_evidence": evidence_binding,
        "composed_candidate_png": dict(cs283["composed_candidate_png"]), "generation_context": dict(cs283["generation_context"]),
        "weighted_score": cs283["weighted_score"], "quality_tier": cs283["quality_tier"],
        "composed_visual_approved": True, "semantic_approved": True,
        "semantic_publication_execution_requested": True, "semantic_publication_gate_executed": True,
        "semantic_publication_allowed": bool(decision.allowed), "base_scene_accepted": bool(decision.base_scene_accepted),
        "semantic_verifier_eligible": bool(decision.semantic_verifier_eligible), "semantic_publication_failures": list(decision.failures),
        "semantic_publication_warnings": list(decision.warnings), "genuine_golden_png_created": False, "publication_ready": False,
        "policy": {"decision_must_come_from_repository_semantic_publication_gate": True, "external_allowed_override_forbidden": True,
                   "gate_success_does_not_create_genuine_golden_png": True, "gate_success_does_not_set_publication_ready": True},
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    output_dir.mkdir(mode=0o700)
    path = output_dir / "semantic_publication_execution.json"; tmp = output_dir / ".semantic_publication_execution.json.tmp"
    try:
        with tmp.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n"); handle.flush(); os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        if tmp.exists(): tmp.unlink()
        if output_dir.exists() and not any(output_dir.iterdir()): output_dir.rmdir()
        raise
    return path


def verify_semantic_publication_execution(receipt_path: Path, *, repo_root: Path) -> dict[str, Any]:
    receipt = _json(receipt_path, "QWEN_SEMANTIC_PUBLICATION_EXECUTION_RECEIPT_INVALID")
    unsigned = dict(receipt); claimed = unsigned.pop("receipt_sha256", None)
    if receipt.get("schema") != SCHEMA or receipt.get("status") != STATUS or claimed != sha256_json(unsigned): raise ValueError("QWEN_SEMANTIC_PUBLICATION_EXECUTION_RECEIPT_INVALID")
    source = receipt.get("source_cs283_semantic_publication_request")
    if not isinstance(source, Mapping): raise ValueError("QWEN_SEMANTIC_PUBLICATION_EXECUTION_CS283_BINDING_INVALID")
    cs283_path = _reopen(repo_root, source, "QWEN_SEMANTIC_PUBLICATION_EXECUTION_CS283_INVALID")
    cs283 = verify_semantic_publication_execution_request(cs283_path, repo_root=repo_root)
    if source.get("receipt_sha256") != cs283.get("receipt_sha256"): raise ValueError("QWEN_SEMANTIC_PUBLICATION_EXECUTION_CS283_RECEIPT_DRIFT")
    evidence_binding = receipt.get("semantic_publication_execution_evidence")
    if not isinstance(evidence_binding, Mapping): raise ValueError("QWEN_SEMANTIC_PUBLICATION_EXECUTION_EVIDENCE_BINDING_INVALID")
    evidence_path = _reopen(repo_root, evidence_binding, "QWEN_SEMANTIC_PUBLICATION_EXECUTION_EVIDENCE_INVALID")
    raw = _json(evidence_path, "QWEN_SEMANTIC_PUBLICATION_EXECUTION_EVIDENCE_INVALID")
    package, base, verifier = _package(raw["generation_package"]), _evidence(raw["base_scene_evidence"]), _verifier(raw["vision_verifier_profile"])
    decision = SemanticPublicationGate().evaluate(package, base, verifier)
    expected = {"story_snapshot_sha256": cs283["story_snapshot_sha256"], "composed_candidate_png": dict(cs283["composed_candidate_png"]),
                "semantic_publication_gate_executed": True, "semantic_publication_allowed": bool(decision.allowed),
                "base_scene_accepted": bool(decision.base_scene_accepted), "semantic_verifier_eligible": bool(decision.semantic_verifier_eligible),
                "semantic_publication_failures": list(decision.failures), "semantic_publication_warnings": list(decision.warnings),
                "genuine_golden_png_created": False, "publication_ready": False}
    for field, value in expected.items():
        if receipt.get(field) != value: raise ValueError(f"QWEN_SEMANTIC_PUBLICATION_EXECUTION_STATE_DRIFT:{field}")
    return receipt
