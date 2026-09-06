"""Byte-admit one genuine CS271 composed candidate for post-composition QA.

Change Set 272 is deliberately non-semantic and non-generative. It revalidates
an exact successful Change Set 271 one-shot composition receipt, reopens the
exact composed PNG, and emits a byte-bound admission receipt that downstream
post-composition semantic/layer QA, Visual Critic, human review, Golden-quality,
brand/typography, and publication gates may consume.

Admission never upgrades a composed candidate into an approved or Golden visual.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import struct
from typing import Any, Mapping

from engine.intelligence.qwen_image_canonical_candidate_one_shot_composition_execution import (
    SCHEMA as CS271_SCHEMA,
    verify_one_shot_composition_execution,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-qwen-image-composed-candidate-byte-admission-v1"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_DOWNSTREAM_FALSE = (
    "composed_visual_approved",
    "semantic_approved",
    "human_visual_review_approved",
    "genuine_golden_png_created",
    "golden_quality_approved",
    "publication_ready",
)


@dataclass(frozen=True)
class ComposedCandidateByteAdmission:
    output_dir: Path
    receipt_path: Path
    story_snapshot_sha256: str
    composed_candidate_sha256: str


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


def _png_dimensions(path: Path) -> tuple[int, int]:
    raw = path.read_bytes()
    if len(raw) < 24 or raw[:8] != PNG_SIGNATURE or raw[12:16] != b"IHDR":
        raise ValueError("QWEN_COMPOSED_ADMISSION_PNG_INVALID")
    width, height = struct.unpack(">II", raw[16:24])
    if width <= 0 or height <= 0:
        raise ValueError("QWEN_COMPOSED_ADMISSION_PNG_DIMENSIONS_INVALID")
    return width, height


def _assert_authority(value: Mapping[str, Any], prefix: str) -> None:
    if value.get("composition_executed") is not True:
        raise ValueError(f"{prefix}_COMPOSITION_NOT_EXECUTED")
    for field in _DOWNSTREAM_FALSE:
        if value.get(field) is not False:
            raise ValueError(f"{prefix}_PREMATURE_AUTHORITY:{field}")


def admit_composed_candidate_bytes(
    cs271_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> ComposedCandidateByteAdmission:
    """Revalidate and byte-bind one CS271 composed candidate without approving it."""
    if output_dir.exists():
        raise ValueError("QWEN_COMPOSED_ADMISSION_OUTPUT_ALREADY_EXISTS")
    if not output_dir.parent.is_dir():
        raise ValueError("QWEN_COMPOSED_ADMISSION_OUTPUT_PARENT_INVALID")

    source_binding = _bind_file(
        repo_root, cs271_receipt_path, "QWEN_COMPOSED_ADMISSION_CS271_INVALID"
    )
    source = verify_one_shot_composition_execution(
        cs271_receipt_path, repo_root=repo_root
    )
    if source.get("schema") != CS271_SCHEMA:
        raise ValueError("QWEN_COMPOSED_ADMISSION_CS271_SCHEMA_DRIFT")
    _assert_authority(source, "QWEN_COMPOSED_ADMISSION_CS271")

    story_sha = source.get("story_snapshot_sha256")
    composed = source.get("composed_candidate_png")
    candidate = source.get("candidate_png")
    if not _is_sha256(story_sha) or not isinstance(composed, Mapping) or not isinstance(candidate, Mapping):
        raise ValueError("QWEN_COMPOSED_ADMISSION_UPSTREAM_BINDING_INVALID")

    composed_path = _reopen_binding(
        repo_root, composed, "QWEN_COMPOSED_ADMISSION_PNG_INVALID"
    )
    width, height = _png_dimensions(composed_path)
    if composed.get("width") != width or composed.get("height") != height:
        raise ValueError("QWEN_COMPOSED_ADMISSION_PNG_DIMENSION_DRIFT")
    if candidate.get("width") != width or candidate.get("height") != height:
        raise ValueError("QWEN_COMPOSED_ADMISSION_CANVAS_DIMENSION_DRIFT")

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "QWEN_IMAGE_COMPOSED_CANDIDATE_BYTES_ADMITTED_FOR_POST_COMPOSITION_QA",
        "story_snapshot_sha256": story_sha,
        "source_cs271_receipt": {
            **source_binding,
            "receipt_sha256": source.get("receipt_sha256"),
        },
        "source_candidate_png": dict(candidate),
        "composed_candidate_png": dict(composed),
        "runner_id": source.get("runner_id"),
        "composition_executed": True,
        "composed_candidate_bytes_admitted_for_post_composition_qa": True,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "genuine_golden_png_created": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "policy": {
            "cs271_must_reverify": True,
            "exact_composed_png_bytes_must_reopen": True,
            "canvas_dimensions_must_match_source_candidate": True,
            "byte_admission_is_not_visual_approval": True,
            "post_composition_qa_must_consume_this_exact_png": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)

    output_dir.mkdir(mode=0o700)
    receipt_path = output_dir / "composed_candidate_byte_admission_receipt.json"
    tmp = output_dir / ".composed_candidate_byte_admission_receipt.json.tmp"
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

    return ComposedCandidateByteAdmission(
        output_dir=output_dir,
        receipt_path=receipt_path,
        story_snapshot_sha256=story_sha,
        composed_candidate_sha256=str(composed.get("sha256")),
    )


def verify_composed_candidate_byte_admission(
    receipt_path: Path, *, repo_root: Path
) -> dict[str, Any]:
    if receipt_path.is_symlink() or not receipt_path.is_file():
        raise ValueError("QWEN_COMPOSED_ADMISSION_RECEIPT_INVALID")
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("QWEN_COMPOSED_ADMISSION_RECEIPT_INVALID") from exc
    if not isinstance(receipt, dict) or receipt.get("schema") != SCHEMA:
        raise ValueError("QWEN_COMPOSED_ADMISSION_SCHEMA_DRIFT")

    claimed = receipt.get("receipt_sha256")
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    if not _is_sha256(claimed) or claimed != sha256_json(unsigned):
        raise ValueError("QWEN_COMPOSED_ADMISSION_RECEIPT_DIGEST_MISMATCH")
    _assert_authority(receipt, "QWEN_COMPOSED_ADMISSION")
    if receipt.get("composed_candidate_bytes_admitted_for_post_composition_qa") is not True:
        raise ValueError("QWEN_COMPOSED_ADMISSION_AUTHORITY_MISSING")

    source_binding = receipt.get("source_cs271_receipt")
    source_candidate = receipt.get("source_candidate_png")
    composed = receipt.get("composed_candidate_png")
    if not all(isinstance(item, Mapping) for item in (source_binding, source_candidate, composed)):
        raise ValueError("QWEN_COMPOSED_ADMISSION_BINDING_INVALID")

    source_path = _reopen_binding(
        repo_root, source_binding, "QWEN_COMPOSED_ADMISSION_CS271_INVALID"
    )
    source = verify_one_shot_composition_execution(source_path, repo_root=repo_root)
    _assert_authority(source, "QWEN_COMPOSED_ADMISSION_CS271")
    if source.get("schema") != CS271_SCHEMA:
        raise ValueError("QWEN_COMPOSED_ADMISSION_CS271_SCHEMA_DRIFT")
    if source.get("receipt_sha256") != source_binding.get("receipt_sha256"):
        raise ValueError("QWEN_COMPOSED_ADMISSION_CS271_RECEIPT_DRIFT")
    if source.get("story_snapshot_sha256") != receipt.get("story_snapshot_sha256"):
        raise ValueError("QWEN_COMPOSED_ADMISSION_CROSS_STORY")
    if source.get("candidate_png") != source_candidate or source.get("composed_candidate_png") != composed:
        raise ValueError("QWEN_COMPOSED_ADMISSION_UPSTREAM_BINDING_DRIFT")

    composed_path = _reopen_binding(
        repo_root, composed, "QWEN_COMPOSED_ADMISSION_PNG_INVALID"
    )
    width, height = _png_dimensions(composed_path)
    if composed.get("width") != width or composed.get("height") != height:
        raise ValueError("QWEN_COMPOSED_ADMISSION_PNG_DIMENSION_DRIFT")
    if source_candidate.get("width") != width or source_candidate.get("height") != height:
        raise ValueError("QWEN_COMPOSED_ADMISSION_CANVAS_DIMENSION_DRIFT")
    return receipt
