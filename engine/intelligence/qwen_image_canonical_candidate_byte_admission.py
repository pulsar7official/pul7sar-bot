"""Byte-admit one genuine CS262 canonical candidate for downstream visual QA.

Change Set 263 is deliberately non-semantic and non-generative. It revalidates
an exact successful Change Set 262 receipt, reopens the exact candidate PNG,
and emits a byte-bound admission receipt that downstream pixel/semantic,
Visual Critic, human review, Golden-quality, brand/typography, and publication
gates may consume.

Admission never upgrades a candidate into a Golden Visual.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import struct
from typing import Any, Mapping

from engine.intelligence.qwen_image_inference_measurement import sha256_json
from engine.intelligence.qwen_image_one_shot_canonical_inference import (
    ONE_SHOT_CANONICAL_INFERENCE_SCHEMA,
    verify_one_shot_canonical_inference,
)

CANONICAL_CANDIDATE_BYTE_ADMISSION_SCHEMA = (
    "pul7sar-phase18-qwen-image-2512-canonical-candidate-byte-admission-v1"
)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_REQUIRED_TRUE = (
    "production_semantic_replay_executed",
    "fresh_story_gates_passed",
    "controlled_trial_preflight_valid",
    "canonical_generation_authorized",
    "inference_executed",
    "genuine_canonical_inference_executed",
)
_REQUIRED_FALSE = (
    "genuine_golden_png_created",
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "publication_ready",
)


@dataclass(frozen=True)
class CanonicalCandidateByteAdmission:
    output_dir: Path
    receipt_path: Path
    story_snapshot_sha256: str
    candidate_sha256: str


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


def _file_binding(path: Path, code: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(code)
    raw = path.read_bytes()
    if not raw:
        raise ValueError(code)
    return {"sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw)}


def _png_dimensions(raw: bytes) -> tuple[int, int]:
    if len(raw) < 24 or raw[:8] != PNG_SIGNATURE:
        raise ValueError("QWEN_CANDIDATE_ADMISSION_PNG_INVALID")
    if raw[12:16] != b"IHDR":
        raise ValueError("QWEN_CANDIDATE_ADMISSION_PNG_IHDR_MISSING")
    width, height = struct.unpack(">II", raw[16:24])
    if width <= 0 or height <= 0:
        raise ValueError("QWEN_CANDIDATE_ADMISSION_PNG_DIMENSIONS_INVALID")
    return width, height


def _assert_authority(receipt: Mapping[str, Any]) -> None:
    for field in _REQUIRED_TRUE:
        if receipt.get(field) is not True:
            raise ValueError(f"QWEN_CANDIDATE_ADMISSION_REQUIRED_GATE_MISSING:{field}")
    for field in _REQUIRED_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(f"QWEN_CANDIDATE_ADMISSION_PREMATURE_AUTHORITY:{field}")


def admit_canonical_candidate_bytes(
    cs262_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> CanonicalCandidateByteAdmission:
    """Revalidate and byte-bind one CS262 candidate without approving it."""
    if output_dir.exists():
        raise ValueError("QWEN_CANDIDATE_ADMISSION_OUTPUT_ALREADY_EXISTS")
    if not output_dir.parent.is_dir():
        raise ValueError("QWEN_CANDIDATE_ADMISSION_OUTPUT_PARENT_INVALID")

    source_relative = _inside_repo_file(
        repo_root,
        cs262_receipt_path,
        "QWEN_CANDIDATE_ADMISSION_CS262_RECEIPT_OUTSIDE_REPOSITORY",
    )
    source_binding = _file_binding(
        cs262_receipt_path, "QWEN_CANDIDATE_ADMISSION_CS262_RECEIPT_INVALID"
    )
    source = verify_one_shot_canonical_inference(
        cs262_receipt_path, repo_root=repo_root
    )
    if source.get("schema") != ONE_SHOT_CANONICAL_INFERENCE_SCHEMA:
        raise ValueError("QWEN_CANDIDATE_ADMISSION_CS262_SCHEMA_DRIFT")
    _assert_authority(source)

    story_sha = source.get("story_snapshot_sha256")
    if not _is_sha256(story_sha):
        raise ValueError("QWEN_CANDIDATE_ADMISSION_STORY_SHA_INVALID")
    png_meta = source.get("png")
    if not isinstance(png_meta, Mapping) or png_meta.get("filename") != "canonical_candidate.png":
        raise ValueError("QWEN_CANDIDATE_ADMISSION_PNG_BINDING_INVALID")

    candidate_path = cs262_receipt_path.parent / "canonical_candidate.png"
    candidate_relative = _inside_repo_file(
        repo_root,
        candidate_path,
        "QWEN_CANDIDATE_ADMISSION_PNG_OUTSIDE_REPOSITORY",
    )
    candidate_binding = _file_binding(
        candidate_path, "QWEN_CANDIDATE_ADMISSION_PNG_INVALID"
    )
    if (
        png_meta.get("sha256") != candidate_binding["sha256"]
        or png_meta.get("byte_size") != candidate_binding["byte_size"]
    ):
        raise ValueError("QWEN_CANDIDATE_ADMISSION_PNG_BYTE_DRIFT")
    width, height = _png_dimensions(candidate_path.read_bytes())
    if (
        png_meta.get("width") != width
        or png_meta.get("height") != height
        or source.get("width") != width
        or source.get("height") != height
    ):
        raise ValueError("QWEN_CANDIDATE_ADMISSION_PNG_DIMENSION_DRIFT")

    receipt = {
        "schema": CANONICAL_CANDIDATE_BYTE_ADMISSION_SCHEMA,
        "status": "QWEN_IMAGE_2512_CANONICAL_CANDIDATE_BYTES_ADMITTED_FOR_POST_GENERATION_QA",
        "story_snapshot_sha256": story_sha,
        "model_id": source.get("model_id"),
        "model_revision": source.get("model_revision"),
        "cost_mode": source.get("cost_mode"),
        "expected_runtime_fingerprint_sha256": source.get(
            "expected_runtime_fingerprint_sha256"
        ),
        "observed_runtime_fingerprint_sha256": source.get(
            "observed_runtime_fingerprint_sha256"
        ),
        "source_cs262_receipt": {
            "repository_relative_path": source_relative,
            **source_binding,
            "receipt_sha256": source.get("receipt_sha256"),
        },
        "candidate_png": {
            "repository_relative_path": candidate_relative,
            **candidate_binding,
            "width": width,
            "height": height,
        },
        "prompt": source.get("prompt"),
        "negative_prompt": source.get("negative_prompt"),
        "seed": source.get("seed"),
        "num_inference_steps": source.get("num_inference_steps"),
        "guidance_scale": source.get("guidance_scale"),
        "production_semantic_replay_executed": True,
        "fresh_story_gates_passed": True,
        "controlled_trial_preflight_valid": True,
        "canonical_generation_authorized": True,
        "inference_executed": True,
        "genuine_canonical_inference_executed": True,
        "candidate_bytes_admitted_for_post_generation_qa": True,
        "genuine_golden_png_created": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
    }
    receipt["receipt_sha256"] = sha256_json(receipt)

    output_dir.mkdir(mode=0o700)
    receipt_path = output_dir / "canonical_candidate_byte_admission_receipt.json"
    tmp = output_dir / ".canonical_candidate_byte_admission_receipt.json.tmp"
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
    return CanonicalCandidateByteAdmission(
        output_dir=output_dir,
        receipt_path=receipt_path,
        story_snapshot_sha256=story_sha,
        candidate_sha256=candidate_binding["sha256"],
    )


def verify_canonical_candidate_byte_admission(
    receipt_path: Path, *, repo_root: Path
) -> dict[str, Any]:
    """Reopen an admission and prove its CS262 receipt and candidate bytes still match."""
    if receipt_path.is_symlink() or not receipt_path.is_file():
        raise ValueError("QWEN_CANDIDATE_ADMISSION_RECEIPT_INVALID")
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("QWEN_CANDIDATE_ADMISSION_RECEIPT_INVALID") from exc
    if not isinstance(receipt, dict):
        raise ValueError("QWEN_CANDIDATE_ADMISSION_RECEIPT_INVALID")
    if receipt.get("schema") != CANONICAL_CANDIDATE_BYTE_ADMISSION_SCHEMA:
        raise ValueError("QWEN_CANDIDATE_ADMISSION_SCHEMA_DRIFT")
    claimed = receipt.get("receipt_sha256")
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    if not _is_sha256(claimed) or sha256_json(unsigned) != claimed:
        raise ValueError("QWEN_CANDIDATE_ADMISSION_RECEIPT_DIGEST_MISMATCH")
    _assert_authority(receipt)
    if receipt.get("candidate_bytes_admitted_for_post_generation_qa") is not True:
        raise ValueError("QWEN_CANDIDATE_ADMISSION_AUTHORITY_MISSING")

    source_meta = receipt.get("source_cs262_receipt")
    candidate_meta = receipt.get("candidate_png")
    if not isinstance(source_meta, Mapping) or not isinstance(candidate_meta, Mapping):
        raise ValueError("QWEN_CANDIDATE_ADMISSION_BINDING_INVALID")
    source_rel = source_meta.get("repository_relative_path")
    candidate_rel = candidate_meta.get("repository_relative_path")
    for rel, code in ((source_rel, "CS262"), (candidate_rel, "PNG")):
        if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
            raise ValueError(f"QWEN_CANDIDATE_ADMISSION_{code}_PATH_INVALID")

    source_path = repo_root.resolve() / source_rel
    candidate_path = repo_root.resolve() / candidate_rel
    if _inside_repo_file(repo_root, source_path, "QWEN_CANDIDATE_ADMISSION_CS262_OUTSIDE_REPOSITORY") != Path(source_rel).as_posix():
        raise ValueError("QWEN_CANDIDATE_ADMISSION_CS262_PATH_DRIFT")
    if _inside_repo_file(repo_root, candidate_path, "QWEN_CANDIDATE_ADMISSION_PNG_OUTSIDE_REPOSITORY") != Path(candidate_rel).as_posix():
        raise ValueError("QWEN_CANDIDATE_ADMISSION_PNG_PATH_DRIFT")

    current_source = _file_binding(source_path, "QWEN_CANDIDATE_ADMISSION_CS262_RECEIPT_INVALID")
    current_candidate = _file_binding(candidate_path, "QWEN_CANDIDATE_ADMISSION_PNG_INVALID")
    if source_meta.get("sha256") != current_source["sha256"] or source_meta.get("byte_size") != current_source["byte_size"]:
        raise ValueError("QWEN_CANDIDATE_ADMISSION_CS262_BYTE_DRIFT")
    if candidate_meta.get("sha256") != current_candidate["sha256"] or candidate_meta.get("byte_size") != current_candidate["byte_size"]:
        raise ValueError("QWEN_CANDIDATE_ADMISSION_PNG_BYTE_DRIFT")

    source = verify_one_shot_canonical_inference(source_path, repo_root=repo_root)
    _assert_authority(source)
    if source.get("receipt_sha256") != source_meta.get("receipt_sha256"):
        raise ValueError("QWEN_CANDIDATE_ADMISSION_CS262_DIGEST_DRIFT")
    if source.get("story_snapshot_sha256") != receipt.get("story_snapshot_sha256"):
        raise ValueError("QWEN_CANDIDATE_ADMISSION_CROSS_STORY")
    width, height = _png_dimensions(candidate_path.read_bytes())
    if candidate_meta.get("width") != width or candidate_meta.get("height") != height:
        raise ValueError("QWEN_CANDIDATE_ADMISSION_PNG_DIMENSION_DRIFT")
    return receipt
