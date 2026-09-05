"""CS345: continue exact CS344 presentation evidence into CS281 final composed approval.

This continuation independently replays CS344, requires its exact admitted CS280
presentation verdict to be approved, derives the exact CS273 semantic-QA receipt through
that CS280 review lineage, and invokes the repository's existing CS281 deterministic
Final Composed Visual Approval contract. It does not execute a new review, alter pixels,
grant final semantic authority, materialize a Genuine Golden PNG, or publish.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Callable, Mapping

from engine.intelligence.qwen_image_final_presentation_review_request_to_evidence_admission import (
    SCHEMA as CS344_SCHEMA,
    verify_final_presentation_review_request_to_evidence_admission,
)
from engine.intelligence.qwen_image_composed_candidate_final_presentation_review_evidence import (
    SCHEMA as CS280_SCHEMA,
    verify_composed_candidate_final_presentation_review_evidence,
)
from engine.intelligence.qwen_image_composed_candidate_final_presentation_review_request import (
    verify_composed_candidate_final_presentation_review_request,
)
from engine.intelligence.qwen_image_composed_candidate_human_visual_review_evidence import (
    verify_composed_candidate_human_visual_review_evidence,
)
from engine.intelligence.qwen_image_composed_candidate_human_visual_review_request import (
    verify_composed_candidate_human_visual_review_request,
)
from engine.intelligence.qwen_image_composed_candidate_golden_quality_adjudication import (
    verify_composed_candidate_golden_quality_adjudication,
)
from engine.intelligence.qwen_image_composed_candidate_visual_quality_review_evidence import (
    verify_composed_candidate_visual_quality_review_evidence,
)
from engine.intelligence.qwen_image_composed_candidate_visual_quality_review_request import (
    verify_composed_candidate_visual_quality_review_request,
)
from engine.intelligence.qwen_image_composed_candidate_hybrid_surface_semantic_qa import (
    SCHEMA as CS273_SCHEMA,
    verify_composed_candidate_hybrid_surface_semantic_qa,
)
from engine.intelligence.qwen_image_composed_candidate_final_composed_visual_approval import (
    SCHEMA as CS281_SCHEMA,
    build_composed_candidate_final_composed_visual_approval,
    verify_composed_candidate_final_composed_visual_approval,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-final-presentation-evidence-to-final-composed-visual-approval-v1"
STATUS = "FINAL_COMPOSED_VISUAL_APPROVED_AWAITING_FINAL_SEMANTIC_APPROVAL"
Verifier = Callable[..., dict[str, Any]]

_UPSTREAM_TRUE = (
    "golden_quality_approved",
    "human_visual_review_approved",
    "final_presentation_review_requested",
    "final_presentation_review_executed",
    "final_presentation_review_evidence_admitted",
    "final_presentation_review_approved",
    "exact_brand_integrity_approved",
    "typography_integrity_approved",
)
_DOWNSTREAM_FALSE = (
    "semantic_approved",
    "genuine_golden_png_created",
    "publication_ready",
)


@dataclass(frozen=True)
class FinalPresentationEvidenceToFinalComposedVisualApprovalRun:
    receipt_path: Path
    cs281_receipt_path: Path


def _json(path: Path, code: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(code)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(code) from exc
    if not isinstance(value, dict):
        raise ValueError(code)
    return value


def _bind(root: Path, path: Path, code: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(code)
    rr, resolved = root.resolve(), path.resolve()
    try:
        rel = resolved.relative_to(rr).as_posix()
    except ValueError as exc:
        raise ValueError(code) from exc
    raw = resolved.read_bytes()
    if not raw:
        raise ValueError(code)
    return {
        "repository_relative_path": rel,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
    }


def _reopen(root: Path, binding: Any, code: str) -> Path:
    if not isinstance(binding, Mapping):
        raise ValueError(code)
    rel = binding.get("repository_relative_path")
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
        raise ValueError(code)
    path = root.resolve() / rel
    current = _bind(root, path, code)
    for key in ("repository_relative_path", "sha256", "byte_size"):
        if current.get(key) != binding.get(key):
            raise ValueError(code + "_BYTE_DRIFT")
    return path


def _verified_child(
    root: Path,
    parent: Mapping[str, Any],
    field: str,
    verifier: Verifier,
    code: str,
) -> tuple[Path, dict[str, Any]]:
    binding = parent.get(field)
    if not isinstance(binding, Mapping):
        raise ValueError(code + "_BINDING_MISSING")
    path = _reopen(root, binding, code)
    child = verifier(path, repo_root=root)
    if binding.get("receipt_sha256") != child.get("receipt_sha256"):
        raise ValueError(code + "_RECEIPT_DRIFT")
    return path, child


def _assert_cs344(value: Mapping[str, Any]) -> None:
    if value.get("schema") != CS344_SCHEMA or value.get("status") != "FINAL_PRESENTATION_REVIEW_EVIDENCE_ADMITTED":
        raise ValueError("CS345_CS344_STATE_INVALID")
    for field in _UPSTREAM_TRUE:
        if value.get(field) is not True:
            raise ValueError(f"CS345_CS344_REQUIRED_GATE_MISSING:{field}")
    if value.get("composed_visual_approved") is not False:
        raise ValueError("CS345_CS344_PREMATURE_AUTHORITY:composed_visual_approved")
    for field in _DOWNSTREAM_FALSE:
        if value.get(field) is not False:
            raise ValueError(f"CS345_CS344_PREMATURE_AUTHORITY:{field}")
    if value.get("authoritative") is not False:
        raise ValueError("CS345_CS344_PREMATURE_AUTHORITY:authoritative")


def _assert_cs280(value: Mapping[str, Any], cs344: Mapping[str, Any]) -> None:
    if value.get("schema") != CS280_SCHEMA:
        raise ValueError("CS345_CS280_SCHEMA_DRIFT")
    if value.get("story_snapshot_sha256") != cs344.get("story_snapshot_sha256"):
        raise ValueError("CS345_CS280_STORY_DRIFT")
    if value.get("composed_candidate_png") != cs344.get("composed_candidate_png"):
        raise ValueError("CS345_CS280_PNG_DRIFT")
    for field in (
        "human_visual_review_approved",
        "final_presentation_review_requested",
        "final_presentation_review_executed",
        "final_presentation_review_evidence_admitted",
        "final_presentation_review_approved",
        "exact_brand_integrity_approved",
        "typography_integrity_approved",
    ):
        if value.get(field) is not True:
            raise ValueError(f"CS345_CS280_REQUIRED_GATE_MISSING:{field}")
    if value.get("composed_visual_approved") is not False:
        raise ValueError("CS345_CS280_PREMATURE_AUTHORITY:composed_visual_approved")
    for field in _DOWNSTREAM_FALSE:
        if value.get(field) is not False:
            raise ValueError(f"CS345_CS280_PREMATURE_AUTHORITY:{field}")


def _derive_exact_cs273(root: Path, cs280: Mapping[str, Any]) -> tuple[Path, dict[str, Any]]:
    _, cs279 = _verified_child(
        root, cs280, "source_cs279_request",
        verify_composed_candidate_final_presentation_review_request,
        "CS345_CS279_INVALID",
    )
    _, cs278 = _verified_child(
        root, cs279, "source_cs278_receipt",
        verify_composed_candidate_human_visual_review_evidence,
        "CS345_CS278_INVALID",
    )
    _, cs277 = _verified_child(
        root, cs278, "source_cs277_request",
        verify_composed_candidate_human_visual_review_request,
        "CS345_CS277_INVALID",
    )
    _, cs276 = _verified_child(
        root, cs277, "source_cs276_receipt",
        verify_composed_candidate_golden_quality_adjudication,
        "CS345_CS276_INVALID",
    )
    _, cs275 = _verified_child(
        root, cs276, "source_cs275_receipt",
        verify_composed_candidate_visual_quality_review_evidence,
        "CS345_CS275_INVALID",
    )
    _, cs274 = _verified_child(
        root, cs275, "source_cs274_request",
        verify_composed_candidate_visual_quality_review_request,
        "CS345_CS274_INVALID",
    )
    path273, cs273 = _verified_child(
        root, cs274, "source_cs273_receipt",
        verify_composed_candidate_hybrid_surface_semantic_qa,
        "CS345_CS273_INVALID",
    )
    if cs273.get("schema") != CS273_SCHEMA:
        raise ValueError("CS345_CS273_SCHEMA_DRIFT")
    return path273, cs273


def _assert_cs273(value: Mapping[str, Any], cs344: Mapping[str, Any]) -> None:
    if value.get("story_snapshot_sha256") != cs344.get("story_snapshot_sha256"):
        raise ValueError("CS345_CS273_STORY_DRIFT")
    if value.get("composed_candidate_png") != cs344.get("composed_candidate_png"):
        raise ValueError("CS345_CS273_PNG_DRIFT")
    for field in (
        "composition_executed",
        "composed_candidate_bytes_admitted_for_post_composition_qa",
        "semantic_inspection_executed",
        "hybrid_surface_semantic_qa_approved",
    ):
        if value.get(field) is not True:
            raise ValueError(f"CS345_CS273_REQUIRED_GATE_MISSING:{field}")


def _assert_cs281(value: Mapping[str, Any], cs344: Mapping[str, Any]) -> None:
    if value.get("schema") != CS281_SCHEMA:
        raise ValueError("CS345_CS281_SCHEMA_DRIFT")
    if value.get("story_snapshot_sha256") != cs344.get("story_snapshot_sha256"):
        raise ValueError("CS345_CS281_STORY_DRIFT")
    if value.get("composed_candidate_png") != cs344.get("composed_candidate_png"):
        raise ValueError("CS345_CS281_PNG_DRIFT")
    if value.get("composed_visual_approved") is not True:
        raise ValueError("CS345_CS281_COMPOSED_APPROVAL_MISSING")
    for field in _DOWNSTREAM_FALSE:
        if value.get(field) is not False:
            raise ValueError(f"CS345_CS281_PREMATURE_AUTHORITY:{field}")


def continue_final_presentation_evidence_to_final_composed_visual_approval(
    cs344_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> FinalPresentationEvidenceToFinalComposedVisualApprovalRun:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    try:
        output_dir.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError("CS345_OUTPUT_INVALID") from exc
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("CS345_OUTPUT_INVALID")

    b344 = _bind(repo_root, cs344_receipt_path, "CS345_CS344_RECEIPT_INVALID")
    cs344 = verify_final_presentation_review_request_to_evidence_admission(
        cs344_receipt_path,
        repo_root=repo_root,
    )
    _assert_cs344(cs344)

    b280 = cs344.get("cs280_receipt")
    p280 = _reopen(repo_root, b280, "CS345_CS280_RECEIPT_INVALID")
    cs280 = verify_composed_candidate_final_presentation_review_evidence(p280, repo_root=repo_root)
    if not isinstance(b280, Mapping) or b280.get("receipt_sha256") != cs280.get("receipt_sha256"):
        raise ValueError("CS345_CS280_RECEIPT_DRIFT")
    _assert_cs280(cs280, cs344)

    p273, cs273 = _derive_exact_cs273(repo_root, cs280)
    _assert_cs273(cs273, cs344)

    output_dir.mkdir(mode=0o700)
    cs281_dir = output_dir / "cs281"
    p281 = build_composed_candidate_final_composed_visual_approval(
        p273,
        p280,
        cs281_dir,
        repo_root=repo_root,
    )
    cs281 = verify_composed_candidate_final_composed_visual_approval(p281, repo_root=repo_root)
    _assert_cs281(cs281, cs344)

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "story_snapshot_sha256": cs344["story_snapshot_sha256"],
        "candidate_png": dict(cs344["candidate_png"]),
        "composed_candidate_png": dict(cs344["composed_candidate_png"]),
        "source_cs344_receipt": b344,
        "cs280_receipt": dict(b280),
        "cs273_receipt": {
            **_bind(repo_root, p273, "CS345_CS273_RECEIPT_INVALID"),
            "receipt_sha256": cs273.get("receipt_sha256"),
        },
        "cs281_receipt": {
            **_bind(repo_root, p281, "CS345_CS281_RECEIPT_INVALID"),
            "receipt_sha256": cs281.get("receipt_sha256"),
        },
        "golden_quality_approved": True,
        "human_visual_review_approved": True,
        "final_presentation_review_approved": True,
        "exact_brand_integrity_approved": True,
        "typography_integrity_approved": True,
        "composed_visual_approved": True,
        "semantic_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "authoritative": False,
        "policy": {
            "exact_cs344_replayed": True,
            "exact_cs344_selected_cs280_replayed": True,
            "presentation_rejection_blocks_progression_fail_closed": True,
            "exact_cs280_review_lineage_replayed_back_to_cs273": True,
            "exact_cs273_semantic_qa_required": True,
            "existing_cs281_final_composed_approval_contract_reused": True,
            "no_new_visual_review_or_pixel_mutation_here": True,
            "final_semantic_approval_remains_independent": True,
            "semantic_publication_gate_remains_independent": True,
            "genuine_golden_png_not_created_here": True,
            "publication_authority_not_granted": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    path = output_dir / "final_presentation_evidence_to_final_composed_visual_approval.json"
    tmp = output_dir / ".final_presentation_evidence_to_final_composed_visual_approval.json.tmp"
    try:
        with tmp.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise

    return FinalPresentationEvidenceToFinalComposedVisualApprovalRun(
        receipt_path=path,
        cs281_receipt_path=p281,
    )


def verify_final_presentation_evidence_to_final_composed_visual_approval(
    receipt_path: Path,
    *,
    repo_root: Path,
) -> dict[str, Any]:
    receipt = _json(receipt_path, "CS345_RECEIPT_INVALID")
    unsigned = dict(receipt)
    claimed = unsigned.pop("receipt_sha256", None)
    if receipt.get("schema") != SCHEMA or receipt.get("status") != STATUS or claimed != sha256_json(unsigned):
        raise ValueError("CS345_RECEIPT_INVALID")

    for field in (
        "golden_quality_approved",
        "human_visual_review_approved",
        "final_presentation_review_approved",
        "exact_brand_integrity_approved",
        "typography_integrity_approved",
        "composed_visual_approved",
    ):
        if receipt.get(field) is not True:
            raise ValueError(f"CS345_STATE_DRIFT:{field}")
    for field in _DOWNSTREAM_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(f"CS345_PREMATURE_AUTHORITY:{field}")
    if receipt.get("authoritative") is not False:
        raise ValueError("CS345_PREMATURE_AUTHORITY:authoritative")

    p344 = _reopen(repo_root, receipt.get("source_cs344_receipt"), "CS345_CS344_RECEIPT_INVALID")
    cs344 = verify_final_presentation_review_request_to_evidence_admission(p344, repo_root=repo_root)
    _assert_cs344(cs344)
    if (
        receipt.get("story_snapshot_sha256") != cs344.get("story_snapshot_sha256")
        or receipt.get("candidate_png") != cs344.get("candidate_png")
        or receipt.get("composed_candidate_png") != cs344.get("composed_candidate_png")
        or receipt.get("cs280_receipt") != cs344.get("cs280_receipt")
    ):
        raise ValueError("CS345_CS344_LINEAGE_DRIFT")

    b280 = receipt.get("cs280_receipt")
    p280 = _reopen(repo_root, b280, "CS345_CS280_RECEIPT_INVALID")
    cs280 = verify_composed_candidate_final_presentation_review_evidence(p280, repo_root=repo_root)
    if not isinstance(b280, Mapping) or b280.get("receipt_sha256") != cs280.get("receipt_sha256"):
        raise ValueError("CS345_CS280_RECEIPT_DRIFT")
    _assert_cs280(cs280, cs344)

    p273, cs273 = _derive_exact_cs273(repo_root, cs280)
    _assert_cs273(cs273, cs344)
    expected273 = {
        **_bind(repo_root, p273, "CS345_CS273_RECEIPT_INVALID"),
        "receipt_sha256": cs273.get("receipt_sha256"),
    }
    if receipt.get("cs273_receipt") != expected273:
        raise ValueError("CS345_CS273_LINEAGE_DRIFT")

    b281 = receipt.get("cs281_receipt")
    p281 = _reopen(repo_root, b281, "CS345_CS281_RECEIPT_INVALID")
    cs281 = verify_composed_candidate_final_composed_visual_approval(p281, repo_root=repo_root)
    if not isinstance(b281, Mapping) or b281.get("receipt_sha256") != cs281.get("receipt_sha256"):
        raise ValueError("CS345_CS281_RECEIPT_DRIFT")
    _assert_cs281(cs281, cs344)

    expected280 = cs281.get("source_cs280_final_presentation_evidence")
    if not isinstance(expected280, Mapping):
        raise ValueError("CS345_CS281_CS280_BINDING_MISSING")
    for key in ("repository_relative_path", "sha256", "byte_size", "receipt_sha256"):
        if expected280.get(key) != b280.get(key):
            raise ValueError("CS345_CS281_CS280_LINEAGE_DRIFT")
    expected281_cs273 = cs281.get("source_cs273_semantic_qa")
    if not isinstance(expected281_cs273, Mapping):
        raise ValueError("CS345_CS281_CS273_BINDING_MISSING")
    for key in ("repository_relative_path", "sha256", "byte_size", "receipt_sha256"):
        if expected281_cs273.get(key) != expected273.get(key):
            raise ValueError("CS345_CS281_CS273_LINEAGE_DRIFT")
    return receipt
