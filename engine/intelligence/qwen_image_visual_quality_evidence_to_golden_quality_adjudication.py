"""CS340: continue one exact CS339 evidence admission into CS276 adjudication.

The continuation derives the exact CS272 and sealed canonical candidate admission
already represented by the admitted CS275 lineage, runs the existing CS276
Golden-quality adjudicator once, independently reverifies it, and stops before
Human Review, presentation/brand approval, final semantic approval, Genuine
Golden PNG creation, or publication.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Callable, Mapping

from engine.intelligence.qwen_image_visual_quality_review_request_to_evidence_admission import (
    SCHEMA as CS339_SCHEMA,
    verify_visual_quality_review_request_to_evidence_admission,
)
from engine.intelligence.qwen_image_composed_candidate_visual_quality_review_evidence import (
    verify_composed_candidate_visual_quality_review_evidence,
)
from engine.intelligence.qwen_image_composed_candidate_visual_quality_review_request import (
    verify_composed_candidate_visual_quality_review_request,
)
from engine.intelligence.qwen_image_composed_candidate_hybrid_surface_semantic_qa import (
    verify_composed_candidate_hybrid_surface_semantic_qa,
)
from engine.intelligence.qwen_image_composed_candidate_byte_admission import (
    verify_composed_candidate_byte_admission,
)
from engine.intelligence.qwen_image_canonical_candidate_one_shot_composition_execution import (
    verify_one_shot_composition_execution,
)
from engine.intelligence.qwen_image_canonical_candidate_composition_execution_preflight import (
    verify_composition_execution_preflight,
)
from engine.intelligence.qwen_image_canonical_candidate_deterministic_composition_request import (
    verify_deterministic_composition_request,
)
from engine.intelligence.qwen_image_canonical_candidate_generated_layer_qa import (
    verify_canonical_candidate_generated_layer_qa,
)
from engine.intelligence.qwen_image_canonical_candidate_semantic_base_qa import (
    verify_canonical_candidate_semantic_base_qa,
)
from engine.intelligence.qwen_image_canonical_candidate_byte_admission import (
    verify_canonical_candidate_byte_admission,
)
from engine.intelligence.qwen_image_composed_candidate_golden_quality_adjudication import (
    SCHEMA as CS276_SCHEMA,
    build_composed_candidate_golden_quality_adjudication,
    verify_composed_candidate_golden_quality_adjudication,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-visual-quality-evidence-to-golden-quality-adjudication-v1"
_DOWNSTREAM_FALSE = (
    "composed_visual_approved",
    "semantic_approved",
    "human_visual_review_approved",
    "genuine_golden_png_created",
    "publication_ready",
)
Verifier = Callable[..., dict[str, Any]]


@dataclass(frozen=True)
class VisualQualityEvidenceToGoldenQualityAdjudicationRun:
    receipt_path: Path
    cs276_receipt_path: Path


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
    return {"repository_relative_path": rel, "sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw)}


def _reopen(root: Path, binding: Any, code: str) -> Path:
    if not isinstance(binding, Mapping):
        raise ValueError(code)
    rel = binding.get("repository_relative_path")
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
        raise ValueError(code)
    path = root.resolve() / rel
    current = _bind(root, path, code)
    if any(current.get(k) != binding.get(k) for k in ("repository_relative_path", "sha256", "byte_size")):
        raise ValueError(code + "_BYTE_DRIFT")
    return path


def _verified_source(root: Path, parent: Mapping[str, Any], field: str, verifier: Verifier, code: str) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    binding = parent.get(field)
    path = _reopen(root, binding, code)
    child = verifier(path, repo_root=root)
    if not isinstance(binding, Mapping) or binding.get("receipt_sha256") != child.get("receipt_sha256"):
        raise ValueError(code + "_RECEIPT_DRIFT")
    return path, dict(binding), child


def _exact(binding: Mapping[str, Any], receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {"repository_relative_path": binding.get("repository_relative_path"), "sha256": binding.get("sha256"), "byte_size": binding.get("byte_size"), "receipt_sha256": receipt.get("receipt_sha256")}


def _assert_cs339(value: Mapping[str, Any]) -> None:
    if value.get("schema") != CS339_SCHEMA or value.get("status") != "VISUAL_QUALITY_EVIDENCE_ADMITTED":
        raise ValueError("CS340_CS339_STATE_INVALID")
    for field in ("composition_executed", "composed_candidate_bytes_admitted_for_post_composition_qa", "semantic_inspection_executed", "hybrid_surface_semantic_qa_approved", "visual_quality_review_requested", "visual_quality_review_executed", "visual_quality_evidence_admitted"):
        if value.get(field) is not True:
            raise ValueError(f"CS340_CS339_REQUIRED_GATE_MISSING:{field}")
    if value.get("visual_quality_review_approved") is not False or value.get("golden_quality_approved") is not False or value.get("authoritative") is not False:
        raise ValueError("CS340_CS339_PREMATURE_AUTHORITY")
    for field in _DOWNSTREAM_FALSE:
        if value.get(field) is not False:
            raise ValueError(f"CS340_CS339_PREMATURE_AUTHORITY:{field}")


def _derive_cs272_from_cs275(root: Path, cs275: Mapping[str, Any]) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    _, _, cs274 = _verified_source(root, cs275, "source_cs274_request", verify_composed_candidate_visual_quality_review_request, "CS340_CS274_INVALID")
    _, _, cs273 = _verified_source(root, cs274, "source_cs273_receipt", verify_composed_candidate_hybrid_surface_semantic_qa, "CS340_CS273_INVALID")
    return _verified_source(root, cs273, "source_cs272_receipt", verify_composed_candidate_byte_admission, "CS340_CS272_INVALID")


def _derive_cs263_from_cs272(root: Path, cs272: Mapping[str, Any]) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    _, _, cs271 = _verified_source(root, cs272, "source_cs271_receipt", verify_one_shot_composition_execution, "CS340_CS271_INVALID")
    _, _, cs270 = _verified_source(root, cs271, "source_cs270_receipt", verify_composition_execution_preflight, "CS340_CS270_INVALID")
    _, _, cs269 = _verified_source(root, cs270, "source_cs269_receipt", verify_deterministic_composition_request, "CS340_CS269_INVALID")
    _, _, cs268 = _verified_source(root, cs269, "source_cs268_receipt", verify_canonical_candidate_generated_layer_qa, "CS340_CS268_INVALID")
    _, _, cs264 = _verified_source(root, cs268, "source_cs264_receipt", verify_canonical_candidate_semantic_base_qa, "CS340_CS264_INVALID")
    return _verified_source(root, cs264, "source_candidate_admission", verify_canonical_candidate_byte_admission, "CS340_CS263_INVALID")


def _assert_cs276(cs276: Mapping[str, Any], cs339: Mapping[str, Any], b263: Mapping[str, Any], cs263: Mapping[str, Any], b272: Mapping[str, Any], cs272: Mapping[str, Any], b275: Mapping[str, Any], cs275: Mapping[str, Any]) -> None:
    if cs276.get("schema") != CS276_SCHEMA or cs276.get("golden_quality_selector_executed") is not True:
        raise ValueError("CS340_CS276_STATE_INVALID")
    if not isinstance(cs276.get("golden_quality_approved"), bool):
        raise ValueError("CS340_CS276_VERDICT_INVALID")
    if cs276.get("story_snapshot_sha256") != cs339.get("story_snapshot_sha256") or cs276.get("composed_candidate_png") != cs339.get("composed_candidate_png"):
        raise ValueError("CS340_CS276_LINEAGE_DRIFT")
    expected = (("source_cs263_receipt", b263, cs263), ("source_cs272_receipt", b272, cs272), ("source_cs275_receipt", b275, cs275))
    for field, binding, receipt in expected:
        if cs276.get(field) != _exact(binding, receipt):
            raise ValueError(f"CS340_CS276_SOURCE_DRIFT:{field}")
    for field in _DOWNSTREAM_FALSE:
        if cs276.get(field) is not False:
            raise ValueError(f"CS340_CS276_PREMATURE_AUTHORITY:{field}")


def continue_visual_quality_evidence_to_golden_quality_adjudication(cs339_receipt_path: Path, output_dir: Path, *, repo_root: Path) -> VisualQualityEvidenceToGoldenQualityAdjudicationRun:
    repo_root = repo_root.resolve(); output_dir = output_dir.resolve()
    try:
        output_dir.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError("CS340_OUTPUT_INVALID") from exc
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("CS340_OUTPUT_INVALID")

    b339 = _bind(repo_root, cs339_receipt_path, "CS340_CS339_RECEIPT_INVALID")
    cs339 = verify_visual_quality_review_request_to_evidence_admission(cs339_receipt_path, repo_root=repo_root)
    _assert_cs339(cs339)

    p275 = _reopen(repo_root, cs339.get("cs275_receipt"), "CS340_CS275_INVALID")
    b275 = dict(cs339["cs275_receipt"])
    cs275 = verify_composed_candidate_visual_quality_review_evidence(p275, repo_root=repo_root)
    if b275.get("receipt_sha256") != cs275.get("receipt_sha256"):
        raise ValueError("CS340_CS275_RECEIPT_DRIFT")

    p272, b272, cs272 = _derive_cs272_from_cs275(repo_root, cs275)
    p263, b263, cs263 = _derive_cs263_from_cs272(repo_root, cs272)

    output_dir.mkdir(mode=0o700)
    cs276_dir = output_dir / "cs276"
    p276 = build_composed_candidate_golden_quality_adjudication(p263, p272, p275, cs276_dir, repo_root=repo_root)
    cs276 = verify_composed_candidate_golden_quality_adjudication(p276, repo_root=repo_root)
    _assert_cs276(cs276, cs339, b263, cs263, b272, cs272, b275, cs275)

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "GOLDEN_QUALITY_ADJUDICATED",
        "story_snapshot_sha256": cs339["story_snapshot_sha256"],
        "candidate_png": dict(cs339["candidate_png"]),
        "composed_candidate_png": dict(cs339["composed_candidate_png"]),
        "source_cs339_receipt": b339,
        "cs275_receipt": b275,
        "cs276_receipt": {**_bind(repo_root, p276, "CS340_CS276_INVALID"), "receipt_sha256": cs276.get("receipt_sha256")},
        "visual_quality_review_executed": True,
        "visual_quality_evidence_admitted": True,
        "golden_quality_selector_executed": True,
        "golden_quality_approved": cs276["golden_quality_approved"],
        "composed_visual_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "authoritative": False,
        "policy": {
            "exact_cs339_selected_cs275_replayed": True,
            "exact_cs275_to_cs272_lineage_derived": True,
            "exact_cs272_to_sealed_candidate_admission_derived": True,
            "existing_cs276_adjudicator_reused": True,
            "scores_and_blockers_not_generated_here": True,
            "human_review_remains_independent": True,
            "final_semantic_publication_remains_independent": True,
            "genuine_golden_png_not_created_here": True,
            "publication_authority_not_granted": True
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    path = output_dir / "visual_quality_evidence_to_golden_quality_adjudication.json"
    tmp = output_dir / ".visual_quality_evidence_to_golden_quality_adjudication.json.tmp"
    with tmp.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n"); handle.flush(); os.fsync(handle.fileno())
    os.replace(tmp, path)
    return VisualQualityEvidenceToGoldenQualityAdjudicationRun(receipt_path=path, cs276_receipt_path=p276)


def verify_visual_quality_evidence_to_golden_quality_adjudication(receipt_path: Path, *, repo_root: Path) -> dict[str, Any]:
    receipt = _json(receipt_path, "CS340_RECEIPT_INVALID")
    unsigned = dict(receipt); claimed = unsigned.pop("receipt_sha256", None)
    if receipt.get("schema") != SCHEMA or receipt.get("status") != "GOLDEN_QUALITY_ADJUDICATED" or claimed != sha256_json(unsigned):
        raise ValueError("CS340_RECEIPT_INVALID")
    if receipt.get("golden_quality_selector_executed") is not True or not isinstance(receipt.get("golden_quality_approved"), bool) or receipt.get("authoritative") is not False:
        raise ValueError("CS340_STATE_DRIFT")
    for field in _DOWNSTREAM_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(f"CS340_PREMATURE_AUTHORITY:{field}")

    p339 = _reopen(repo_root, receipt.get("source_cs339_receipt"), "CS340_CS339_RECEIPT_INVALID")
    cs339 = verify_visual_quality_review_request_to_evidence_admission(p339, repo_root=repo_root); _assert_cs339(cs339)
    if receipt.get("story_snapshot_sha256") != cs339.get("story_snapshot_sha256") or receipt.get("candidate_png") != cs339.get("candidate_png") or receipt.get("composed_candidate_png") != cs339.get("composed_candidate_png") or receipt.get("cs275_receipt") != cs339.get("cs275_receipt"):
        raise ValueError("CS340_CS339_LINEAGE_DRIFT")

    p275 = _reopen(repo_root, receipt.get("cs275_receipt"), "CS340_CS275_INVALID")
    b275 = dict(receipt["cs275_receipt"]); cs275 = verify_composed_candidate_visual_quality_review_evidence(p275, repo_root=repo_root)
    p272, b272, cs272 = _derive_cs272_from_cs275(repo_root, cs275)
    _, b263, cs263 = _derive_cs263_from_cs272(repo_root, cs272)
    p276 = _reopen(repo_root, receipt.get("cs276_receipt"), "CS340_CS276_INVALID")
    cs276 = verify_composed_candidate_golden_quality_adjudication(p276, repo_root=repo_root)
    _assert_cs276(cs276, cs339, b263, cs263, b272, cs272, b275, cs275)
    if receipt.get("golden_quality_approved") != cs276.get("golden_quality_approved") or receipt.get("cs276_receipt", {}).get("receipt_sha256") != cs276.get("receipt_sha256"):
        raise ValueError("CS340_CS276_VERDICT_DRIFT")
    return receipt
