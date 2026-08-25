#!/usr/bin/env python3
"""Prove combined Qwen + FLUX cache headroom before either model download.

This command is intentionally download-free. It only checks whether the exact
approved Qwen and FLUX snapshots are already present in the local Hugging Face
cache and, for every missing snapshot, reserves the conservative free-space
budget used by the existing individual prefetch tools.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.first_golden_cache_budget import FirstGoldenCacheBudgetPolicy
from engine.intelligence.qwen25_vl_inspector import MODEL_ID as QWEN_MODEL_ID
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


def _branch() -> str:
    completed = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError("FIRST_GOLDEN_CACHE_BUDGET_BRANCH_RESOLUTION_FAILED")
    return completed.stdout.strip()


def _cache_root() -> Path:
    hf_home = os.environ.get("HF_HOME")
    if hf_home:
        return Path(hf_home).expanduser().resolve()
    return (Path.home() / ".cache" / "huggingface").resolve()


def _cached_snapshot(snapshot_download, model_id: str) -> str | None:
    try:
        return str(snapshot_download(repo_id=model_id, local_files_only=True))
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight combined local cache headroom for first Golden Candidate 1")
    parser.add_argument("--receipt", default="output/phase18_gpu_smoke/first-golden-cache-budget.json")
    parser.add_argument("--qwen-minimum-free-gib", type=float, default=12.0)
    parser.add_argument("--flux-minimum-free-gib", type=float, default=30.0)
    args = parser.parse_args()

    if _branch() != EXPECTED_BRANCH:
        raise RuntimeError("FIRST_GOLDEN_CACHE_BUDGET_BRANCH_BLOCKED")

    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise RuntimeError("huggingface_hub is required for first Golden cache-budget preflight") from exc

    cache_root = _cache_root()
    cache_root.mkdir(parents=True, exist_ok=True)
    qwen_cached = _cached_snapshot(snapshot_download, QWEN_MODEL_ID)
    flux_cached = _cached_snapshot(snapshot_download, FLUX2_KLEIN_4B_LOCAL.model_id)
    free_bytes = shutil.disk_usage(cache_root).free

    policy = FirstGoldenCacheBudgetPolicy(
        qwen_minimum_free_gib=args.qwen_minimum_free_gib,
        flux_minimum_free_gib=args.flux_minimum_free_gib,
    )
    decision = policy.evaluate(
        qwen_cached=qwen_cached is not None,
        flux_cached=flux_cached is not None,
        free_bytes=free_bytes,
    )
    policy.assert_eligible(decision)

    receipt = {
        "schema": "pul7sar-first-golden-cache-budget-v1",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "branch": EXPECTED_BRANCH,
        "cost_mode": "$0-local",
        "cache_root": str(cache_root),
        "qwen_model_id": QWEN_MODEL_ID,
        "flux_model_id": FLUX2_KLEIN_4B_LOCAL.model_id,
        "qwen_snapshot_path": qwen_cached,
        "flux_snapshot_path": flux_cached,
        "budget": asdict(decision),
        "ready": True,
        "downloads_performed": False,
        "generation_authorized": False,
        "queue_mutated": False,
        "png_created": False,
        "publication_ready": False,
    }

    target = Path(args.receipt)
    if not target.is_absolute():
        target = ROOT / target
    target = target.resolve()
    root = ROOT.resolve()
    if target != root and root not in target.parents:
        raise RuntimeError("FIRST_GOLDEN_CACHE_BUDGET_RECEIPT_ESCAPES_REPOSITORY")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
