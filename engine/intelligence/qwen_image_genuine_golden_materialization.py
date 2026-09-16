"""CS285: materialize an exact-byte Genuine Golden Visual only after CS284 allows publication.

This stage does not generate or alter image pixels. It re-verifies the real CS284
SemanticPublicationGate decision, re-opens the exact composed PNG, validates PNG
container integrity, writes an exact byte-for-byte Golden artifact, and records
immutable provenance. Publication readiness remains a separate downstream authority.
"""
from __future__ import annotations

import hashlib
import json
import os
import struct
import zlib
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_composed_candidate_semantic_publication_execution import (
    SCHEMA as CS284_SCHEMA,
    verify_semantic_publication_execution,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-qwen-image-genuine-golden-materialization-v1"
STATUS = "QWEN_IMAGE_GENUINE_GOLDEN_VISUAL_MATERIALIZED"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MATERIALIZATION_POLICY = {
    "pixel_mutation_forbidden": True,
    "source_must_be_cs284_allowed_exact_png": True,
    "genuine_golden_creation_does_not_set_publication_ready": True,
}


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
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(code) from exc
    raw = resolved.read_bytes()
    if not raw:
        raise ValueError(code)
    return {
        "repository_relative_path": relative,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
    }


def _reopen(root: Path, binding: Mapping[str, Any], code: str) -> Path:
    relative = binding.get("repository_relative_path")
    if (
        not isinstance(relative, str)
        or not relative
        or Path(relative).is_absolute()
        or ".." in Path(relative).parts
    ):
        raise ValueError(code)
    path = root.resolve() / relative
    current = _bind(root, path, code)
    for field in ("repository_relative_path", "sha256", "byte_size"):
        if current[field] != binding.get(field):
            raise ValueError(f"{code}_BYTE_DRIFT")
    return path


def _validate_png_bytes(raw: bytes) -> tuple[int, int]:
    """Validate signature, chunk framing/CRC, IHDR dimensions and terminal IEND."""
    if not raw.startswith(PNG_SIGNATURE):
        raise ValueError("QWEN_GENUINE_GOLDEN_PNG_SIGNATURE_INVALID")
    offset = len(PNG_SIGNATURE)
    seen_ihdr = False
    seen_iend = False
    width = height = 0
    while offset < len(raw):
        if offset + 12 > len(raw):
            raise ValueError("QWEN_GENUINE_GOLDEN_PNG_CHUNK_TRUNCATED")
        length = struct.unpack(">I", raw[offset : offset + 4])[0]
        chunk_type = raw[offset + 4 : offset + 8]
        data_start = offset + 8
        data_end = data_start + length
        crc_end = data_end + 4
        if crc_end > len(raw):
            raise ValueError("QWEN_GENUINE_GOLDEN_PNG_CHUNK_TRUNCATED")
        data = raw[data_start:data_end]
        expected_crc = struct.unpack(">I", raw[data_end:crc_end])[0]
        actual_crc = zlib.crc32(chunk_type)
        actual_crc = zlib.crc32(data, actual_crc) & 0xFFFFFFFF
        if expected_crc != actual_crc:
            raise ValueError("QWEN_GENUINE_GOLDEN_PNG_CRC_INVALID")
        if not seen_ihdr:
            if chunk_type != b"IHDR" or length != 13:
                raise ValueError("QWEN_GENUINE_GOLDEN_PNG_IHDR_INVALID")
            width, height = struct.unpack(">II", data[:8])
            if width <= 0 or height <= 0:
                raise ValueError("QWEN_GENUINE_GOLDEN_PNG_DIMENSIONS_INVALID")
            seen_ihdr = True
        elif chunk_type == b"IHDR":
            raise ValueError("QWEN_GENUINE_GOLDEN_PNG_DUPLICATE_IHDR")
        if chunk_type == b"IEND":
            if length != 0 or crc_end != len(raw):
                raise ValueError("QWEN_GENUINE_GOLDEN_PNG_IEND_INVALID")
            seen_iend = True
            break
        offset = crc_end
    if not seen_ihdr or not seen_iend:
        raise ValueError("QWEN_GENUINE_GOLDEN_PNG_STRUCTURE_INVALID")
    return width, height


def _require_cs284_authority(cs284: Mapping[str, Any]) -> None:
    expected_true = (
        "composed_visual_approved",
        "semantic_approved",
        "semantic_publication_execution_requested",
        "semantic_publication_gate_executed",
        "semantic_publication_allowed",
    )
    for field in expected_true:
        if cs284.get(field) is not True:
            raise ValueError(f"QWEN_GENUINE_GOLDEN_CS284_AUTHORITY_MISSING:{field}")
    if cs284.get("genuine_golden_png_created") is not False:
        raise ValueError("QWEN_GENUINE_GOLDEN_CS284_PREMATURE_GOLDEN_STATE")
    if cs284.get("publication_ready") is not False:
        raise ValueError("QWEN_GENUINE_GOLDEN_CS284_PREMATURE_PUBLICATION_STATE")
    failures = cs284.get("semantic_publication_failures")
    if not isinstance(failures, list) or failures:
        raise ValueError("QWEN_GENUINE_GOLDEN_CS284_FAILURE_STATE_INVALID")


def _require_materialization_receipt_matches_cs284(
    receipt: Mapping[str, Any],
    cs284: Mapping[str, Any],
) -> None:
    """Bind all CS285 metadata consumed downstream to the exact verified CS284 state."""
    generation_context = cs284.get("generation_context")
    source_png = cs284.get("composed_candidate_png")
    if not isinstance(generation_context, Mapping) or not isinstance(source_png, Mapping):
        raise ValueError("QWEN_GENUINE_GOLDEN_CS284_LINEAGE_INVALID")

    expected = {
        "story_snapshot_sha256": cs284.get("story_snapshot_sha256"),
        "source_composed_candidate_png": dict(source_png),
        "generation_context": dict(generation_context),
        "weighted_score": cs284.get("weighted_score"),
        "quality_tier": cs284.get("quality_tier"),
    }
    for field, value in expected.items():
        if receipt.get(field) != value:
            raise ValueError(f"QWEN_GENUINE_GOLDEN_CS284_LINEAGE_DRIFT:{field}")

    policy = receipt.get("policy")
    if not isinstance(policy, Mapping) or dict(policy) != MATERIALIZATION_POLICY:
        raise ValueError("QWEN_GENUINE_GOLDEN_POLICY_DRIFT")


def materialize_genuine_golden_visual(
    cs284_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> Path:
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("QWEN_GENUINE_GOLDEN_OUTPUT_INVALID")

    cs284_binding = _bind(repo_root, cs284_receipt_path, "QWEN_GENUINE_GOLDEN_CS284_INVALID")
    cs284 = verify_semantic_publication_execution(cs284_receipt_path, repo_root=repo_root)
    if cs284.get("schema") != CS284_SCHEMA:
        raise ValueError("QWEN_GENUINE_GOLDEN_CS284_SCHEMA_INVALID")
    _require_cs284_authority(cs284)

    source_binding = cs284.get("composed_candidate_png")
    if not isinstance(source_binding, Mapping):
        raise ValueError("QWEN_GENUINE_GOLDEN_SOURCE_BINDING_INVALID")
    source_path = _reopen(repo_root, source_binding, "QWEN_GENUINE_GOLDEN_SOURCE_PNG_INVALID")
    source_raw = source_path.read_bytes()
    width, height = _validate_png_bytes(source_raw)

    output_dir.mkdir(mode=0o700)
    golden_path = output_dir / "genuine_golden_visual.png"
    receipt_path = output_dir / "genuine_golden_materialization.json"
    try:
        with golden_path.open("xb") as handle:
            handle.write(source_raw)
            handle.flush()
            os.fsync(handle.fileno())
        golden_binding = _bind(repo_root, golden_path, "QWEN_GENUINE_GOLDEN_MATERIALIZED_PNG_INVALID")
        if golden_binding["sha256"] != source_binding.get("sha256") or golden_binding["byte_size"] != source_binding.get("byte_size"):
            raise ValueError("QWEN_GENUINE_GOLDEN_BYTE_IDENTITY_FAILED")

        receipt: dict[str, Any] = {
            "schema": SCHEMA,
            "status": STATUS,
            "story_snapshot_sha256": cs284["story_snapshot_sha256"],
            "source_cs284_semantic_publication_execution": {
                **cs284_binding,
                "receipt_sha256": cs284.get("receipt_sha256"),
            },
            "source_composed_candidate_png": dict(source_binding),
            "genuine_golden_visual_png": golden_binding,
            "png_dimensions": {"width": width, "height": height},
            "generation_context": dict(cs284["generation_context"]),
            "weighted_score": cs284["weighted_score"],
            "quality_tier": cs284["quality_tier"],
            "composed_visual_approved": True,
            "semantic_approved": True,
            "semantic_publication_gate_executed": True,
            "semantic_publication_allowed": True,
            "byte_identity_preserved": True,
            "genuine_golden_png_created": True,
            "publication_ready": False,
            "policy": dict(MATERIALIZATION_POLICY),
        }
        receipt["receipt_sha256"] = sha256_json(receipt)
        tmp = output_dir / ".genuine_golden_materialization.json.tmp"
        with tmp.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, receipt_path)
    except Exception:
        for candidate in (
            output_dir / ".genuine_golden_materialization.json.tmp",
            receipt_path,
            golden_path,
        ):
            if candidate.exists():
                candidate.unlink()
        if output_dir.exists() and not any(output_dir.iterdir()):
            output_dir.rmdir()
        raise
    return receipt_path


def verify_genuine_golden_materialization(receipt_path: Path, *, repo_root: Path) -> dict[str, Any]:
    receipt = _json(receipt_path, "QWEN_GENUINE_GOLDEN_RECEIPT_INVALID")
    unsigned = dict(receipt)
    claimed = unsigned.pop("receipt_sha256", None)
    if receipt.get("schema") != SCHEMA or receipt.get("status") != STATUS or claimed != sha256_json(unsigned):
        raise ValueError("QWEN_GENUINE_GOLDEN_RECEIPT_INVALID")

    source = receipt.get("source_cs284_semantic_publication_execution")
    if not isinstance(source, Mapping):
        raise ValueError("QWEN_GENUINE_GOLDEN_CS284_BINDING_INVALID")
    cs284_path = _reopen(repo_root, source, "QWEN_GENUINE_GOLDEN_CS284_INVALID")
    cs284 = verify_semantic_publication_execution(cs284_path, repo_root=repo_root)
    if cs284.get("schema") != CS284_SCHEMA:
        raise ValueError("QWEN_GENUINE_GOLDEN_CS284_SCHEMA_INVALID")
    _require_cs284_authority(cs284)
    if source.get("receipt_sha256") != cs284.get("receipt_sha256"):
        raise ValueError("QWEN_GENUINE_GOLDEN_CS284_RECEIPT_DRIFT")
    _require_materialization_receipt_matches_cs284(receipt, cs284)

    source_png = receipt.get("source_composed_candidate_png")
    golden_png = receipt.get("genuine_golden_visual_png")
    if not isinstance(source_png, Mapping) or not isinstance(golden_png, Mapping):
        raise ValueError("QWEN_GENUINE_GOLDEN_PNG_BINDING_INVALID")
    source_path = _reopen(repo_root, source_png, "QWEN_GENUINE_GOLDEN_SOURCE_PNG_INVALID")
    golden_path = _reopen(repo_root, golden_png, "QWEN_GENUINE_GOLDEN_MATERIALIZED_PNG_INVALID")
    width, height = _validate_png_bytes(golden_path.read_bytes())
    if source_path.read_bytes() != golden_path.read_bytes():
        raise ValueError("QWEN_GENUINE_GOLDEN_BYTE_IDENTITY_FAILED")

    expected = {
        "story_snapshot_sha256": cs284["story_snapshot_sha256"],
        "source_composed_candidate_png": dict(cs284["composed_candidate_png"]),
        "png_dimensions": {"width": width, "height": height},
        "generation_context": dict(cs284["generation_context"]),
        "weighted_score": cs284["weighted_score"],
        "quality_tier": cs284["quality_tier"],
        "composed_visual_approved": True,
        "semantic_approved": True,
        "semantic_publication_gate_executed": True,
        "semantic_publication_allowed": True,
        "byte_identity_preserved": True,
        "genuine_golden_png_created": True,
        "publication_ready": False,
    }
    for field, value in expected.items():
        if receipt.get(field) != value:
            raise ValueError(f"QWEN_GENUINE_GOLDEN_STATE_DRIFT:{field}")
    if golden_png.get("sha256") != source_png.get("sha256") or golden_png.get("byte_size") != source_png.get("byte_size"):
        raise ValueError("QWEN_GENUINE_GOLDEN_BYTE_BINDING_DRIFT")
    return receipt