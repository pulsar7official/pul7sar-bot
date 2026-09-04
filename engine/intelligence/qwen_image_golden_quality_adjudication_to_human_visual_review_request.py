"""CS341: continue an exact successful CS340 adjudication into CS277 Human Review request.

This continuation independently replays CS340, requires the existing CS276 verdict to
be genuinely Golden/Elite, binds the exact CS276 receipt selected by CS340, invokes
the existing CS277 request builder once, independently replays CS277, and stops
before any human verdict, presentation approval, final semantic authority, Genuine
Golden PNG creation, or publication.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_visual_quality_evidence_to_golden_quality_adjudication import (
    SCHEMA as CS340_SCHEMA,
    verify_visual_quality_evidence_to_golden_quality_adjudication,
)
from engine.intelligence.qwen_image_composed_candidate_golden_quality_adjudication import (
    SCHEMA as CS276_SCHEMA,
    verify_composed_candidate_golden_quality_adjudication,
)
from engine.intelligence.qwen_image_composed_candidate_human_visual_review_request import (
    SCHEMA as CS277_SCHEMA,
    build_composed_candidate_human_visual_review_request,
    verify_composed_candidate_human_visual_review_request,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-golden-quality-adjudication-to-human-visual-review-request-v1"
STATUS = "HUMAN_VISUAL_REVIEW_REQUEST_READY"
_DOWNSTREAM_FALSE = (
    "human_visual_review_executed",
    "human_visual_review_approved",
    "composed_visual_approved",
    "semantic_approved",
    "genuine_golden_png_created",
    "publication_ready",
)

@dataclass(frozen=True)
class GoldenQualityToHumanVisualReviewRequestRun:
    receipt_path: Path
    cs277_receipt_path: Path

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

def _assert_cs340(value: Mapping[str, Any]) -> None:
    if value.get("schema") != CS340_SCHEMA or value.get("status") != "GOLDEN_QUALITY_ADJUDICATED":
        raise ValueError("CS341_CS340_STATE_INVALID")
    if value.get("golden_quality_selector_executed") is not True:
        raise ValueError("CS341_CS340_SELECTOR_NOT_EXECUTED")
    if value.get("golden_quality_approved") is not True:
        raise ValueError("CS341_CS340_BELOW_GOLDEN")
    for field in _DOWNSTREAM_FALSE:
        if value.get(field) is not False:
            raise ValueError(f"CS341_CS340_PREMATURE_AUTHORITY:{field}")
    if value.get("authoritative") is not False:
        raise ValueError("CS341_CS340_PREMATURE_AUTHORITY:authoritative")

def _assert_cs276(value: Mapping[str, Any], cs340: Mapping[str, Any]) -> None:
    if value.get("schema") != CS276_SCHEMA:
        raise ValueError("CS341_CS276_SCHEMA_DRIFT")
    if value.get("golden_quality_selector_executed") is not True or value.get("golden_quality_approved") is not True:
        raise ValueError("CS341_CS276_BELOW_GOLDEN")
    if value.get("quality_tier") not in ("golden", "elite"):
        raise ValueError("CS341_CS276_QUALITY_TIER_INVALID")
    if value.get("story_snapshot_sha256") != cs340.get("story_snapshot_sha256"):
        raise ValueError("CS341_CS276_STORY_DRIFT")
    if value.get("composed_candidate_png") != cs340.get("composed_candidate_png"):
        raise ValueError("CS341_CS276_PNG_DRIFT")
    for field in ("human_visual_review_approved", "composed_visual_approved", "semantic_approved", "genuine_golden_png_created", "publication_ready"):
        if value.get(field) is not False:
            raise ValueError(f"CS341_CS276_PREMATURE_AUTHORITY:{field}")

def _assert_cs277(value: Mapping[str, Any], cs340: Mapping[str, Any], cs276_binding: Mapping[str, Any], cs276: Mapping[str, Any]) -> None:
    if value.get("schema") != CS277_SCHEMA or value.get("status") != "QWEN_IMAGE_COMPOSED_CANDIDATE_HUMAN_VISUAL_REVIEW_REQUESTED":
        raise ValueError("CS341_CS277_STATE_INVALID")
    if value.get("story_snapshot_sha256") != cs340.get("story_snapshot_sha256") or value.get("composed_candidate_png") != cs340.get("composed_candidate_png"):
        raise ValueError("CS341_CS277_LINEAGE_DRIFT")
    expected_source = {**dict(cs276_binding), "receipt_sha256": cs276.get("receipt_sha256")}
    if value.get("source_cs276_receipt") != expected_source:
        raise ValueError("CS341_CS277_SOURCE_DRIFT")
    if value.get("golden_quality_approved") is not True or value.get("human_visual_review_requested") is not True:
        raise ValueError("CS341_CS277_REQUEST_STATE_INVALID")
    for field in _DOWNSTREAM_FALSE:
        if value.get(field) is not False:
            raise ValueError(f"CS341_CS277_PREMATURE_AUTHORITY:{field}")

def continue_golden_quality_to_human_visual_review_request(
    cs340_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> GoldenQualityToHumanVisualReviewRequestRun:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    try:
        output_dir.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError("CS341_OUTPUT_INVALID") from exc
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("CS341_OUTPUT_INVALID")

    b340 = _bind(repo_root, cs340_receipt_path, "CS341_CS340_RECEIPT_INVALID")
    cs340 = verify_visual_quality_evidence_to_golden_quality_adjudication(cs340_receipt_path, repo_root=repo_root)
    _assert_cs340(cs340)

    b276 = cs340.get("cs276_receipt")
    p276 = _reopen(repo_root, b276, "CS341_CS276_RECEIPT_INVALID")
    cs276 = verify_composed_candidate_golden_quality_adjudication(p276, repo_root=repo_root)
    if not isinstance(b276, Mapping) or b276.get("receipt_sha256") != cs276.get("receipt_sha256"):
        raise ValueError("CS341_CS276_RECEIPT_DRIFT")
    _assert_cs276(cs276, cs340)

    output_dir.mkdir(mode=0o700)
    cs277_dir = output_dir / "cs277"
    p277 = build_composed_candidate_human_visual_review_request(p276, cs277_dir, repo_root=repo_root)
    cs277 = verify_composed_candidate_human_visual_review_request(p277, repo_root=repo_root)
    _assert_cs277(cs277, cs340, b276, cs276)

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "story_snapshot_sha256": cs340["story_snapshot_sha256"],
        "candidate_png": dict(cs340["candidate_png"]),
        "composed_candidate_png": dict(cs340["composed_candidate_png"]),
        "source_cs340_receipt": b340,
        "cs276_receipt": dict(b276),
        "cs277_receipt": {**_bind(repo_root, p277, "CS341_CS277_RECEIPT_INVALID"), "receipt_sha256": cs277.get("receipt_sha256")},
        "golden_quality_selector_executed": True,
        "golden_quality_approved": True,
        "human_visual_review_requested": True,
        "human_visual_review_executed": False,
        "human_visual_review_approved": False,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "authoritative": False,
        "policy": {
            "exact_cs340_replayed": True,
            "exact_cs340_selected_cs276_replayed": True,
            "cs276_rejection_stops_before_human_review_request": True,
            "existing_cs277_request_contract_reused": True,
            "human_verdict_not_generated_here": True,
            "exact_bound_composed_png_preserved": True,
            "presentation_and_brand_review_remain_independent": True,
            "final_semantic_publication_remains_independent": True,
            "genuine_golden_png_not_created_here": True,
            "publication_authority_not_granted": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    path = output_dir / "golden_quality_to_human_visual_review_request.json"
    tmp = output_dir / ".golden_quality_to_human_visual_review_request.json.tmp"
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
    return GoldenQualityToHumanVisualReviewRequestRun(receipt_path=path, cs277_receipt_path=p277)

def verify_golden_quality_to_human_visual_review_request(receipt_path: Path, *, repo_root: Path) -> dict[str, Any]:
    receipt = _json(receipt_path, "CS341_RECEIPT_INVALID")
    unsigned = dict(receipt)
    claimed = unsigned.pop("receipt_sha256", None)
    if receipt.get("schema") != SCHEMA or receipt.get("status") != STATUS or claimed != sha256_json(unsigned):
        raise ValueError("CS341_RECEIPT_INVALID")
    if receipt.get("golden_quality_approved") is not True or receipt.get("human_visual_review_requested") is not True or receipt.get("authoritative") is not False:
        raise ValueError("CS341_STATE_DRIFT")
    for field in _DOWNSTREAM_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(f"CS341_PREMATURE_AUTHORITY:{field}")

    p340 = _reopen(repo_root, receipt.get("source_cs340_receipt"), "CS341_CS340_RECEIPT_INVALID")
    cs340 = verify_visual_quality_evidence_to_golden_quality_adjudication(p340, repo_root=repo_root)
    _assert_cs340(cs340)
    if receipt.get("story_snapshot_sha256") != cs340.get("story_snapshot_sha256") or receipt.get("candidate_png") != cs340.get("candidate_png") or receipt.get("composed_candidate_png") != cs340.get("composed_candidate_png") or receipt.get("cs276_receipt") != cs340.get("cs276_receipt"):
        raise ValueError("CS341_CS340_LINEAGE_DRIFT")

    b276 = receipt.get("cs276_receipt")
    p276 = _reopen(repo_root, b276, "CS341_CS276_RECEIPT_INVALID")
    cs276 = verify_composed_candidate_golden_quality_adjudication(p276, repo_root=repo_root)
    _assert_cs276(cs276, cs340)
    if not isinstance(b276, Mapping) or b276.get("receipt_sha256") != cs276.get("receipt_sha256"):
        raise ValueError("CS341_CS276_RECEIPT_DRIFT")

    p277 = _reopen(repo_root, receipt.get("cs277_receipt"), "CS341_CS277_RECEIPT_INVALID")
    cs277 = verify_composed_candidate_human_visual_review_request(p277, repo_root=repo_root)
    _assert_cs277(cs277, cs340, b276, cs276)
    if receipt.get("cs277_receipt", {}).get("receipt_sha256") != cs277.get("receipt_sha256"):
        raise ValueError("CS341_CS277_RECEIPT_DRIFT")
    return receipt
