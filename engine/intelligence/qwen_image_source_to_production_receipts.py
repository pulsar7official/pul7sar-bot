"""Atomically replay source bindings, compile six evidences, and execute production gates.

Change Set 256 removes the manual gap between Change Set 255 source-byte replay and
Change Set 252 production receipt execution. The runner stages all outputs in a private
directory, executes the six canonical production verifiers over the newly compiled
same-story evidence, writes byte-bound receipts, and publishes the output directory only
if every gate succeeds. A failure removes the staging directory and publishes nothing.

This module is CPU-only. It does not perform Change Set 237 freshness admission,
Change Set 238 independent semantic replay, generation authorization, model loading,
image inference, visual approval, Golden scoring, human review, or publication.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any, Mapping

from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    REQUIRED_FRESH_GATE_EVIDENCE,
)
from engine.intelligence.qwen_image_production_gate_receipt_executor import (
    build_production_gate_receipt_set,
)
from engine.intelligence.qwen_image_retrieved_source_binding_replay import (
    compile_replayed_source_binding_to_evidence_pack,
)


SOURCE_TO_PRODUCTION_RECEIPTS_SCHEMA = "pul7sar-phase18-source-to-production-receipts-v1"
_RECEIPT_FILENAMES = {
    gate_id: f"{index:02d}_{gate_id}_receipt.json"
    for index, gate_id in enumerate(REQUIRED_FRESH_GATE_EVIDENCE, start=1)
}
_FORBIDDEN_TRUE_AUTHORITY = (
    "production_semantic_replay_executed",
    "fresh_story_gates_passed",
    "controlled_trial_preflight_valid",
    "canonical_generation_authorized",
    "model_weights_loaded",
    "inference_executed",
    "genuine_golden_png_created",
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "publication_ready",
)


@dataclass(frozen=True)
class SourceToProductionReceiptsRun:
    output_dir: Path
    story_snapshot_sha256: str
    evidence_dir: Path
    receipt_dir: Path
    run_receipt_path: Path
    production_gate_receipt_paths: Mapping[str, Path]


def _write_json(path: Path, payload: Mapping[str, Any]) -> bytes:
    raw = (json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    path.write_bytes(raw)
    return raw


def _sha256_file(path: Path, code: str) -> tuple[str, int]:
    if not path.is_file():
        raise ValueError(code)
    raw = path.read_bytes()
    if not raw:
        raise ValueError(code)
    return hashlib.sha256(raw).hexdigest(), len(raw)


def _validate_target(output_dir: Path) -> None:
    if not isinstance(output_dir, Path):
        raise ValueError("QWEN_SOURCE_TO_RECEIPTS_OUTPUT_DIR_INVALID")
    if output_dir.exists():
        raise ValueError("QWEN_SOURCE_TO_RECEIPTS_OUTPUT_ALREADY_EXISTS")
    parent = output_dir.parent
    if not parent.is_dir():
        raise ValueError("QWEN_SOURCE_TO_RECEIPTS_OUTPUT_PARENT_INVALID")


def run_source_to_production_receipts(
    binding_receipt_path: Path,
    bound_manifest_path: Path,
    source_root: Path,
    output_dir: Path,
    *,
    evaluated_at_utc: str,
) -> SourceToProductionReceiptsRun:
    """Publish a six-receipt run only after source replay and all production gates pass."""
    _validate_target(output_dir)
    staging = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.stage-", dir=str(output_dir.parent)))
    published = False
    try:
        evidence_dir = staging / "evidence"
        pack = compile_replayed_source_binding_to_evidence_pack(
            binding_receipt_path,
            bound_manifest_path,
            source_root,
            evidence_dir,
        )

        receipts = build_production_gate_receipt_set(
            pack.evidence_paths,
            pack.story_snapshot_sha256,
            evaluated_at_utc=evaluated_at_utc,
        )
        if len(receipts) != len(REQUIRED_FRESH_GATE_EVIDENCE):
            raise RuntimeError("QWEN_SOURCE_TO_RECEIPTS_INTERNAL_RECEIPT_COUNT_DRIFT")

        receipt_dir = staging / "production_gate_receipts"
        receipt_dir.mkdir()
        receipt_paths: dict[str, Path] = {}
        receipt_bindings: list[dict[str, Any]] = []
        for expected_gate_id, receipt in zip(REQUIRED_FRESH_GATE_EVIDENCE, receipts):
            if not isinstance(receipt, Mapping) or receipt.get("gate_id") != expected_gate_id:
                raise RuntimeError("QWEN_SOURCE_TO_RECEIPTS_INTERNAL_RECEIPT_GATE_DRIFT")
            path = receipt_dir / _RECEIPT_FILENAMES[expected_gate_id]
            raw = _write_json(path, receipt)
            receipt_paths[expected_gate_id] = path
            receipt_bindings.append(
                {
                    "gate_id": expected_gate_id,
                    "path": f"production_gate_receipts/{path.name}",
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "byte_size": len(raw),
                }
            )

        binding_sha, binding_size = _sha256_file(
            binding_receipt_path, "QWEN_SOURCE_TO_RECEIPTS_BINDING_RECEIPT_INVALID"
        )
        manifest_sha, manifest_size = _sha256_file(
            bound_manifest_path, "QWEN_SOURCE_TO_RECEIPTS_BOUND_MANIFEST_INVALID"
        )
        pack_sha, pack_size = _sha256_file(
            pack.pack_receipt_path, "QWEN_SOURCE_TO_RECEIPTS_EVIDENCE_PACK_RECEIPT_INVALID"
        )
        run_receipt = {
            "schema": SOURCE_TO_PRODUCTION_RECEIPTS_SCHEMA,
            "story_snapshot_sha256": pack.story_snapshot_sha256,
            "binding_receipt": {
                "sha256": binding_sha,
                "byte_size": binding_size,
            },
            "bound_manifest": {
                "sha256": manifest_sha,
                "byte_size": manifest_size,
            },
            "evidence_pack_receipt": {
                "path": "evidence/evidence_pack_receipt.json",
                "sha256": pack_sha,
                "byte_size": pack_size,
            },
            "production_gate_receipts": receipt_bindings,
            "production_gate_execution_completed": True,
            "production_semantic_replay_executed": False,
            "fresh_story_gates_passed": False,
            "controlled_trial_preflight_valid": False,
            "canonical_generation_authorized": False,
            "model_weights_loaded": False,
            "inference_executed": False,
            "genuine_golden_png_created": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        for key in _FORBIDDEN_TRUE_AUTHORITY:
            if run_receipt[key] is not False:
                raise RuntimeError("QWEN_SOURCE_TO_RECEIPTS_INTERNAL_AUTHORITY_DRIFT")
        _write_json(staging / "source_to_production_receipts.json", run_receipt)

        os.replace(staging, output_dir)
        published = True
        final_receipt_dir = output_dir / "production_gate_receipts"
        return SourceToProductionReceiptsRun(
            output_dir=output_dir,
            story_snapshot_sha256=pack.story_snapshot_sha256,
            evidence_dir=output_dir / "evidence",
            receipt_dir=final_receipt_dir,
            run_receipt_path=output_dir / "source_to_production_receipts.json",
            production_gate_receipt_paths={
                gate_id: final_receipt_dir / _RECEIPT_FILENAMES[gate_id]
                for gate_id in REQUIRED_FRESH_GATE_EVIDENCE
            },
        )
    finally:
        if not published and staging.exists():
            shutil.rmtree(staging)
