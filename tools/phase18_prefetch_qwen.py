#!/usr/bin/env python3
"""Prefetch the exact local Qwen semantic model before FLUX GPU generation.

The command is zero-cost and never performs inference. It proves that the exact
Qwen2.5-VL snapshot is already cached or that the Hugging Face cache filesystem
has conservative free-space headroom, then downloads only the approved model
repository. This prevents a late semantic-model download from consuming the
post-FLUX inspection timeout or turning a successful base-scene generation into
an avoidable runtime failure.
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
from engine.intelligence.qwen25_vl_inspector import MODEL_ID

DEFAULT_MINIMUM_FREE_GIB = 12.0


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


def _assert_snapshot_complete(snapshot: Path) -> None:
    if not snapshot.is_dir():
        raise RuntimeError("Qwen snapshot download did not return an existing directory")
    if not (snapshot / "config.json").is_file():
        raise RuntimeError("cached Qwen snapshot is incomplete: config.json is missing")
    if not any(snapshot.rglob("*.safetensors")):
        raise RuntimeError("cached Qwen snapshot is incomplete: model safetensors are missing")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prefetch the exact Phase 18 Qwen2.5-VL semantic model")
    parser.add_argument("--receipt", default="output/phase18_gpu_smoke/qwen-model-cache.json")
    parser.add_argument("--minimum-free-gib", type=float, default=DEFAULT_MINIMUM_FREE_GIB)
    args = parser.parse_args()

    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise RuntimeError("huggingface_hub is required for Phase 18 Qwen model prefetch") from exc

    cache_root = _cache_root()
    cache_root.mkdir(parents=True, exist_ok=True)
    cached = _cached_snapshot(snapshot_download, MODEL_ID)
    free_bytes = shutil.disk_usage(cache_root).free
    policy = ModelCachePolicy(minimum_free_gib=args.minimum_free_gib)
    before = policy.evaluate(model_id=MODEL_ID, cached_snapshot_path=cached, free_bytes=free_bytes)
    policy.assert_eligible(before)

    downloaded = False
    snapshot_path = cached
    if snapshot_path is None:
        snapshot_path = str(snapshot_download(repo_id=MODEL_ID))
        downloaded = True

    snapshot = Path(snapshot_path)
    _assert_snapshot_complete(snapshot)
    files = [p for p in snapshot.rglob("*") if p.is_file()]
    apparent_bytes = sum(p.stat().st_size for p in files)
    receipt = {
        "schema": "pul7sar-phase18-qwen-model-cache-v1",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "provider_id": "huggingface-local-cache",
        "model_id": MODEL_ID,
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
