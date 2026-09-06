"""CS301/358: seal a genuine canonical Qwen candidate for downstream gate handoff.

The handoff is not an approval. It packages a replay-verified canonical candidate and
its exact evidence lineage into one byte-bound artifact that downstream semantic,
composition, visual-quality, human-review, brand/typography, Golden, and publication
gates can consume without trusting directory convention or operator-selected files.

CS358 also carries the CS357 exact local Qwen snapshot-byte inventory into the sealed
handoff so downstream QA can prove which already-local model/config/tokenizer bytes
produced the candidate without weakening any later approval gate.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from .qwen_image_inference_measurement import sha256_json
from .qwen_image_launch_to_output_attestation import verify_launch_to_output_attestation

SCHEMA = "pul7sar-phase18-qwen-image-2512-canonical-candidate-handoff-v1"
STATUS = "QWEN_IMAGE_2512_CANONICAL_CANDIDATE_HANDOFF_SEALED"
SOURCE_FILES = (
    "canonical_candidate.png",
    "canonical_inference_receipt.json",
    "local_inference_provenance.json",
    "launch_to_output_attestation.json",
)
DOWNSTREAM_FALSE = (
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "genuine_golden_png_created",
    "publication_ready",
)


def _sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value.lower()
    )


def _repo_file(path: Path, root: Path, code: str) -> tuple[Path, str]:
    candidate = path if path.is_absolute() else root / path
    if candidate.is_symlink():
        raise ValueError(code)
    resolved = candidate.resolve()
    try:
        relative = resolved.relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(code) from exc
    if not resolved.is_file():
        raise ValueError(code)
    return resolved, relative


def _binding(path: Path, root: Path, code: str) -> dict[str, Any]:
    resolved, relative = _repo_file(path, root, code)
    raw = resolved.read_bytes()
    if not raw:
        raise ValueError(code)
    return {
        "repository_relative_path": relative,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
    }


def _assert_downstream_closed(payload: Mapping[str, Any], prefix: str) -> None:
    for field in DOWNSTREAM_FALSE:
        if payload.get(field) is not False:
            raise ValueError(f"{prefix}:{field}")


def _snapshot_inventory_evidence(attestation: Mapping[str, Any]) -> dict[str, Any]:
    if attestation.get("snapshot_byte_inventory_verified") is not True:
        raise ValueError("QWEN_CANDIDATE_HANDOFF_SNAPSHOT_INVENTORY_AUTHORITY_MISSING")
    inventory = attestation.get("snapshot_byte_inventory")
    if not isinstance(inventory, Mapping):
        raise ValueError("QWEN_CANDIDATE_HANDOFF_SNAPSHOT_INVENTORY_MISSING")
    digest = inventory.get("snapshot_inventory_sha256")
    count = inventory.get("snapshot_file_count")
    total = inventory.get("snapshot_total_bytes")
    revision = inventory.get("model_revision")
    if not _sha(digest):
        raise ValueError("QWEN_CANDIDATE_HANDOFF_SNAPSHOT_INVENTORY_DIGEST_INVALID")
    if not isinstance(count, int) or count < 1:
        raise ValueError("QWEN_CANDIDATE_HANDOFF_SNAPSHOT_INVENTORY_FILE_COUNT_INVALID")
    if not isinstance(total, int) or total < 1:
        raise ValueError("QWEN_CANDIDATE_HANDOFF_SNAPSHOT_INVENTORY_BYTE_COUNT_INVALID")
    if revision != attestation.get("model_revision"):
        raise ValueError("QWEN_CANDIDATE_HANDOFF_SNAPSHOT_INVENTORY_REVISION_DRIFT")
    return {
        "snapshot_inventory_sha256": digest,
        "snapshot_file_count": count,
        "snapshot_total_bytes": total,
        "model_revision": revision,
    }


def build_canonical_candidate_handoff(
    output_dir: Path,
    handoff_path: Path,
    *,
    repo_root: Path,
) -> dict[str, Any]:
    """Create one immutable handoff only after replaying the CS293/357 evidence chain."""
    root = repo_root.resolve()
    output = output_dir if output_dir.is_absolute() else root / output_dir
    if output.is_symlink():
        raise ValueError("QWEN_CANDIDATE_HANDOFF_OUTPUT_DIR_INVALID")
    output = output.resolve()
    try:
        output.relative_to(root)
    except ValueError as exc:
        raise ValueError("QWEN_CANDIDATE_HANDOFF_OUTPUT_DIR_INVALID") from exc
    if not output.is_dir():
        raise ValueError("QWEN_CANDIDATE_HANDOFF_OUTPUT_DIR_INVALID")

    for filename in SOURCE_FILES:
        _repo_file(output / filename, root, f"QWEN_CANDIDATE_HANDOFF_SOURCE_INVALID:{filename}")

    attestation_path = output / "launch_to_output_attestation.json"
    attestation = verify_launch_to_output_attestation(attestation_path, repo_root=root)
    if attestation.get("genuine_canonical_inference_executed") is not True:
        raise ValueError("QWEN_CANDIDATE_HANDOFF_GENUINE_INFERENCE_MISSING")
    _assert_downstream_closed(attestation, "QWEN_CANDIDATE_HANDOFF_PREMATURE_AUTHORITY")
    inventory_evidence = _snapshot_inventory_evidence(attestation)

    candidate_binding = _binding(
        output / "canonical_candidate.png", root, "QWEN_CANDIDATE_HANDOFF_CANDIDATE_INVALID"
    )
    attested_candidate = attestation.get("canonical_candidate_png")
    if not isinstance(attested_candidate, Mapping):
        raise ValueError("QWEN_CANDIDATE_HANDOFF_ATTESTED_CANDIDATE_INVALID")
    for field in ("repository_relative_path", "sha256", "byte_size"):
        if attested_candidate.get(field) != candidate_binding.get(field):
            raise ValueError(f"QWEN_CANDIDATE_HANDOFF_ATTESTED_CANDIDATE_DRIFT:{field}")

    source_bindings = {
        filename: _binding(
            output / filename,
            root,
            f"QWEN_CANDIDATE_HANDOFF_SOURCE_INVALID:{filename}",
        )
        for filename in SOURCE_FILES
    }
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "story_snapshot_sha256": attestation.get("story_snapshot_sha256"),
        "model_id": attestation.get("model_id"),
        "model_revision": attestation.get("model_revision"),
        "cost_mode": "$0-local",
        "network_allowed": False,
        "local_files_only": True,
        "source_bindings": source_bindings,
        "canonical_candidate_png": {
            **candidate_binding,
            "width": attested_candidate.get("width"),
            "height": attested_candidate.get("height"),
        },
        "inference_settings": dict(attestation.get("inference_settings", {})),
        "snapshot_byte_inventory": inventory_evidence,
        "snapshot_byte_inventory_verified": True,
        "launch_to_output_binding_verified": True,
        "genuine_canonical_inference_executed": True,
        "handoff_sealed": True,
        "next_required_gates": [
            "factual_identity_sentiment_revalidation",
            "semantic_candidate_approval",
            "composition_and_generated_layer_qa",
            "visual_quality_adjudication",
            "human_visual_review",
            "exact_brand_typography",
            "semantic_publication_gate",
            "genuine_golden_materialization",
            "publication_readiness",
        ],
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
    }
    payload["handoff_sha256"] = sha256_json(payload)

    destination = handoff_path if handoff_path.is_absolute() else root / handoff_path
    if destination.is_symlink():
        raise ValueError("QWEN_CANDIDATE_HANDOFF_OUTPUT_INVALID")
    try:
        destination.parent.resolve().relative_to(root)
    except ValueError as exc:
        raise ValueError("QWEN_CANDIDATE_HANDOFF_OUTPUT_INVALID") from exc
    if destination.exists() or not destination.parent.is_dir():
        raise ValueError("QWEN_CANDIDATE_HANDOFF_OUTPUT_INVALID")

    raw = (json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n").encode()
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    return payload


def verify_canonical_candidate_handoff(path: Path, *, repo_root: Path) -> dict[str, Any]:
    """Replay the sealed handoff, including exact sources and CS357 inventory lineage."""
    root = repo_root.resolve()
    receipt, _ = _repo_file(path, root, "QWEN_CANDIDATE_HANDOFF_RECEIPT_INVALID")
    try:
        payload = json.loads(receipt.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("QWEN_CANDIDATE_HANDOFF_RECEIPT_INVALID") from exc
    if not isinstance(payload, dict) or payload.get("schema") != SCHEMA or payload.get("status") != STATUS:
        raise ValueError("QWEN_CANDIDATE_HANDOFF_SCHEMA_STATUS_DRIFT")

    claimed = payload.get("handoff_sha256")
    unsigned = dict(payload)
    unsigned.pop("handoff_sha256", None)
    if not _sha(claimed) or sha256_json(unsigned) != claimed:
        raise ValueError("QWEN_CANDIDATE_HANDOFF_DIGEST_MISMATCH")
    if payload.get("cost_mode") != "$0-local" or payload.get("network_allowed") is not False:
        raise ValueError("QWEN_CANDIDATE_HANDOFF_ZERO_COST_NETWORK_DRIFT")
    if payload.get("local_files_only") is not True:
        raise ValueError("QWEN_CANDIDATE_HANDOFF_LOCAL_ONLY_DRIFT")
    if payload.get("handoff_sealed") is not True or payload.get("genuine_canonical_inference_executed") is not True:
        raise ValueError("QWEN_CANDIDATE_HANDOFF_AUTHORITY_MISSING")
    if payload.get("snapshot_byte_inventory_verified") is not True:
        raise ValueError("QWEN_CANDIDATE_HANDOFF_SNAPSHOT_INVENTORY_AUTHORITY_MISSING")
    _assert_downstream_closed(payload, "QWEN_CANDIDATE_HANDOFF_DOWNSTREAM_AUTHORITY_DRIFT")

    bindings = payload.get("source_bindings")
    if not isinstance(bindings, Mapping) or set(bindings) != set(SOURCE_FILES):
        raise ValueError("QWEN_CANDIDATE_HANDOFF_BINDINGS_INVALID")
    resolved_sources: dict[str, Path] = {}
    for filename in SOURCE_FILES:
        binding = bindings.get(filename)
        if not isinstance(binding, Mapping) or not isinstance(binding.get("repository_relative_path"), str):
            raise ValueError(f"QWEN_CANDIDATE_HANDOFF_BINDING_INVALID:{filename}")
        source = root / binding["repository_relative_path"]
        current = _binding(source, root, f"QWEN_CANDIDATE_HANDOFF_SOURCE_INVALID:{filename}")
        if binding.get("sha256") != current["sha256"] or binding.get("byte_size") != current["byte_size"]:
            raise ValueError(f"QWEN_CANDIDATE_HANDOFF_BYTE_DRIFT:{filename}")
        resolved_sources[filename] = source

    attestation = verify_launch_to_output_attestation(
        resolved_sources["launch_to_output_attestation.json"], repo_root=root
    )
    _assert_downstream_closed(attestation, "QWEN_CANDIDATE_HANDOFF_UPSTREAM_AUTHORITY_DRIFT")
    for field in ("story_snapshot_sha256", "model_id", "model_revision", "inference_settings"):
        if payload.get(field) != attestation.get(field):
            raise ValueError(f"QWEN_CANDIDATE_HANDOFF_ATTESTATION_DRIFT:{field}")
    inventory_evidence = _snapshot_inventory_evidence(attestation)
    if payload.get("snapshot_byte_inventory") != inventory_evidence:
        raise ValueError("QWEN_CANDIDATE_HANDOFF_SNAPSHOT_INVENTORY_RECEIPT_DRIFT")

    candidate = payload.get("canonical_candidate_png")
    attested_candidate = attestation.get("canonical_candidate_png")
    if not isinstance(candidate, Mapping) or not isinstance(attested_candidate, Mapping):
        raise ValueError("QWEN_CANDIDATE_HANDOFF_CANDIDATE_BINDING_INVALID")
    for field in ("repository_relative_path", "sha256", "byte_size", "width", "height"):
        if candidate.get(field) != attested_candidate.get(field):
            raise ValueError(f"QWEN_CANDIDATE_HANDOFF_CANDIDATE_DRIFT:{field}")
    return payload
