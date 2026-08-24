#!/usr/bin/env python3
"""Fail-closed semantic-side GPU preflight for the first Golden Hybrid candidate.

This command deliberately runs *before* FLUX generation. It proves that the exact
Qwen/Pillow/Transformers runtime is qualified on CUDA, then proves/prefetches the
approved local Qwen2.5-VL snapshot. It never invokes FLUX, never mutates the
Phase 18 generation queue, never creates a PNG, and never authorizes publication.

The purpose is to avoid spending GPU time on a Golden base scene only to discover
later that the semantic publication inspector cannot run on the same host.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.qwen25_vl_inspector import MODEL_ID
from engine.intelligence.semantic_inspector_readiness import Qwen25VLReadinessProbe


EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_COST_MODE = "$0-local"


def _branch(repository_root: Path) -> str:
    completed = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repository_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError("SEMANTIC_PREFLIGHT_BRANCH_UNRESOLVED")
    return completed.stdout.strip()


def _run_prefetch(repository_root: Path, receipt_path: Path, minimum_free_gib: float) -> dict[str, object]:
    completed = subprocess.run(
        [
            sys.executable,
            str(repository_root / "tools" / "phase18_prefetch_qwen.py"),
            "--receipt",
            str(receipt_path),
            "--minimum-free-gib",
            str(minimum_free_gib),
        ],
        cwd=repository_root,
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        detail = (completed.stderr or completed.stdout)[-2000:]
        raise RuntimeError("QWEN_MODEL_PREFETCH_INVALID_JSON: " + detail) from exc
    if completed.returncode != 0:
        raise RuntimeError(
            "QWEN_MODEL_PREFETCH_FAILED: "
            + json.dumps(payload, ensure_ascii=False, sort_keys=True)
        )
    return payload


def _validate_prefetch_payload(payload: dict[str, object]) -> None:
    if payload.get("ready") is not True:
        raise RuntimeError("QWEN_MODEL_CACHE_NOT_READY")
    if payload.get("model_id") != MODEL_ID:
        raise RuntimeError("QWEN_MODEL_ID_DRIFT")
    if payload.get("cost_mode") != EXPECTED_COST_MODE:
        raise RuntimeError("QWEN_MODEL_PREFETCH_ESCAPED_ZERO_COST_POLICY")
    snapshot = payload.get("snapshot_path")
    if not isinstance(snapshot, str) or not snapshot.strip():
        raise RuntimeError("QWEN_MODEL_SNAPSHOT_PATH_MISSING")


def _build_receipt(
    *,
    readiness,
    prefetch: dict[str, object],
    branch: str,
    prefetch_receipt_path: Path,
) -> dict[str, object]:
    return {
        "schema": "pul7sar-phase18-semantic-gpu-preflight-v1",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "branch": branch,
        "model_id": MODEL_ID,
        "cost_mode": EXPECTED_COST_MODE,
        "semantic_runtime_ready": readiness.ready,
        "semantic_model_ready": prefetch.get("ready") is True,
        "cuda_available": readiness.cuda_available,
        "transformers_version": readiness.transformers_version,
        "torch_version": readiness.torch_version,
        "runtime_failures": list(readiness.failures),
        "model_snapshot_path": prefetch.get("snapshot_path"),
        "model_downloaded_now": bool(prefetch.get("downloaded_now")),
        "model_prefetch_receipt": str(prefetch_receipt_path),
        "generation_authorized": False,
        "queue_mutated": False,
        "png_created": False,
        "publication_ready": False,
        "next_gate": "FLUX/BF16 generation readiness and locked Candidate 1 execution",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight the local Qwen semantic runtime before Golden GPU generation")
    parser.add_argument("--repository-root", default=str(ROOT))
    parser.add_argument("--minimum-free-gib", type=float, default=12.0)
    parser.add_argument("--qwen-cache-receipt", default="output/phase18_gpu_smoke/qwen-model-cache.json")
    parser.add_argument("--output", default="output/phase18_gpu_smoke/semantic-preflight.json")
    args = parser.parse_args()

    if args.minimum_free_gib <= 0:
        raise ValueError("minimum-free-gib must be positive")

    repository_root = Path(args.repository_root).resolve()
    if not (repository_root / "engine" / "intelligence").is_dir():
        raise RuntimeError("repository-root does not contain the Phase 18 intelligence engine")

    branch = _branch(repository_root)
    if branch != EXPECTED_BRANCH:
        raise RuntimeError(f"SEMANTIC_PREFLIGHT_BRANCH_BLOCKED: expected {EXPECTED_BRANCH}, found {branch}")

    # Runtime readiness must pass *before* a potentially large Qwen model download.
    readiness = Qwen25VLReadinessProbe().inspect()
    if not readiness.ready:
        raise RuntimeError(
            "SEMANTIC_RUNTIME_NOT_READY_BEFORE_FLUX: " + "; ".join(readiness.failures)
        )

    cache_receipt = Path(args.qwen_cache_receipt)
    if not cache_receipt.is_absolute():
        cache_receipt = repository_root / cache_receipt
    prefetch = _run_prefetch(repository_root, cache_receipt, args.minimum_free_gib)
    _validate_prefetch_payload(prefetch)

    receipt = _build_receipt(
        readiness=readiness,
        prefetch=prefetch,
        branch=branch,
        prefetch_receipt_path=cache_receipt,
    )

    output = Path(args.output)
    if not output.is_absolute():
        output = repository_root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
