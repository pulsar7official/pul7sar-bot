#!/usr/bin/env python3
"""Fresh-Colab bootstrap for the first genuine Golden Hybrid v5 review packet.

This is the preferred entrypoint when the next CUDA/BF16 Colab session starts
from a fresh runtime. It deliberately has no engineering-proof fallback: the
first Golden Candidate must have the exact Qwen semantic runtime/model ready
before FLUX spends GPU time, then it delegates to the SHA-sealed Candidate 1
review path.

The command never authorizes Seeds 2-4, never fills the human review decision,
and never grants Golden or publication authority.
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
GPU_SMOKE = ROOT / "output" / "phase18_gpu_smoke"
REPOSITORY_INTEGRITY = GPU_SMOKE / "repository-integrity.json"
CACHE_BUDGET = GPU_SMOKE / "first-golden-cache-budget.json"
QWEN_MODEL_CACHE = GPU_SMOKE / "qwen-model-cache.json"
SEALED_REVIEW = GPU_SMOKE / "first-golden-human-review-sealed.json"
FINAL = GPU_SMOKE / "first-golden-colab-bootstrap.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.phase18_colab_bootstrap as runtime_bootstrap


def _branch() -> str:
    completed = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError("FIRST_GOLDEN_BOOTSTRAP_BRANCH_RESOLUTION_FAILED")
    return completed.stdout.strip()


def _inside_root(path: Path) -> Path:
    resolved = path if path.is_absolute() else ROOT / path
    resolved = resolved.resolve()
    root = ROOT.resolve()
    if resolved != root and root not in resolved.parents:
        raise RuntimeError("FIRST_GOLDEN_BOOTSTRAP_OUTPUT_ESCAPES_REPOSITORY")
    return resolved


def _run_json(command: list[str], *, label: str) -> dict[str, object]:
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout)[-4000:]
        raise RuntimeError(f"{label} failed: {detail}")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{label} did not emit valid JSON") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"{label} emitted non-object JSON")
    return payload


def _load_json_file(path: Path, *, label: str) -> dict[str, object]:
    target = _inside_root(path)
    if not target.is_file():
        raise RuntimeError(f"FIRST_GOLDEN_BOOTSTRAP_{label}_MISSING")
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"FIRST_GOLDEN_BOOTSTRAP_{label}_INVALID_JSON") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"FIRST_GOLDEN_BOOTSTRAP_{label}_NOT_OBJECT")
    return payload


def _evidence_record(path: Path, *, label: str) -> dict[str, object]:
    target = _inside_root(path)
    if not target.is_file():
        raise RuntimeError(f"FIRST_GOLDEN_BOOTSTRAP_{label}_EVIDENCE_MISSING")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    return {"path": str(target), "sha256": digest, "bytes": target.stat().st_size}


def run(
    *,
    worker_id: str,
    timeout_seconds: int,
    skip_repair: bool = False,
    final_path: Path = FINAL,
) -> dict[str, object]:
    if _branch() != EXPECTED_BRANCH:
        raise RuntimeError("FIRST_GOLDEN_BOOTSTRAP_BRANCH_BLOCKED")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")

    # Repository/reference integrity is CPU-only and must pass before dependency
    # repair, model downloads, CUDA qualification or any queue mutation.
    repository = _run_json(
        [
            sys.executable,
            str(ROOT / "tools" / "phase18_preflight_repository_integrity.py"),
            "--output",
            str(REPOSITORY_INTEGRITY),
        ],
        label="FIRST_GOLDEN_REPOSITORY_INTEGRITY",
    )
    if repository.get("schema") != "pul7sar-phase18-pre-gpu-repository-integrity-v1" or repository.get("ready") is not True:
        raise RuntimeError("FIRST_GOLDEN_BOOTSTRAP_REPOSITORY_INTEGRITY_BLOCKED")
    if repository.get("branch") != EXPECTED_BRANCH or repository.get("cost_mode") != "$0-local":
        raise RuntimeError("FIRST_GOLDEN_BOOTSTRAP_REPOSITORY_IDENTITY_DRIFT")
    for field in ("generation_authorized", "queue_mutated", "png_created", "publication_ready"):
        if repository.get(field) is not False:
            raise RuntimeError(f"FIRST_GOLDEN_BOOTSTRAP_REPOSITORY_{field.upper()}_DRIFT")

    # Fresh runtime repair is reused from the already-tested Colab bootstrap.
    # Once huggingface_hub is available, prove combined Qwen+FLUX cache headroom
    # before either approved model is allowed to download.
    if not skip_repair:
        runtime_bootstrap._repair_runtime()
    cache_budget = _run_json(
        [
            sys.executable,
            str(ROOT / "tools" / "phase18_preflight_first_golden_cache_budget.py"),
            "--receipt",
            str(CACHE_BUDGET),
        ],
        label="FIRST_GOLDEN_CACHE_BUDGET",
    )
    if cache_budget.get("schema") != "pul7sar-first-golden-cache-budget-v1" or cache_budget.get("ready") is not True:
        raise RuntimeError("FIRST_GOLDEN_BOOTSTRAP_CACHE_BUDGET_BLOCKED")
    if cache_budget.get("branch") != EXPECTED_BRANCH or cache_budget.get("cost_mode") != "$0-local":
        raise RuntimeError("FIRST_GOLDEN_BOOTSTRAP_CACHE_BUDGET_IDENTITY_DRIFT")
    if cache_budget.get("downloads_performed") is not False:
        raise RuntimeError("FIRST_GOLDEN_BOOTSTRAP_CACHE_BUDGET_DOWNLOAD_DRIFT")
    for field in ("generation_authorized", "queue_mutated", "png_created", "publication_ready"):
        if cache_budget.get(field) is not False:
            raise RuntimeError(f"FIRST_GOLDEN_BOOTSTRAP_CACHE_BUDGET_{field.upper()}_DRIFT")

    # The Golden path is strict: semantic degradation is fatal, not a request to
    # fall back to the engineering-proof route.
    if not runtime_bootstrap._fresh_process_probe():
        raise RuntimeError("FIRST_GOLDEN_BOOTSTRAP_SEMANTIC_RUNTIME_NOT_READY")
    if not runtime_bootstrap._prefetch_semantic_model():
        raise RuntimeError("FIRST_GOLDEN_BOOTSTRAP_QWEN_MODEL_NOT_READY")

    qwen_cache = _load_json_file(QWEN_MODEL_CACHE, label="QWEN_MODEL_CACHE")
    if qwen_cache.get("schema") != "pul7sar-phase18-qwen-model-cache-v1" or qwen_cache.get("ready") is not True:
        raise RuntimeError("FIRST_GOLDEN_BOOTSTRAP_QWEN_MODEL_CACHE_CONTRACT_MISMATCH")
    if qwen_cache.get("model_id") != "Qwen/Qwen2.5-VL-3B-Instruct" or qwen_cache.get("cost_mode") != "$0-local":
        raise RuntimeError("FIRST_GOLDEN_BOOTSTRAP_QWEN_MODEL_CACHE_IDENTITY_DRIFT")

    staged = _run_json(
        [
            sys.executable,
            str(ROOT / "tools" / "phase18_colab_first_golden_review_sealed.py"),
            "--worker-id",
            worker_id,
            "--timeout-seconds",
            str(timeout_seconds),
        ],
        label="FIRST_GOLDEN_SEALED_REVIEW_STAGING",
    )
    if staged.get("status") != "FIRST_GOLDEN_CANDIDATE_READY_FOR_VERIFIED_HUMAN_REVIEW":
        raise RuntimeError("FIRST_GOLDEN_BOOTSTRAP_REVIEW_NOT_READY")
    if staged.get("candidate") != 1 or staged.get("cost_mode") != "$0-local":
        raise RuntimeError("FIRST_GOLDEN_BOOTSTRAP_REVIEW_IDENTITY_DRIFT")
    for field in ("human_visual_review_approved", "golden_quality_approved", "publication_ready", "seeds_2_to_4_authorized"):
        if staged.get(field) is not False:
            raise RuntimeError(f"FIRST_GOLDEN_BOOTSTRAP_{field.upper()}_AUTHORITY_DRIFT")

    evidence = {
        "repository_integrity": _evidence_record(REPOSITORY_INTEGRITY, label="REPOSITORY_INTEGRITY"),
        "first_golden_cache_budget": _evidence_record(CACHE_BUDGET, label="CACHE_BUDGET"),
        "qwen_model_cache": _evidence_record(QWEN_MODEL_CACHE, label="QWEN_MODEL_CACHE"),
        "sealed_review_receipt": _evidence_record(SEALED_REVIEW, label="SEALED_REVIEW"),
    }

    payload: dict[str, object] = {
        "schema": "pul7sar-first-golden-colab-bootstrap-v2",
        "status": "FIRST_GOLDEN_COLAB_REVIEW_PACKET_READY",
        "branch": EXPECTED_BRANCH,
        "candidate": 1,
        "cost_mode": "$0-local",
        "repository_integrity": str(REPOSITORY_INTEGRITY),
        "first_golden_cache_budget": str(CACHE_BUDGET),
        "qwen_model_cache": str(QWEN_MODEL_CACHE),
        "semantic_runtime_ready": True,
        "semantic_model_ready": True,
        "sealed_review_receipt": str(SEALED_REVIEW),
        "bootstrap_evidence": evidence,
        "review_base_png": staged["review_base_png"],
        "review_hybrid_png": staged["review_hybrid_png"],
        "review_base_png_sha256": staged["review_base_png_sha256"],
        "review_hybrid_png_sha256": staged["review_hybrid_png_sha256"],
        "human_visual_review_required": True,
        "automatic_selection_performed": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
        "next_gate": "explicit human review of the sealed Candidate 1 base and Hybrid PNGs",
    }
    target = _inside_root(final_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Repair a fresh Colab runtime and stage Candidate 1 through the sealed Golden human-review packet"
    )
    parser.add_argument("--worker-id", default="colab-first-golden-bootstrap-01")
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--skip-repair", action="store_true", help="Only for a runtime already repaired by the verified bootstrap")
    parser.add_argument("--output", type=Path, default=FINAL)
    args = parser.parse_args()
    payload = run(
        worker_id=args.worker_id,
        timeout_seconds=args.timeout_seconds,
        skip_repair=args.skip_repair,
        final_path=args.output,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
