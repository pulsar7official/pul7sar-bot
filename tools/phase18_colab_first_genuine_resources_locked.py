#!/usr/bin/env python3
"""Resource/runtime-lock and stage the first genuine Golden Editorial v6 Candidate 1.

This wrapper is the preferred execution seam for an immutable self-hosted GPU
checkout. It proves live GPU qualification and live host-memory readiness,
proves the exact pinned Qwen semantic runtime/snapshot before Candidate 1,
captures the approved software/runtime fingerprint immediately before the
strict genuine-Golden entrypoint, then captures it again after staging and
fails closed on any drift. Resource, semantic, runtime and staging receipts are
all bound by SHA-256.

It never authorizes human acceptance, Golden quality, publication, or Seeds 2-4.
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
GPU_HOST = ROOT / "output" / "phase18_gpu_host" / "qualification.json"
HOST_MEMORY = ROOT / "output" / "phase18_gpu_smoke" / "host-memory-preflight.json"
SEMANTIC_PREFLIGHT = ROOT / "output" / "phase18_gpu_smoke" / "semantic-preflight.json"
QWEN_MODEL_CACHE = ROOT / "output" / "phase18_gpu_smoke" / "qwen-model-cache.json"
RUNTIME_PRE = ROOT / "output" / "phase18_gpu_smoke" / "first-genuine-golden-runtime-pre.json"
RUNTIME_POST = ROOT / "output" / "phase18_gpu_smoke" / "first-genuine-golden-runtime-post.json"
STAGING = ROOT / "output" / "phase18_visual_proof" / "editorial" / "candidate-01-first-genuine-golden-staging.json"
FINAL = ROOT / "output" / "phase18_gpu_smoke" / "first-genuine-golden-v6-resource-lock.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.approved_model_revisions import (
    QWEN25_VL_3B_MODEL_ID,
    QWEN25_VL_3B_REVISION,
    assert_snapshot_revision,
)
from engine.intelligence.generation_runtime_fingerprint import (
    capture_generation_runtime_fingerprint,
    verify_matching_runtime_fingerprints,
)


def _branch() -> str:
    completed = subprocess.run(["git", "branch", "--show-current"], cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_RESOURCE_LOCK_BRANCH_RESOLUTION_FAILED")
    return completed.stdout.strip()


def _inside_repo(path: Path) -> Path:
    target = path if path.is_absolute() else ROOT / path
    target = target.resolve()
    root = ROOT.resolve()
    if target != root and root not in target.parents:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_RESOURCE_LOCK_PATH_ESCAPES_REPOSITORY")
    return target


def _load(path: Path) -> dict[str, object]:
    target = _inside_repo(path)
    if not target.is_file():
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_RESOURCE_EVIDENCE_MISSING:{target}")
    payload = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_RESOURCE_EVIDENCE_INVALID")
    return payload


def _write(path: Path, payload: dict[str, object]) -> None:
    target = _inside_repo(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _record(path: Path) -> dict[str, object]:
    target = _inside_repo(path)
    if not target.is_file():
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_RESOURCE_EVIDENCE_MISSING:{target}")
    data = target.read_bytes()
    return {"path": str(target), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def _run(command: list[str], *, label: str) -> None:
    completed = subprocess.run(command, cwd=ROOT, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"{label}_FAILED:{completed.returncode}")


def _validate_semantic_preflight(semantic: dict[str, object], qwen_cache: dict[str, object]) -> None:
    if semantic.get("schema") != "pul7sar-phase18-semantic-gpu-preflight-v2":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_SEMANTIC_PREFLIGHT_SCHEMA_DRIFT")
    if semantic.get("branch") != EXPECTED_BRANCH:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_SEMANTIC_PREFLIGHT_BRANCH_DRIFT")
    if semantic.get("model_id") != QWEN25_VL_3B_MODEL_ID or semantic.get("model_revision") != QWEN25_VL_3B_REVISION:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_SEMANTIC_MODEL_IDENTITY_DRIFT")
    if semantic.get("resolved_snapshot_revision") != QWEN25_VL_3B_REVISION or semantic.get("revision_pinned") is not True:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_SEMANTIC_SNAPSHOT_REVISION_UNPROVEN")
    if semantic.get("semantic_runtime_ready") is not True or semantic.get("semantic_model_ready") is not True:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_SEMANTIC_RUNTIME_NOT_READY")
    if semantic.get("cuda_available") is not True or semantic.get("cost_mode") != "$0-local":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_SEMANTIC_RUNTIME_POLICY_DRIFT")
    for field in ("generation_authorized", "queue_mutated", "png_created", "publication_ready"):
        if semantic.get(field) is not False:
            raise RuntimeError(f"FIRST_GENUINE_GOLDEN_SEMANTIC_AUTHORITY_DRIFT:{field}")

    if qwen_cache.get("schema") != "pul7sar-phase18-qwen-model-cache-v2":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_QWEN_CACHE_SCHEMA_DRIFT")
    if qwen_cache.get("ready") is not True:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_QWEN_CACHE_NOT_READY")
    if qwen_cache.get("model_id") != QWEN25_VL_3B_MODEL_ID or qwen_cache.get("model_revision") != QWEN25_VL_3B_REVISION:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_QWEN_CACHE_MODEL_DRIFT")
    if qwen_cache.get("resolved_snapshot_revision") != QWEN25_VL_3B_REVISION or qwen_cache.get("revision_pinned") is not True:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_QWEN_CACHE_REVISION_UNPROVEN")
    if qwen_cache.get("cost_mode") != "$0-local":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_QWEN_CACHE_COST_MODE_DRIFT")
    snapshot = qwen_cache.get("snapshot_path")
    if not isinstance(snapshot, str) or not snapshot.strip():
        raise RuntimeError("FIRST_GENUINE_GOLDEN_QWEN_CACHE_SNAPSHOT_MISSING")
    try:
        assert_snapshot_revision(snapshot, QWEN25_VL_3B_REVISION)
    except (RuntimeError, ValueError) as exc:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_QWEN_CACHE_SNAPSHOT_PATH_DRIFT") from exc

    semantic_cache_receipt = semantic.get("model_prefetch_receipt")
    if not isinstance(semantic_cache_receipt, str) or _inside_repo(Path(semantic_cache_receipt)) != _inside_repo(QWEN_MODEL_CACHE):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_SEMANTIC_CACHE_RECEIPT_PATH_DRIFT")
    if semantic.get("model_snapshot_path") != snapshot:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_SEMANTIC_CACHE_SNAPSHOT_DRIFT")


def run(*, force: bool = False, output: Path = FINAL) -> dict[str, object]:
    if _branch() != EXPECTED_BRANCH:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_RESOURCE_LOCK_BRANCH_BLOCKED")

    _run(
        [sys.executable, str(ROOT / "tools" / "phase18_qualify_gpu_host.py"), "--output", str(GPU_HOST)],
        label="FIRST_GENUINE_GOLDEN_GPU_QUALIFICATION",
    )
    gpu = _load(GPU_HOST)
    if gpu.get("eligible") is not True or gpu.get("cuda_available") is not True or gpu.get("bf16_supported") is not True:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_GPU_NOT_QUALIFIED")
    if gpu.get("cost_mode") != "$0-local":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_GPU_COST_MODE_DRIFT")
    free_vram = gpu.get("gpu_free_vram_gb")
    required_vram = gpu.get("required_vram_gb")
    if not isinstance(free_vram, (int, float)) or isinstance(free_vram, bool):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_LIVE_FREE_VRAM_NOT_PROVEN")
    if not isinstance(required_vram, (int, float)) or isinstance(required_vram, bool) or float(free_vram) < float(required_vram):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_LIVE_FREE_VRAM_BELOW_FLOOR")

    _run(
        [sys.executable, str(ROOT / "tools" / "phase18_preflight_host_memory.py"), "--output", str(HOST_MEMORY)],
        label="FIRST_GENUINE_GOLDEN_HOST_MEMORY_PREFLIGHT",
    )
    memory = _load(HOST_MEMORY)
    if memory.get("ready") is not True or memory.get("cost_mode") != "$0-local":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_HOST_MEMORY_NOT_READY")

    # Semantic model qualification is part of the same resource lock, after the
    # host has proved it is worth preparing model bytes and before FLUX begins.
    _run(
        [
            sys.executable,
            str(ROOT / "tools" / "phase18_preflight_semantic_gpu.py"),
            "--output",
            str(SEMANTIC_PREFLIGHT),
            "--qwen-cache-receipt",
            str(QWEN_MODEL_CACHE),
        ],
        label="FIRST_GENUINE_GOLDEN_SEMANTIC_PREFLIGHT",
    )
    semantic = _load(SEMANTIC_PREFLIGHT)
    qwen_cache = _load(QWEN_MODEL_CACHE)
    _validate_semantic_preflight(semantic, qwen_cache)

    # Freeze the software/runtime identity immediately before Candidate 1.
    runtime_before = capture_generation_runtime_fingerprint()
    _write(RUNTIME_PRE, runtime_before)

    command = [sys.executable, str(ROOT / "tools" / "phase18_colab_first_genuine_golden.py")]
    if force:
        command.append("--force")
    _run(command, label="FIRST_GENUINE_GOLDEN_STRICT_STAGING")

    # Candidate 1 is not accepted if the executing software stack changed while
    # generation + BASE_SCENE inspection were running.
    runtime_after = capture_generation_runtime_fingerprint()
    _write(RUNTIME_POST, runtime_after)
    runtime_fingerprint_sha = verify_matching_runtime_fingerprints(runtime_before, runtime_after)

    staging = _load(STAGING)
    if staging.get("schema") != "pul7sar-first-genuine-golden-staging-v3":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_STAGING_SCHEMA_DRIFT")
    if staging.get("status") != "FIRST_GENUINE_GOLDEN_EDITORIAL_CANDIDATE_READY_FOR_HUMAN_REVIEW":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_STAGING_NOT_READY")
    if staging.get("candidate") != 1 or staging.get("cost_mode") != "$0-local":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_STAGING_IDENTITY_DRIFT")
    if staging.get("resolved_dtype") != "bfloat16" or staging.get("precision_quality_tier") != "golden_reference":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_STAGING_PRECISION_DRIFT")
    if staging.get("semantic_model_id") != QWEN25_VL_3B_MODEL_ID or staging.get("semantic_model_revision") != QWEN25_VL_3B_REVISION:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_STAGING_SEMANTIC_IDENTITY_DRIFT")
    if staging.get("semantic_approved") is not True or staging.get("layer_ownership_approved") is not True:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_STAGING_SEMANTIC_GATE_NOT_APPROVED")
    for field in ("golden_quality_approved", "publication_ready", "seeds_2_to_4_authorized"):
        if staging.get(field) is not False:
            raise RuntimeError(f"FIRST_GENUINE_GOLDEN_STAGING_AUTHORITY_DRIFT:{field}")

    png_value = staging.get("png")
    if not isinstance(png_value, str) or not png_value.strip():
        raise RuntimeError("FIRST_GENUINE_GOLDEN_STAGING_PNG_MISSING")
    png = _inside_repo(Path(png_value))
    if not png.is_file() or png.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_STAGING_PNG_INVALID")
    png_sha = hashlib.sha256(png.read_bytes()).hexdigest()
    if staging.get("png_sha256") != png_sha:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_STAGING_PNG_SHA_DRIFT")

    evidence = {
        "gpu_host_qualification": _record(GPU_HOST),
        "host_memory_preflight": _record(HOST_MEMORY),
        "semantic_preflight": _record(SEMANTIC_PREFLIGHT),
        "qwen_model_cache": _record(QWEN_MODEL_CACHE),
        "runtime_fingerprint_pre": _record(RUNTIME_PRE),
        "runtime_fingerprint_post": _record(RUNTIME_POST),
        "strict_golden_staging": _record(STAGING),
    }
    payload: dict[str, object] = {
        "schema": "pul7sar-first-genuine-golden-v6-resource-lock-v3",
        "status": "FIRST_GENUINE_GOLDEN_V6_RESOURCE_RUNTIME_SEMANTIC_LOCK_VERIFIED",
        "branch": EXPECTED_BRANCH,
        "candidate": 1,
        "cost_mode": "$0-local",
        "gpu_eligible": True,
        "native_bf16_proven": True,
        "live_free_vram_gb": free_vram,
        "required_vram_gb": required_vram,
        "host_memory_ready": True,
        "semantic_preflight_bound": True,
        "semantic_model_id": QWEN25_VL_3B_MODEL_ID,
        "semantic_model_revision": QWEN25_VL_3B_REVISION,
        "runtime_fingerprint_sha256": runtime_fingerprint_sha,
        "runtime_stable_across_generation": True,
        "staging_receipt": str(STAGING),
        "png": str(png),
        "png_sha256": png_sha,
        "png_bytes": png.stat().st_size,
        "evidence": evidence,
        "human_visual_review_required": True,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
        "next_gate": "human Golden visual review at 8.5 minimum / 9.0+ elite target; exact brand/typography and SemanticPublicationGate remain downstream",
    }
    target = _inside_repo(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Resource/runtime/semantic-lock the strict first genuine Golden Editorial v6 Candidate 1")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--output", type=Path, default=FINAL)
    args = parser.parse_args()
    payload = run(force=args.force, output=args.output)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
