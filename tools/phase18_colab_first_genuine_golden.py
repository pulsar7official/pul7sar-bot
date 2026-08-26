#!/usr/bin/env python3
"""Strict Candidate 1 entrypoint for the first genuine Golden Editorial v6 PNG.

This wrapper deliberately refuses the engineering-proof fallback. It delegates
actual generation and semantic inspection to phase18_colab_one_command.py with
--strict-semantic, then verifies that the exact generated PNG is the same
story-first Candidate 1 artifact recorded by both the Colab summary and the
semantic receipt.

Passing this wrapper does NOT mean Golden quality or publication approval. It
only proves that a genuine BF16/$0-local PNG exists, its durable generation
provenance replays against the pinned FLUX revision, and BASE_SCENE
semantic/layer QA completed on the same bytes using the approved pinned Qwen
semantic runtime identity. Human visual review, Golden 8.5/9.0+, exact brand,
typography and SemanticPublicationGate remain downstream and fail-closed.

The wrapper always requests --skip-update from the delegated one-command flow.
Its caller must therefore pin and reattach the exact Phase 18 source commit
before execution. This prevents a git pull from changing the source tree between
workflow admission and GPU generation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_MANIFEST_VERSION = "pul7sar-golden-batch-v6"
EXPECTED_BENCHMARK = "golden-visual-season-opener-editorial-v6"
EXPECTED_RECEIPT_STATUS = "GOLDEN_EDITORIAL_BASE_SEMANTICALLY_CLEAN"
EXPECTED_FOCAL_ANCHOR = "illuminated_tunnel_lower_left"
EXPECTED_COPY_NEGATIVE_SPACE = "right_center"
EXPECTED_BRAND_QUIET_ZONE = "upper_left"
EXPECTED_PROVENANCE_STATUS = "GENERATION_PROVENANCE_LOCK_VERIFIED"
EXPECTED_COST_MODE = "$0-local"
EXPECTED_DTYPE = "bfloat16"
EXPECTED_PRECISION_TIER = "golden_reference"
LATEST = ROOT / "output" / "phase18_colab" / "latest.json"
SEMANTIC_RECEIPT = ROOT / "output" / "phase18_visual_proof" / "editorial" / "candidate-01-golden-editorial-v6-receipt.json"
STAGING_RECEIPT = ROOT / "output" / "phase18_visual_proof" / "editorial" / "candidate-01-first-genuine-golden-staging.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.approved_model_revisions import (
    FLUX2_KLEIN_4B_MODEL_ID,
    FLUX2_KLEIN_4B_REVISION,
    QWEN25_VL_3B_MODEL_ID,
    QWEN25_VL_3B_REVISION,
)
from engine.intelligence.generation_provenance_lock import GenerationProvenanceLock
from engine.intelligence.qwen25_vl_inspector import VERIFIER_ID as QWEN25_VL_VERIFIER_ID

EXPECTED_QWEN_BASE_VERIFIER_ID = f"{QWEN25_VL_VERIFIER_ID}:base_scene"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdefABCDEF" for ch in value)


def _branch() -> str:
    completed = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise RuntimeError("unable to resolve current branch")
    return completed.stdout.strip()


def _inside_repo(path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise RuntimeError(f"EVIDENCE_PATH_OUTSIDE_REPOSITORY: {resolved}") from exc
    return resolved


def _load_json(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise RuntimeError(f"REQUIRED_EVIDENCE_MISSING: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"INVALID_EVIDENCE_PAYLOAD: {path}")
    return payload


def _resolve_png(value: object) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError("GOLDEN_PNG_PATH_MISSING")
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    path = _inside_repo(path)
    if not path.is_file():
        raise RuntimeError("GOLDEN_PNG_MISSING")
    if path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError("GOLDEN_PNG_SIGNATURE_INVALID")
    return path


def _require_golden_generation_identity(latest: dict[str, object]) -> None:
    if latest.get("model_id") != FLUX2_KLEIN_4B_MODEL_ID:
        raise RuntimeError("FIRST_GOLDEN_MODEL_ID_DRIFT")
    if latest.get("generation_provenance_status") != EXPECTED_PROVENANCE_STATUS:
        raise RuntimeError("FIRST_GOLDEN_PROVENANCE_STATUS_NOT_GOLDEN_REFERENCE")
    if latest.get("provenance_resolved_dtype") != EXPECTED_DTYPE:
        raise RuntimeError("FIRST_GOLDEN_MUST_USE_NATIVE_BFLOAT16")
    if latest.get("provenance_precision_quality_tier") != EXPECTED_PRECISION_TIER:
        raise RuntimeError("FIRST_GOLDEN_PRECISION_TIER_DRIFT")
    if latest.get("provenance_cost_mode") != EXPECTED_COST_MODE:
        raise RuntimeError("FIRST_GOLDEN_ZERO_COST_CONTRACT_DRIFT")
    if not isinstance(latest.get("request_id"), str) or not str(latest.get("request_id")).strip():
        raise RuntimeError("FIRST_GOLDEN_REQUEST_ID_MISSING")
    seed = latest.get("seed")
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise RuntimeError("FIRST_GOLDEN_SEED_INVALID")
    if not _is_sha256(latest.get("payload_sha256")):
        raise RuntimeError("FIRST_GOLDEN_PAYLOAD_SHA256_INVALID")


def _require_pinned_semantic_identity(semantic: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
    runtime = semantic.get("semantic_runtime")
    if not isinstance(runtime, dict):
        raise RuntimeError("SEMANTIC_RUNTIME_EVIDENCE_MISSING")
    if runtime.get("ready") is not True:
        raise RuntimeError("SEMANTIC_RUNTIME_NOT_READY")
    if runtime.get("model_id") != QWEN25_VL_3B_MODEL_ID:
        raise RuntimeError("SEMANTIC_MODEL_ID_DRIFT")
    if runtime.get("cuda_available") is not True:
        raise RuntimeError("SEMANTIC_RUNTIME_CUDA_NOT_PROVEN")

    inspection = semantic.get("semantic_visual_inspection")
    if not isinstance(inspection, dict) or inspection.get("approved") is not True:
        raise RuntimeError("BASE_SCENE_SEMANTIC_QA_NOT_APPROVED")
    if inspection.get("verifier_id") != EXPECTED_QWEN_BASE_VERIFIER_ID:
        raise RuntimeError("SEMANTIC_VERIFIER_ID_DRIFT")
    return runtime, inspection


def verify_genuine_candidate(*, latest_path: Path = LATEST, semantic_receipt_path: Path = SEMANTIC_RECEIPT) -> dict[str, object]:
    latest = _load_json(latest_path)
    semantic = _load_json(semantic_receipt_path)

    if latest.get("manifest_version") != EXPECTED_MANIFEST_VERSION:
        raise RuntimeError("GOLDEN_V6_MANIFEST_REQUIRED")
    if latest.get("benchmark") != EXPECTED_BENCHMARK:
        raise RuntimeError("GOLDEN_V6_BENCHMARK_REQUIRED")
    if latest.get("candidate") != 1:
        raise RuntimeError("FIRST_GOLDEN_MUST_USE_CANDIDATE_1")
    if latest.get("publication_ready") is True:
        raise RuntimeError("GENERATION_SUMMARY_CANNOT_AUTHORIZE_PUBLICATION")
    if latest.get("visual_grammar_surface_visibility") != "context_only":
        raise RuntimeError("GOLDEN_V6_PREVIEW_MUST_BE_CONTEXT_ONLY")
    if latest.get("hybrid_surface_replacement_required") is not False:
        raise RuntimeError("GOLDEN_V6_PREVIEW_MUST_NOT_REQUIRE_PITCH_REPLACEMENT")
    _require_golden_generation_identity(latest)

    for key, expected in (
        ("focal_anchor", EXPECTED_FOCAL_ANCHOR),
        ("copy_negative_space", EXPECTED_COPY_NEGATIVE_SPACE),
        ("brand_quiet_zone", EXPECTED_BRAND_QUIET_ZONE),
    ):
        if latest.get(key) != expected:
            raise RuntimeError(f"GOLDEN_V6_COMPOSITION_MAP_DRIFT: {key}")

    if semantic.get("status") != EXPECTED_RECEIPT_STATUS:
        raise RuntimeError("BASE_SCENE_SEMANTIC_RECEIPT_NOT_APPROVED")
    if semantic.get("candidate") != 1:
        raise RuntimeError("SEMANTIC_RECEIPT_CANDIDATE_DRIFT")
    if semantic.get("publication_ready") is True:
        raise RuntimeError("SEMANTIC_RECEIPT_CANNOT_AUTHORIZE_PUBLICATION")
    if semantic.get("deterministic_pitch_applied") is not False:
        raise RuntimeError("GOLDEN_V6_PREVIEW_PITCH_TEMPLATE_REGRESSED")
    if semantic.get("pitch_replacement_required") is not False:
        raise RuntimeError("GOLDEN_V6_PREVIEW_PITCH_REPLACEMENT_REGRESSED")

    semantic_runtime, semantic_visual = _require_pinned_semantic_identity(semantic)
    layer_gate = semantic.get("base_scene_layer_gate")
    if not isinstance(layer_gate, dict) or layer_gate.get("allowed") is not True or layer_gate.get("inspection_complete") is not True:
        raise RuntimeError("BASE_SCENE_LAYER_QA_NOT_APPROVED")

    latest_png = _resolve_png(latest.get("png"))
    semantic_png = _resolve_png(semantic.get("editorial_png"))
    if latest_png != semantic_png:
        raise RuntimeError("SEMANTIC_RECEIPT_PNG_PATH_DRIFT")

    png_sha = _sha256(latest_png)
    latest_sha = latest.get("base_png_sha256") or latest.get("png_sha256")
    if latest_sha is not None and latest_sha != png_sha:
        raise RuntimeError("GENERATION_SUMMARY_PNG_SHA256_MISMATCH")

    provenance = GenerationProvenanceLock().verify(
        repository_root=str(ROOT),
        summary=latest,
        base_png=str(latest_png),
    )
    if provenance.get("status") != EXPECTED_PROVENANCE_STATUS:
        raise RuntimeError("FIRST_GOLDEN_PROVENANCE_REPLAY_NOT_GOLDEN_REFERENCE")
    if provenance.get("model_id") != FLUX2_KLEIN_4B_MODEL_ID:
        raise RuntimeError("FIRST_GOLDEN_PROVENANCE_MODEL_DRIFT")
    if provenance.get("model_revision") != FLUX2_KLEIN_4B_REVISION:
        raise RuntimeError("FIRST_GOLDEN_PROVENANCE_MODEL_REVISION_DRIFT")
    if provenance.get("resolved_dtype") != EXPECTED_DTYPE:
        raise RuntimeError("FIRST_GOLDEN_PROVENANCE_DTYPE_DRIFT")
    if provenance.get("precision_quality_tier") != EXPECTED_PRECISION_TIER:
        raise RuntimeError("FIRST_GOLDEN_PROVENANCE_PRECISION_TIER_DRIFT")
    if provenance.get("cost_mode") != EXPECTED_COST_MODE:
        raise RuntimeError("FIRST_GOLDEN_PROVENANCE_COST_MODE_DRIFT")
    if provenance.get("base_png_sha256") != png_sha:
        raise RuntimeError("FIRST_GOLDEN_PROVENANCE_PNG_SHA256_DRIFT")
    if provenance.get("request_id") != latest.get("request_id") or provenance.get("seed") != latest.get("seed"):
        raise RuntimeError("FIRST_GOLDEN_PROVENANCE_REQUEST_IDENTITY_DRIFT")
    if provenance.get("payload_sha256") != latest.get("payload_sha256"):
        raise RuntimeError("FIRST_GOLDEN_PROVENANCE_PAYLOAD_SHA256_DRIFT")
    if provenance.get("publication_ready") is not False:
        raise RuntimeError("FIRST_GOLDEN_PROVENANCE_CANNOT_AUTHORIZE_PUBLICATION")

    semantic_receipt = _inside_repo(semantic_receipt_path)
    payload = {
        "schema": "pul7sar-first-genuine-golden-staging-v3",
        "status": "FIRST_GENUINE_GOLDEN_EDITORIAL_CANDIDATE_READY_FOR_HUMAN_REVIEW",
        "branch": EXPECTED_BRANCH,
        "candidate": 1,
        "manifest_version": EXPECTED_MANIFEST_VERSION,
        "benchmark": EXPECTED_BENCHMARK,
        "request_id": latest.get("request_id"),
        "seed": latest.get("seed"),
        "payload_sha256": latest.get("payload_sha256"),
        "model_id": FLUX2_KLEIN_4B_MODEL_ID,
        "model_revision": FLUX2_KLEIN_4B_REVISION,
        "cost_mode": EXPECTED_COST_MODE,
        "resolved_dtype": EXPECTED_DTYPE,
        "precision_quality_tier": EXPECTED_PRECISION_TIER,
        "generation_provenance_status": provenance.get("status"),
        "png": str(latest_png),
        "png_sha256": png_sha,
        "png_bytes": latest_png.stat().st_size,
        "executor_result": provenance.get("executor_result"),
        "executor_result_sha256": provenance.get("executor_result_sha256"),
        "proof_metadata": provenance.get("metadata"),
        "proof_metadata_sha256": provenance.get("metadata_sha256"),
        "semantic_receipt": str(semantic_receipt),
        "semantic_receipt_sha256": _sha256(semantic_receipt),
        "semantic_model_id": QWEN25_VL_3B_MODEL_ID,
        "semantic_model_revision": QWEN25_VL_3B_REVISION,
        "semantic_verifier_id": semantic_visual.get("verifier_id"),
        "semantic_runtime_ready": semantic_runtime.get("ready"),
        "semantic_cuda_available": semantic_runtime.get("cuda_available"),
        "semantic_approved": True,
        "layer_ownership_approved": True,
        "composition_map_locked": True,
        "deterministic_pitch_applied": False,
        "human_visual_review_required": True,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
        "next_gate": "human visual review, then Golden 8.5/9.0+ review; exact brand/typography and SemanticPublicationGate remain downstream",
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="PUL7SAR strict first genuine Golden Editorial v6 Candidate 1")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if _branch() != EXPECTED_BRANCH:
        raise RuntimeError(f"BRANCH_BLOCKED: expected {EXPECTED_BRANCH}")

    command = [
        sys.executable,
        str(ROOT / "tools" / "phase18_colab_one_command.py"),
        "--candidate", "1",
        "--semantic-inspection", "qwen",
        "--strict-semantic",
        "--skip-update",
    ]
    if args.force:
        command.append("--force")
    completed = subprocess.run(command, cwd=ROOT)
    if completed.returncode != 0:
        return completed.returncode

    payload = verify_genuine_candidate()
    STAGING_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    STAGING_RECEIPT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print("\n=== FIRST GENUINE GOLDEN EDITORIAL CANDIDATE STAGED ===")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
