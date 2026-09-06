"""CS286: grant final publication readiness only to a verified CS285 Genuine Golden artifact.

This stage performs no image generation, editing, decoding/re-encoding, or publication side
effect. It re-verifies CS285, re-opens the exact composed source and Genuine Golden PNG,
requires byte identity, and records the final publication-readiness authority.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_genuine_golden_materialization import (
    SCHEMA as CS285_SCHEMA,
    _validate_png_bytes,
    verify_genuine_golden_materialization,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-qwen-image-genuine-golden-publication-readiness-v1"
STATUS = "QWEN_IMAGE_GENUINE_GOLDEN_PUBLICATION_READY"

PUBLICATION_POLICY = {
    "final_authority_consumes_verified_cs285_only": True,
    "pixel_mutation_forbidden": True,
    "publication_readiness_has_no_publish_side_effect": True,
    "publication_ready_requires_exact_genuine_golden_bytes": True,
}

PUBLICATION_RECEIPT_FIELDS = frozenset(
    {
        "schema",
        "status",
        "story_snapshot_sha256",
        "source_cs285_genuine_golden_materialization",
        "source_composed_candidate_png",
        "genuine_golden_visual_png",
        "png_dimensions",
        "generation_context",
        "weighted_score",
        "quality_tier",
        "composed_visual_approved",
        "semantic_approved",
        "semantic_publication_gate_executed",
        "semantic_publication_allowed",
        "byte_identity_preserved",
        "genuine_golden_png_created",
        "publication_ready",
        "policy",
        "receipt_sha256",
    }
)


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


def _require_cs285_authority(cs285: Mapping[str, Any]) -> None:
    expected_true = (
        "composed_visual_approved",
        "semantic_approved",
        "semantic_publication_gate_executed",
        "semantic_publication_allowed",
        "byte_identity_preserved",
        "genuine_golden_png_created",
    )
    for field in expected_true:
        if cs285.get(field) is not True:
            raise ValueError(f"QWEN_GENUINE_GOLDEN_PUBLICATION_CS285_AUTHORITY_MISSING:{field}")
    if cs285.get("publication_ready") is not False:
        raise ValueError("QWEN_GENUINE_GOLDEN_PUBLICATION_CS285_PREMATURE_PUBLICATION_STATE")
    policy = cs285.get("policy")
    if not isinstance(policy, Mapping):
        raise ValueError("QWEN_GENUINE_GOLDEN_PUBLICATION_CS285_POLICY_INVALID")
    required_policy_true = (
        "pixel_mutation_forbidden",
        "source_must_be_cs284_allowed_exact_png",
        "genuine_golden_creation_does_not_set_publication_ready",
    )
    for field in required_policy_true:
        if policy.get(field) is not True:
            raise ValueError(f"QWEN_GENUINE_GOLDEN_PUBLICATION_CS285_POLICY_MISSING:{field}")


def _require_exact_publication_envelope(receipt: Mapping[str, Any]) -> None:
    if set(receipt) != PUBLICATION_RECEIPT_FIELDS:
        raise ValueError("QWEN_GENUINE_GOLDEN_PUBLICATION_ENVELOPE_FIELDS_INVALID")
    if receipt.get("policy") != PUBLICATION_POLICY:
        raise ValueError("QWEN_GENUINE_GOLDEN_PUBLICATION_POLICY_INVALID")


def _require_output_inside_repo(repo_root: Path, output_dir: Path) -> None:
    try:
        output_dir.resolve().relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ValueError("QWEN_GENUINE_GOLDEN_PUBLICATION_OUTPUT_OUTSIDE_REPOSITORY") from exc


def finalize_genuine_golden_publication_readiness(
    cs285_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> Path:
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("QWEN_GENUINE_GOLDEN_PUBLICATION_OUTPUT_INVALID")
    _require_output_inside_repo(repo_root, output_dir)

    cs285_binding = _bind(
        repo_root,
        cs285_receipt_path,
        "QWEN_GENUINE_GOLDEN_PUBLICATION_CS285_INVALID",
    )
    cs285 = verify_genuine_golden_materialization(cs285_receipt_path, repo_root=repo_root)
    if cs285.get("schema") != CS285_SCHEMA:
        raise ValueError("QWEN_GENUINE_GOLDEN_PUBLICATION_CS285_SCHEMA_INVALID")
    _require_cs285_authority(cs285)

    source_binding = cs285.get("source_composed_candidate_png")
    golden_binding = cs285.get("genuine_golden_visual_png")
    if not isinstance(source_binding, Mapping) or not isinstance(golden_binding, Mapping):
        raise ValueError("QWEN_GENUINE_GOLDEN_PUBLICATION_PNG_BINDING_INVALID")

    source_path = _reopen(
        repo_root,
        source_binding,
        "QWEN_GENUINE_GOLDEN_PUBLICATION_SOURCE_PNG_INVALID",
    )
    golden_path = _reopen(
        repo_root,
        golden_binding,
        "QWEN_GENUINE_GOLDEN_PUBLICATION_GOLDEN_PNG_INVALID",
    )
    source_raw = source_path.read_bytes()
    golden_raw = golden_path.read_bytes()
    if source_raw != golden_raw:
        raise ValueError("QWEN_GENUINE_GOLDEN_PUBLICATION_BYTE_IDENTITY_FAILED")
    width, height = _validate_png_bytes(golden_raw)
    if cs285.get("png_dimensions") != {"width": width, "height": height}:
        raise ValueError("QWEN_GENUINE_GOLDEN_PUBLICATION_DIMENSION_DRIFT")

    output_dir.mkdir(mode=0o700)
    receipt_path = output_dir / "genuine_golden_publication_readiness.json"
    try:
        receipt: dict[str, Any] = {
            "schema": SCHEMA,
            "status": STATUS,
            "story_snapshot_sha256": cs285["story_snapshot_sha256"],
            "source_cs285_genuine_golden_materialization": {
                **cs285_binding,
                "receipt_sha256": cs285.get("receipt_sha256"),
            },
            "source_composed_candidate_png": dict(source_binding),
            "genuine_golden_visual_png": dict(golden_binding),
            "png_dimensions": {"width": width, "height": height},
            "generation_context": dict(cs285["generation_context"]),
            "weighted_score": cs285["weighted_score"],
            "quality_tier": cs285["quality_tier"],
            "composed_visual_approved": True,
            "semantic_approved": True,
            "semantic_publication_gate_executed": True,
            "semantic_publication_allowed": True,
            "byte_identity_preserved": True,
            "genuine_golden_png_created": True,
            "publication_ready": True,
            "policy": dict(PUBLICATION_POLICY),
        }
        receipt["receipt_sha256"] = sha256_json(receipt)
        tmp = output_dir / ".genuine_golden_publication_readiness.json.tmp"
        with tmp.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, receipt_path)
    except Exception:
        for candidate in (
            output_dir / ".genuine_golden_publication_readiness.json.tmp",
            receipt_path,
        ):
            if candidate.exists():
                candidate.unlink()
        if output_dir.exists() and not any(output_dir.iterdir()):
            output_dir.rmdir()
        raise
    return receipt_path


def verify_genuine_golden_publication_readiness(
    receipt_path: Path,
    *,
    repo_root: Path,
) -> dict[str, Any]:
    receipt = _json(receipt_path, "QWEN_GENUINE_GOLDEN_PUBLICATION_RECEIPT_INVALID")
    unsigned = dict(receipt)
    claimed = unsigned.pop("receipt_sha256", None)
    if receipt.get("schema") != SCHEMA or receipt.get("status") != STATUS or claimed != sha256_json(unsigned):
        raise ValueError("QWEN_GENUINE_GOLDEN_PUBLICATION_RECEIPT_INVALID")
    _require_exact_publication_envelope(receipt)

    source = receipt.get("source_cs285_genuine_golden_materialization")
    if not isinstance(source, Mapping):
        raise ValueError("QWEN_GENUINE_GOLDEN_PUBLICATION_CS285_BINDING_INVALID")
    cs285_path = _reopen(repo_root, source, "QWEN_GENUINE_GOLDEN_PUBLICATION_CS285_INVALID")
    cs285 = verify_genuine_golden_materialization(cs285_path, repo_root=repo_root)
    if cs285.get("schema") != CS285_SCHEMA:
        raise ValueError("QWEN_GENUINE_GOLDEN_PUBLICATION_CS285_SCHEMA_INVALID")
    _require_cs285_authority(cs285)
    if source.get("receipt_sha256") != cs285.get("receipt_sha256"):
        raise ValueError("QWEN_GENUINE_GOLDEN_PUBLICATION_CS285_RECEIPT_DRIFT")

    source_png = receipt.get("source_composed_candidate_png")
    golden_png = receipt.get("genuine_golden_visual_png")
    if not isinstance(source_png, Mapping) or not isinstance(golden_png, Mapping):
        raise ValueError("QWEN_GENUINE_GOLDEN_PUBLICATION_PNG_BINDING_INVALID")
    source_path = _reopen(repo_root, source_png, "QWEN_GENUINE_GOLDEN_PUBLICATION_SOURCE_PNG_INVALID")
    golden_path = _reopen(repo_root, golden_png, "QWEN_GENUINE_GOLDEN_PUBLICATION_GOLDEN_PNG_INVALID")
    source_raw = source_path.read_bytes()
    golden_raw = golden_path.read_bytes()
    if source_raw != golden_raw:
        raise ValueError("QWEN_GENUINE_GOLDEN_PUBLICATION_BYTE_IDENTITY_FAILED")
    width, height = _validate_png_bytes(golden_raw)

    expected = {
        "story_snapshot_sha256": cs285["story_snapshot_sha256"],
        "source_composed_candidate_png": dict(cs285["source_composed_candidate_png"]),
        "genuine_golden_visual_png": dict(cs285["genuine_golden_visual_png"]),
        "png_dimensions": {"width": width, "height": height},
        "generation_context": dict(cs285["generation_context"]),
        "weighted_score": cs285["weighted_score"],
        "quality_tier": cs285["quality_tier"],
        "composed_visual_approved": True,
        "semantic_approved": True,
        "semantic_publication_gate_executed": True,
        "semantic_publication_allowed": True,
        "byte_identity_preserved": True,
        "genuine_golden_png_created": True,
        "publication_ready": True,
    }
    for field, value in expected.items():
        if receipt.get(field) != value:
            raise ValueError(f"QWEN_GENUINE_GOLDEN_PUBLICATION_STATE_DRIFT:{field}")
    return receipt
