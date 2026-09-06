"""CS342: continue exact CS341 Human Review request into CS278 evidence admission.

This continuation independently replays CS341, binds and replays the exact CS277
request selected by CS341, admits only repository-bound external independent human
review evidence through the existing CS278 contract, independently replays CS278,
and stops before presentation/brand approval, final composed approval, final semantic
authority, Genuine Golden PNG creation, or publication.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_golden_quality_adjudication_to_human_visual_review_request import (
    SCHEMA as CS341_SCHEMA,
    verify_golden_quality_to_human_visual_review_request,
)
from engine.intelligence.qwen_image_composed_candidate_human_visual_review_request import (
    SCHEMA as CS277_SCHEMA,
    verify_composed_candidate_human_visual_review_request,
)
from engine.intelligence.qwen_image_composed_candidate_human_visual_review_evidence import (
    SCHEMA as CS278_SCHEMA,
    build_composed_candidate_human_visual_review_evidence,
    verify_composed_candidate_human_visual_review_evidence,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-human-visual-review-request-to-evidence-admission-v1"
STATUS = "HUMAN_VISUAL_REVIEW_EVIDENCE_ADMITTED"
_FINAL_FALSE = (
    "composed_visual_approved",
    "semantic_approved",
    "genuine_golden_png_created",
    "publication_ready",
)


@dataclass(frozen=True)
class HumanVisualReviewRequestToEvidenceAdmissionRun:
    receipt_path: Path
    cs278_receipt_path: Path


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


def _assert_cs341(value: Mapping[str, Any]) -> None:
    if value.get("schema") != CS341_SCHEMA or value.get("status") != "HUMAN_VISUAL_REVIEW_REQUEST_READY":
        raise ValueError("CS342_CS341_STATE_INVALID")
    for field in ("golden_quality_approved", "human_visual_review_requested"):
        if value.get(field) is not True:
            raise ValueError(f"CS342_CS341_REQUIRED_GATE_MISSING:{field}")
    for field in ("human_visual_review_executed", "human_visual_review_approved", *_FINAL_FALSE):
        if value.get(field) is not False:
            raise ValueError(f"CS342_CS341_PREMATURE_AUTHORITY:{field}")
    if value.get("authoritative") is not False:
        raise ValueError("CS342_CS341_PREMATURE_AUTHORITY:authoritative")


def _assert_cs277(value: Mapping[str, Any], cs341: Mapping[str, Any]) -> None:
    if value.get("schema") != CS277_SCHEMA or value.get("status") != "QWEN_IMAGE_COMPOSED_CANDIDATE_HUMAN_VISUAL_REVIEW_REQUESTED":
        raise ValueError("CS342_CS277_STATE_INVALID")
    if value.get("story_snapshot_sha256") != cs341.get("story_snapshot_sha256"):
        raise ValueError("CS342_CS277_STORY_DRIFT")
    if value.get("composed_candidate_png") != cs341.get("composed_candidate_png"):
        raise ValueError("CS342_CS277_PNG_DRIFT")
    if value.get("golden_quality_approved") is not True or value.get("human_visual_review_requested") is not True:
        raise ValueError("CS342_CS277_REQUEST_STATE_INVALID")
    for field in ("human_visual_review_executed", "human_visual_review_approved", *_FINAL_FALSE):
        if value.get(field) is not False:
            raise ValueError(f"CS342_CS277_PREMATURE_AUTHORITY:{field}")


def _assert_cs278(
    value: Mapping[str, Any],
    cs341: Mapping[str, Any],
    cs277_binding: Mapping[str, Any],
    cs277: Mapping[str, Any],
    external_binding: Mapping[str, Any],
) -> None:
    if value.get("schema") != CS278_SCHEMA or value.get("status") != "QWEN_IMAGE_COMPOSED_CANDIDATE_HUMAN_VISUAL_REVIEW_EVIDENCE_ADMITTED":
        raise ValueError("CS342_CS278_STATE_INVALID")
    if value.get("story_snapshot_sha256") != cs341.get("story_snapshot_sha256"):
        raise ValueError("CS342_CS278_STORY_DRIFT")
    if value.get("composed_candidate_png") != cs341.get("composed_candidate_png"):
        raise ValueError("CS342_CS278_PNG_DRIFT")
    expected_source = {**dict(cs277_binding), "receipt_sha256": cs277.get("receipt_sha256")}
    if value.get("source_cs277_request") != expected_source:
        raise ValueError("CS342_CS278_SOURCE_DRIFT")
    if value.get("external_human_review_evidence") != dict(external_binding):
        raise ValueError("CS342_CS278_EXTERNAL_EVIDENCE_DRIFT")
    for field in (
        "golden_quality_approved",
        "human_visual_review_requested",
        "human_visual_review_executed",
        "human_visual_review_evidence_admitted",
    ):
        if value.get(field) is not True:
            raise ValueError(f"CS342_CS278_REQUIRED_STATE_MISSING:{field}")
    if not isinstance(value.get("human_visual_review_approved"), bool):
        raise ValueError("CS342_CS278_HUMAN_VERDICT_INVALID")
    for field in _FINAL_FALSE:
        if value.get(field) is not False:
            raise ValueError(f"CS342_CS278_PREMATURE_AUTHORITY:{field}")


def continue_human_visual_review_request_to_evidence_admission(
    cs341_receipt_path: Path,
    external_human_review_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> HumanVisualReviewRequestToEvidenceAdmissionRun:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    try:
        output_dir.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError("CS342_OUTPUT_INVALID") from exc
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("CS342_OUTPUT_INVALID")

    b341 = _bind(repo_root, cs341_receipt_path, "CS342_CS341_RECEIPT_INVALID")
    cs341 = verify_golden_quality_to_human_visual_review_request(cs341_receipt_path, repo_root=repo_root)
    _assert_cs341(cs341)

    b277 = cs341.get("cs277_receipt")
    p277 = _reopen(repo_root, b277, "CS342_CS277_RECEIPT_INVALID")
    cs277 = verify_composed_candidate_human_visual_review_request(p277, repo_root=repo_root)
    if not isinstance(b277, Mapping) or b277.get("receipt_sha256") != cs277.get("receipt_sha256"):
        raise ValueError("CS342_CS277_RECEIPT_DRIFT")
    _assert_cs277(cs277, cs341)

    external_binding = _bind(repo_root, external_human_review_path, "CS342_EXTERNAL_HUMAN_REVIEW_INVALID")

    output_dir.mkdir(mode=0o700)
    cs278_dir = output_dir / "cs278"
    p278 = build_composed_candidate_human_visual_review_evidence(
        p277,
        external_human_review_path,
        cs278_dir,
        repo_root=repo_root,
    )
    cs278 = verify_composed_candidate_human_visual_review_evidence(p278, repo_root=repo_root)
    _assert_cs278(cs278, cs341, b277, cs277, external_binding)

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "story_snapshot_sha256": cs341["story_snapshot_sha256"],
        "candidate_png": dict(cs341["candidate_png"]),
        "composed_candidate_png": dict(cs341["composed_candidate_png"]),
        "source_cs341_receipt": b341,
        "cs277_receipt": dict(b277),
        "external_human_review_evidence": dict(external_binding),
        "cs278_receipt": {
            **_bind(repo_root, p278, "CS342_CS278_RECEIPT_INVALID"),
            "receipt_sha256": cs278.get("receipt_sha256"),
        },
        "golden_quality_approved": True,
        "human_visual_review_requested": True,
        "human_visual_review_executed": True,
        "human_visual_review_evidence_admitted": True,
        "human_visual_review_approved": bool(cs278["human_visual_review_approved"]),
        "composed_visual_approved": False,
        "semantic_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "authoritative": False,
        "policy": {
            "exact_cs341_replayed": True,
            "exact_cs341_selected_cs277_replayed": True,
            "existing_cs278_evidence_contract_reused": True,
            "human_verdict_is_external_and_never_generated_here": True,
            "human_rejection_is_preserved_fail_closed_for_downstream_progression": True,
            "exact_bound_composed_png_preserved": True,
            "presentation_and_brand_review_remain_independent": True,
            "final_composed_and_semantic_approval_remain_independent": True,
            "semantic_publication_gate_remains_independent": True,
            "genuine_golden_png_not_created_here": True,
            "publication_authority_not_granted": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    path = output_dir / "human_visual_review_request_to_evidence_admission.json"
    tmp = output_dir / ".human_visual_review_request_to_evidence_admission.json.tmp"
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
    return HumanVisualReviewRequestToEvidenceAdmissionRun(receipt_path=path, cs278_receipt_path=p278)


def verify_human_visual_review_request_to_evidence_admission(
    receipt_path: Path,
    *,
    repo_root: Path,
) -> dict[str, Any]:
    receipt = _json(receipt_path, "CS342_RECEIPT_INVALID")
    unsigned = dict(receipt)
    claimed = unsigned.pop("receipt_sha256", None)
    if receipt.get("schema") != SCHEMA or receipt.get("status") != STATUS or claimed != sha256_json(unsigned):
        raise ValueError("CS342_RECEIPT_INVALID")
    if receipt.get("golden_quality_approved") is not True:
        raise ValueError("CS342_STATE_DRIFT:golden_quality_approved")
    if receipt.get("human_visual_review_requested") is not True or receipt.get("human_visual_review_executed") is not True or receipt.get("human_visual_review_evidence_admitted") is not True:
        raise ValueError("CS342_STATE_DRIFT:human_review")
    if not isinstance(receipt.get("human_visual_review_approved"), bool):
        raise ValueError("CS342_STATE_DRIFT:human_visual_review_approved")
    if receipt.get("authoritative") is not False:
        raise ValueError("CS342_PREMATURE_AUTHORITY:authoritative")
    for field in _FINAL_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(f"CS342_PREMATURE_AUTHORITY:{field}")

    p341 = _reopen(repo_root, receipt.get("source_cs341_receipt"), "CS342_CS341_RECEIPT_INVALID")
    cs341 = verify_golden_quality_to_human_visual_review_request(p341, repo_root=repo_root)
    _assert_cs341(cs341)
    if (
        receipt.get("story_snapshot_sha256") != cs341.get("story_snapshot_sha256")
        or receipt.get("candidate_png") != cs341.get("candidate_png")
        or receipt.get("composed_candidate_png") != cs341.get("composed_candidate_png")
        or receipt.get("cs277_receipt") != cs341.get("cs277_receipt")
    ):
        raise ValueError("CS342_CS341_LINEAGE_DRIFT")

    b277 = receipt.get("cs277_receipt")
    p277 = _reopen(repo_root, b277, "CS342_CS277_RECEIPT_INVALID")
    cs277 = verify_composed_candidate_human_visual_review_request(p277, repo_root=repo_root)
    if not isinstance(b277, Mapping) or b277.get("receipt_sha256") != cs277.get("receipt_sha256"):
        raise ValueError("CS342_CS277_RECEIPT_DRIFT")
    _assert_cs277(cs277, cs341)

    external_binding = receipt.get("external_human_review_evidence")
    _reopen(repo_root, external_binding, "CS342_EXTERNAL_HUMAN_REVIEW_INVALID")
    b278 = receipt.get("cs278_receipt")
    p278 = _reopen(repo_root, b278, "CS342_CS278_RECEIPT_INVALID")
    cs278 = verify_composed_candidate_human_visual_review_evidence(p278, repo_root=repo_root)
    if not isinstance(b278, Mapping) or b278.get("receipt_sha256") != cs278.get("receipt_sha256"):
        raise ValueError("CS342_CS278_RECEIPT_DRIFT")
    _assert_cs278(cs278, cs341, b277, cs277, external_binding)
    if receipt.get("human_visual_review_approved") is not cs278.get("human_visual_review_approved"):
        raise ValueError("CS342_HUMAN_VERDICT_DRIFT")
    return receipt
