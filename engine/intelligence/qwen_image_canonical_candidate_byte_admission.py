"""Byte-admit one sealed canonical candidate for downstream visual QA.

Change Set 303 upgrades the original CS263 admission edge so production
post-generation QA can no longer start from a bare CS262 receipt.  Admission
must start from the CS301/302 canonical-candidate handoff, replay that sealed
lineage, and derive the exact canonical inference receipt and PNG from the
handoff bindings.

Admission is still non-semantic and non-generative.  It never upgrades a
candidate into a Golden Visual and never grants publication authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import struct
from typing import Any, Mapping

from engine.intelligence.qwen_image_canonical_candidate_handoff import (
    SCHEMA as CANONICAL_CANDIDATE_HANDOFF_SCHEMA,
    verify_canonical_candidate_handoff,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json
from engine.intelligence.qwen_image_one_shot_canonical_inference import (
    ONE_SHOT_CANONICAL_INFERENCE_SCHEMA,
    verify_one_shot_canonical_inference,
)

CANONICAL_CANDIDATE_BYTE_ADMISSION_SCHEMA = (
    "pul7sar-phase18-qwen-image-2512-canonical-candidate-byte-admission-v2"
)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_REQUIRED_TRUE = (
    "genuine_canonical_inference_executed",
    "handoff_sealed",
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


def _assert_handoff_authority(payload: Mapping[str, Any]) -> None:
    for field in _REQUIRED_TRUE:
        if payload.get(field) is not True:
            raise ValueError(f"QWEN_CANDIDATE_ADMISSION_REQUIRED_GATE_MISSING:{field}")
    for field in _REQUIRED_FALSE:
        if payload.get(field) is not False:
            raise ValueError(f"QWEN_CANDIDATE_ADMISSION_PREMATURE_AUTHORITY:{field}")
    if payload.get("cost_mode") != "$0-local":
        raise ValueError("QWEN_CANDIDATE_ADMISSION_COST_MODE_DRIFT")
    if payload.get("network_allowed") is not False or payload.get("local_files_only") is not True:
        raise ValueError("QWEN_CANDIDATE_ADMISSION_LOCAL_ONLY_DRIFT")


def _binding_path(
    repo_root: Path,
    binding: Mapping[str, Any],
    *,
    code: str,
) -> Path:
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
    current = _file_binding(path, code)
    if binding.get("sha256") != current["sha256"] or binding.get("byte_size") != current["byte_size"]:
        raise ValueError(f"{code}_BYTE_DRIFT")
    return path


def admit_canonical_candidate_bytes(
    candidate_handoff_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> CanonicalCandidateByteAdmission:
    """Replay a CS301/302 handoff and byte-admit its exact candidate only."""
    if output_dir.exists():
        raise ValueError("QWEN_CANDIDATE_ADMISSION_OUTPUT_ALREADY_EXISTS")
    if not output_dir.parent.is_dir():
        raise ValueError("QWEN_CANDIDATE_ADMISSION_OUTPUT_PARENT_INVALID")

    handoff_relative = _inside_repo_file(
        repo_root,
        candidate_handoff_path,
        "QWEN_CANDIDATE_ADMISSION_HANDOFF_OUTSIDE_REPOSITORY",
    )
    handoff_binding = _file_binding(
        candidate_handoff_path,
        "QWEN_CANDIDATE_ADMISSION_HANDOFF_INVALID",
    )
    handoff = verify_canonical_candidate_handoff(
        candidate_handoff_path,
        repo_root=repo_root,
    )
    if handoff.get("schema") != CANONICAL_CANDIDATE_HANDOFF_SCHEMA:
        raise ValueError("QWEN_CANDIDATE_ADMISSION_HANDOFF_SCHEMA_DRIFT")
    _assert_handoff_authority(handoff)

    bindings = handoff.get("source_bindings")
    if not isinstance(bindings, Mapping):
        raise ValueError("QWEN_CANDIDATE_ADMISSION_HANDOFF_BINDINGS_INVALID")
    source_binding = bindings.get("canonical_inference_receipt.json")
    candidate_binding = handoff.get("canonical_candidate_png")
    if not isinstance(source_binding, Mapping) or not isinstance(candidate_binding, Mapping):
        raise ValueError("QWEN_CANDIDATE_ADMISSION_HANDOFF_BINDINGS_INVALID")

    source_path = _binding_path(
        repo_root,
        source_binding,
        code="QWEN_CANDIDATE_ADMISSION_CANONICAL_RECEIPT_INVALID",
    )
    candidate_path = _binding_path(
        repo_root,
        candidate_binding,
        code="QWEN_CANDIDATE_ADMISSION_PNG_INVALID",
    )
    source_relative = _inside_repo_file(
        repo_root,
        source_path,
        "QWEN_CANDIDATE_ADMISSION_CANONICAL_RECEIPT_OUTSIDE_REPOSITORY",
    )
    source_file_binding = _file_binding(
        source_path,
        "QWEN_CANDIDATE_ADMISSION_CANONICAL_RECEIPT_INVALID",
    )
    candidate_relative = _inside_repo_file(
        repo_root,
        candidate_path,
        "QWEN_CANDIDATE_ADMISSION_PNG_OUTSIDE_REPOSITORY",
    )
    candidate_file_binding = _file_binding(
        candidate_path,
        "QWEN_CANDIDATE_ADMISSION_PNG_INVALID",
    )

    source = verify_one_shot_canonical_inference(source_path, repo_root=repo_root)
    if source.get("schema") != ONE_SHOT_CANONICAL_INFERENCE_SCHEMA:
        raise ValueError("QWEN_CANDIDATE_ADMISSION_CANONICAL_SCHEMA_DRIFT")
    for field in _REQUIRED_FALSE:
        if source.get(field) is not False:
            raise ValueError(f"QWEN_CANDIDATE_ADMISSION_PREMATURE_AUTHORITY:{field}")
    if source.get("genuine_canonical_inference_executed") is not True:
        raise ValueError("QWEN_CANDIDATE_ADMISSION_GENUINE_INFERENCE_MISSING")

    story_sha = handoff.get("story_snapshot_sha256")
    if not _is_sha256(story_sha) or source.get("story_snapshot_sha256") != story_sha:
        raise ValueError("QWEN_CANDIDATE_ADMISSION_CROSS_STORY")
    png_meta = source.get("png")
    if not isinstance(png_meta, Mapping) or png_meta.get("filename") != "canonical_candidate.png":
        raise ValueError("QWEN_CANDIDATE_ADMISSION_PNG_BINDING_INVALID")
    if (
        png_meta.get("sha256") != candidate_file_binding["sha256"]
        or png_meta.get("byte_size") != candidate_file_binding["byte_size"]
        or candidate_binding.get("sha256") != candidate_file_binding["sha256"]
        or candidate_binding.get("byte_size") != candidate_file_binding["byte_size"]
    ):
        raise ValueError("QWEN_CANDIDATE_ADMISSION_PNG_BYTE_DRIFT")

    width, height = _png_dimensions(candidate_path.read_bytes())
    if any(
        value != expected
        for value, expected in (
            (png_meta.get("width"), width),
            (png_meta.get("height"), height),
            (source.get("width"), width),
            (source.get("height"), height),
            (candidate_binding.get("width"), width),
            (candidate_binding.get("height"), height),
        )
    ):
        raise ValueError("QWEN_CANDIDATE_ADMISSION_PNG_DIMENSION_DRIFT")

    receipt = {
        "schema": CANONICAL_CANDIDATE_BYTE_ADMISSION_SCHEMA,
        "status": "QWEN_IMAGE_2512_SEALED_CANONICAL_CANDIDATE_BYTES_ADMITTED_FOR_POST_GENERATION_QA",
        "story_snapshot_sha256": story_sha,
        "model_id": handoff.get("model_id"),
        "model_revision": handoff.get("model_revision"),
        "cost_mode": "$0-local",
        "network_allowed": False,
        "local_files_only": True,
        "source_candidate_handoff": {
            "repository_relative_path": handoff_relative,
            **handoff_binding,
            "handoff_sha256": handoff.get("handoff_sha256"),
        },
        "source_canonical_inference_receipt": {
            "repository_relative_path": source_relative,
            **source_file_binding,
            "receipt_sha256": source.get("receipt_sha256"),
        },
        "candidate_png": {
            "repository_relative_path": candidate_relative,
            **candidate_file_binding,
            "width": width,
            "height": height,
        },
        "inference_settings": dict(handoff.get("inference_settings", {})),
        "genuine_canonical_inference_executed": True,
        "handoff_sealed": True,
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
        candidate_sha256=candidate_file_binding["sha256"],
    )


def verify_canonical_candidate_byte_admission(
    receipt_path: Path, *, repo_root: Path
) -> dict[str, Any]:
    """Replay an admission, its sealed handoff, canonical receipt and candidate bytes."""
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
    _assert_handoff_authority(receipt)
    if receipt.get("candidate_bytes_admitted_for_post_generation_qa") is not True:
        raise ValueError("QWEN_CANDIDATE_ADMISSION_AUTHORITY_MISSING")

    handoff_meta = receipt.get("source_candidate_handoff")
    source_meta = receipt.get("source_canonical_inference_receipt")
    candidate_meta = receipt.get("candidate_png")
    if not all(isinstance(value, Mapping) for value in (handoff_meta, source_meta, candidate_meta)):
        raise ValueError("QWEN_CANDIDATE_ADMISSION_BINDING_INVALID")

    handoff_path = _binding_path(
        repo_root,
        handoff_meta,
        code="QWEN_CANDIDATE_ADMISSION_HANDOFF_INVALID",
    )
    handoff = verify_canonical_candidate_handoff(handoff_path, repo_root=repo_root)
    _assert_handoff_authority(handoff)
    if handoff_meta.get("handoff_sha256") != handoff.get("handoff_sha256"):
        raise ValueError("QWEN_CANDIDATE_ADMISSION_HANDOFF_DIGEST_DRIFT")

    source_path = _binding_path(
        repo_root,
        source_meta,
        code="QWEN_CANDIDATE_ADMISSION_CANONICAL_RECEIPT_INVALID",
    )
    candidate_path = _binding_path(
        repo_root,
        candidate_meta,
        code="QWEN_CANDIDATE_ADMISSION_PNG_INVALID",
    )
    source = verify_one_shot_canonical_inference(source_path, repo_root=repo_root)
    if source_meta.get("receipt_sha256") != source.get("receipt_sha256"):
        raise ValueError("QWEN_CANDIDATE_ADMISSION_CANONICAL_DIGEST_DRIFT")
    if source.get("story_snapshot_sha256") != receipt.get("story_snapshot_sha256"):
        raise ValueError("QWEN_CANDIDATE_ADMISSION_CROSS_STORY")

    handoff_candidate = handoff.get("canonical_candidate_png")
    if not isinstance(handoff_candidate, Mapping):
        raise ValueError("QWEN_CANDIDATE_ADMISSION_HANDOFF_CANDIDATE_INVALID")
    for field in ("repository_relative_path", "sha256", "byte_size", "width", "height"):
        if candidate_meta.get(field) != handoff_candidate.get(field):
            raise ValueError(f"QWEN_CANDIDATE_ADMISSION_HANDOFF_CANDIDATE_DRIFT:{field}")
    width, height = _png_dimensions(candidate_path.read_bytes())
    if candidate_meta.get("width") != width or candidate_meta.get("height") != height:
        raise ValueError("QWEN_CANDIDATE_ADMISSION_PNG_DIMENSION_DRIFT")
    return receipt
