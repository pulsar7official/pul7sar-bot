"""Byte-bound visual-quality review request for a CS273 composed candidate.

Change Set 274 does not invent Visual Critic scores. It verifies that the exact
CS273 hybrid-surface semantic-QA receipt passed, reopens the exact composed PNG,
and binds the repository's existing Golden Visual quality contract by bytes.
The resulting request is only an immutable handoff for later visual-quality
evidence; Human Review, Golden approval, semantic publication, and publication
remain closed.
"""
from __future__ import annotations

from dataclasses import fields
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.golden_visual_quality import (
    ELITE_TARGET,
    GOLDEN_CORE_FLOOR,
    GOLDEN_WEIGHTED_FLOOR,
    GoldenVisualBlockers,
    GoldenVisualScores,
)
from engine.intelligence.qwen_image_composed_candidate_hybrid_surface_semantic_qa import (
    SCHEMA as CS273_SCHEMA,
    verify_composed_candidate_hybrid_surface_semantic_qa,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-qwen-image-composed-candidate-visual-quality-review-request-v1"
GOLDEN_QUALITY_CONTRACT_PATH = "engine/intelligence/golden_visual_quality.py"
_REQUIRED_SOURCE_TRUE = (
    "composition_executed",
    "composed_candidate_bytes_admitted_for_post_composition_qa",
    "semantic_inspection_executed",
    "hybrid_surface_semantic_qa_approved",
)
_REQUIRED_SOURCE_FALSE = (
    "composed_visual_approved",
    "semantic_approved",
    "human_visual_review_approved",
    "genuine_golden_png_created",
    "golden_quality_approved",
    "publication_ready",
)
_DOWNSTREAM_FALSE = (
    "visual_quality_review_executed",
    "visual_quality_review_approved",
    "composed_visual_approved",
    "semantic_approved",
    "human_visual_review_approved",
    "genuine_golden_png_created",
    "golden_quality_approved",
    "publication_ready",
)


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value.lower()
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


def _assert_source_authority(source: Mapping[str, Any]) -> None:
    for field in _REQUIRED_SOURCE_TRUE:
        if source.get(field) is not True:
            raise ValueError(f"QWEN_VISUAL_QUALITY_REQUEST_REQUIRED_GATE_MISSING:{field}")
    for field in _REQUIRED_SOURCE_FALSE:
        if source.get(field) is not False:
            raise ValueError(f"QWEN_VISUAL_QUALITY_REQUEST_PREMATURE_AUTHORITY:{field}")


def _quality_contract_payload(repo_root: Path) -> dict[str, Any]:
    source_path = repo_root.resolve() / GOLDEN_QUALITY_CONTRACT_PATH
    source_binding = _bind_file(
        repo_root, source_path, "QWEN_VISUAL_QUALITY_REQUEST_CONTRACT_SOURCE_INVALID"
    )
    return {
        "source": source_binding,
        "score_fields": [item.name for item in fields(GoldenVisualScores)],
        "blocker_fields": [item.name for item in fields(GoldenVisualBlockers)],
        "golden_weighted_floor": GOLDEN_WEIGHTED_FLOOR,
        "golden_core_floor": GOLDEN_CORE_FLOOR,
        "elite_target": ELITE_TARGET,
        "selector_contract": "GoldenVisualQualitySelector",
        "evaluation_contract": "GoldenVisualEvaluation",
    }


def build_composed_candidate_visual_quality_review_request(
    cs273_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> Path:
    """Create an immutable request for later visual-quality evidence.

    No scores are generated here. A rejected CS273 candidate cannot receive a
    quality-review request.
    """
    if output_dir.exists():
        raise ValueError("QWEN_VISUAL_QUALITY_REQUEST_OUTPUT_ALREADY_EXISTS")
    if not output_dir.parent.is_dir():
        raise ValueError("QWEN_VISUAL_QUALITY_REQUEST_OUTPUT_PARENT_INVALID")

    cs273_binding = _bind_file(
        repo_root, cs273_receipt_path, "QWEN_VISUAL_QUALITY_REQUEST_CS273_INVALID"
    )
    source = verify_composed_candidate_hybrid_surface_semantic_qa(
        cs273_receipt_path, repo_root=repo_root
    )
    if source.get("schema") != CS273_SCHEMA:
        raise ValueError("QWEN_VISUAL_QUALITY_REQUEST_CS273_SCHEMA_DRIFT")
    _assert_source_authority(source)

    story_sha = source.get("story_snapshot_sha256")
    if not _is_sha256(story_sha):
        raise ValueError("QWEN_VISUAL_QUALITY_REQUEST_STORY_SHA_INVALID")
    composed = source.get("composed_candidate_png")
    if not isinstance(composed, Mapping):
        raise ValueError("QWEN_VISUAL_QUALITY_REQUEST_COMPOSED_BINDING_INVALID")
    _reopen_binding(
        repo_root, composed, "QWEN_VISUAL_QUALITY_REQUEST_COMPOSED_INVALID"
    )

    quality_contract = _quality_contract_payload(repo_root)
    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "QWEN_IMAGE_COMPOSED_CANDIDATE_VISUAL_QUALITY_REVIEW_REQUESTED",
        "story_snapshot_sha256": story_sha,
        "source_cs273_receipt": {
            **cs273_binding,
            "receipt_sha256": source.get("receipt_sha256"),
        },
        "composed_candidate_png": dict(composed),
        "golden_visual_quality_contract": quality_contract,
        "review_requirements": {
            "scores_must_describe_exact_composed_candidate_bytes": True,
            "all_score_fields_required": True,
            "all_blocker_fields_required": True,
            "semantic_qa_is_not_visual_quality_score_evidence": True,
            "quality_scores_must_not_be_inferred_from_cs273": True,
            "human_review_is_separate_downstream_authority": True,
            "semantic_publication_is_separate_downstream_authority": True,
        },
        "visual_quality_review_requested": True,
        "visual_quality_review_executed": False,
        "visual_quality_review_approved": False,
        "composition_executed": True,
        "composed_candidate_bytes_admitted_for_post_composition_qa": True,
        "semantic_inspection_executed": True,
        "hybrid_surface_semantic_qa_approved": True,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "genuine_golden_png_created": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "policy": {
            "existing_golden_visual_quality_contract_reused": True,
            "no_visual_critic_scores_fabricated": True,
            "exact_candidate_bytes_bound": True,
            "quality_contract_source_bytes_bound": True,
            "fail_closed_without_review_evidence": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)

    output_dir.mkdir(mode=0o700)
    receipt_path = output_dir / "composed_candidate_visual_quality_review_request.json"
    tmp = output_dir / ".composed_candidate_visual_quality_review_request.json.tmp"
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
    return receipt_path


def verify_composed_candidate_visual_quality_review_request(
    receipt_path: Path, *, repo_root: Path
) -> dict[str, Any]:
    if receipt_path.is_symlink() or not receipt_path.is_file():
        raise ValueError("QWEN_VISUAL_QUALITY_REQUEST_RECEIPT_INVALID")
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("QWEN_VISUAL_QUALITY_REQUEST_RECEIPT_INVALID") from exc
    if not isinstance(receipt, dict) or receipt.get("schema") != SCHEMA:
        raise ValueError("QWEN_VISUAL_QUALITY_REQUEST_SCHEMA_DRIFT")

    claimed = receipt.get("receipt_sha256")
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    if claimed != sha256_json(unsigned):
        raise ValueError("QWEN_VISUAL_QUALITY_REQUEST_RECEIPT_DIGEST_MISMATCH")

    if receipt.get("visual_quality_review_requested") is not True:
        raise ValueError("QWEN_VISUAL_QUALITY_REQUEST_NOT_REQUESTED")
    for field in _DOWNSTREAM_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(f"QWEN_VISUAL_QUALITY_REQUEST_PREMATURE_AUTHORITY:{field}")

    source_binding = receipt.get("source_cs273_receipt")
    if not isinstance(source_binding, Mapping):
        raise ValueError("QWEN_VISUAL_QUALITY_REQUEST_CS273_BINDING_INVALID")
    source_path = _reopen_binding(
        repo_root, source_binding, "QWEN_VISUAL_QUALITY_REQUEST_CS273_INVALID"
    )
    source = verify_composed_candidate_hybrid_surface_semantic_qa(
        source_path, repo_root=repo_root
    )
    if source.get("schema") != CS273_SCHEMA:
        raise ValueError("QWEN_VISUAL_QUALITY_REQUEST_CS273_SCHEMA_DRIFT")
    _assert_source_authority(source)
    if source_binding.get("receipt_sha256") != source.get("receipt_sha256"):
        raise ValueError("QWEN_VISUAL_QUALITY_REQUEST_CS273_RECEIPT_SHA_DRIFT")
    if receipt.get("story_snapshot_sha256") != source.get("story_snapshot_sha256"):
        raise ValueError("QWEN_VISUAL_QUALITY_REQUEST_STORY_BINDING_DRIFT")
    if receipt.get("composed_candidate_png") != source.get("composed_candidate_png"):
        raise ValueError("QWEN_VISUAL_QUALITY_REQUEST_COMPOSED_BINDING_DRIFT")

    composed = receipt.get("composed_candidate_png")
    if not isinstance(composed, Mapping):
        raise ValueError("QWEN_VISUAL_QUALITY_REQUEST_COMPOSED_BINDING_INVALID")
    _reopen_binding(
        repo_root, composed, "QWEN_VISUAL_QUALITY_REQUEST_COMPOSED_INVALID"
    )

    expected_contract = _quality_contract_payload(repo_root)
    if receipt.get("golden_visual_quality_contract") != expected_contract:
        raise ValueError("QWEN_VISUAL_QUALITY_REQUEST_CONTRACT_DRIFT")

    requirements = receipt.get("review_requirements")
    if not isinstance(requirements, Mapping) or not all(
        requirements.get(field) is True
        for field in (
            "scores_must_describe_exact_composed_candidate_bytes",
            "all_score_fields_required",
            "all_blocker_fields_required",
            "semantic_qa_is_not_visual_quality_score_evidence",
            "quality_scores_must_not_be_inferred_from_cs273",
            "human_review_is_separate_downstream_authority",
            "semantic_publication_is_separate_downstream_authority",
        )
    ):
        raise ValueError("QWEN_VISUAL_QUALITY_REQUEST_REQUIREMENTS_DRIFT")

    return receipt
