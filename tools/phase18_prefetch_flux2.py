#!/usr/bin/env python3
"""Preflight and cache the approved FLUX.2 Klein snapshot before GPU generation.

The command never generates an image and never selects a paid inference provider.
It proves that the approved model is already cached or that the cache filesystem
has enough free space, then uses Hugging Face Hub only to download the exact
open-weight repository used by Phase 18. A machine-readable receipt is written
for later GPU-smoke evidence.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.model_cache import ModelCachePolicy
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


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
    parser = argparse.ArgumentParser(description="Prefetch the approved Phase 18 FLUX.2 Klein model snapshot")
    parser.add_argument("--receipt", default="output/phase18_gpu_smoke/model-cache.json")
    parser.add_argument("--minimum-free-gib", type=float, default=30.0)
    args = parser.parse_args()

    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise RuntimeError("huggingface_hub is required for Phase 18 model prefetch") from exc

    cache_root = _cache_root()
    cache_root.mkdir(parents=True, exist_ok=True)
    cached = _cached_snapshot(snapshot_download, FLUX2_KLEIN_4B_LOCAL.model_id)
    free_bytes = shutil.disk_usage(cache_root).free
    policy = ModelCachePolicy(minimum_free_gib=args.minimum_free_gib)
    before = policy.evaluate(
        model_id=FLUX2_KLEIN_4B_LOCAL.model_id,
        cached_snapshot_path=cached,
        free_bytes=free_bytes,
    )
    policy.assert_eligible(before)

    downloaded = False
    snapshot_path = cached
    if snapshot_path is None:
        snapshot_path = str(snapshot_download(repo_id=FLUX2_KLEIN_4B_LOCAL.model_id))
        downloaded = True

    snapshot = Path(snapshot_path)
    if not snapshot.is_dir():
        raise RuntimeError("Hugging Face snapshot download did not return an existing directory")
    if not (snapshot / "model_index.json").is_file():
        raise RuntimeError("cached FLUX.2 snapshot is incomplete: model_index.json is missing")

    files = [p for p in snapshot.rglob("*") if p.is_file()]
    apparent_bytes = sum(p.stat().st_size for p in files)
    receipt = {
        "schema": "pul7sar-phase18-model-cache-v1",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "provider_id": FLUX2_KLEIN_4B_LOCAL.provider_id,
        "model_id": FLUX2_KLEIN_4B_LOCAL.model_id,
        "license_id": FLUX2_KLEIN_4B_LOCAL.license_id,
        "cost_mode": "$0-local",
        "snapshot_path": str(snapshot),
        "cache_root": str(cache_root),
        "downloaded_now": downloaded,
        "file_count": len(files),
        "apparent_snapshot_gib": round(apparent_bytes / (1024 ** 3), 3),
        "qualification_before_download": asdict(before),
        "ready": True,
    }

    receipt_path = Path(args.receipt)
    if not receipt_path.is_absolute():
        receipt_path = ROOT / receipt_path
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
