#!/usr/bin/env python3
"""Prove the immutable local Qwen semantic model is cached before FLUX generation.

The command is zero-cost and never performs inference or downloads model bytes. It
requires the exact approved Qwen2.5-VL upstream revision to already exist in the
local Hugging Face cache, validates that snapshot, and emits a fail-closed receipt.
This prevents late semantic-model downloads or upstream drift from invalidating a
successful Golden base-scene generation.
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

from engine.intelligence.approved_model_revisions import (
    QWEN25_VL_3B_MODEL_ID,
    QWEN25_VL_3B_REVISION,
    assert_snapshot_revision,
)
from engine.intelligence.model_cache import ModelCachePolicy

MODEL_ID = QWEN25_VL_3B_MODEL_ID
MODEL_REVISION = QWEN25_VL_3B_REVISION
DEFAULT_MINIMUM_FREE_GIB = 12.0


def _cache_root() -> Path:
    hf_home = os.environ.get("HF_HOME")
    if hf_home:
        return Path(hf_home).expanduser().resolve()
    return (Path.home() / ".cache" / "huggingface").resolve()


def _require_cached_snapshot(snapshot_download, model_id: str, revision: str) -> str:
    """Resolve only an already-cached approved snapshot; never allow network fallback."""
    try:
        return str(
            snapshot_download(
                repo_id=model_id,
                revision=revision,
                local_files_only=True,
            )
        )
    except Exception as exc:
        raise RuntimeError(
            "QWEN_APPROVED_LOCAL_SNAPSHOT_REQUIRED: exact approved revision is not available in the local cache"
        ) from exc


def _assert_snapshot_complete(snapshot: Path) -> None:
    if not snapshot.is_dir():
        raise RuntimeError("cached Qwen snapshot did not resolve to an existing directory")
    if not (snapshot / "config.json").is_file():
        raise RuntimeError("cached Qwen snapshot is incomplete: config.json is missing")
    if not any(snapshot.rglob("*.safetensors")):
        raise RuntimeError("cached Qwen snapshot is incomplete: model safetensors are missing")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prove the immutable Phase 18 Qwen2.5-VL semantic model is already cached locally")
    parser.add_argument("--receipt", default="output/phase18_gpu_smoke/qwen-model-cache.json")
    parser.add_argument("--minimum-free-gib", type=float, default=DEFAULT_MINIMUM_FREE_GIB)
    args = parser.parse_args()

    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise RuntimeError("huggingface_hub is required for Phase 18 Qwen local-cache proof") from exc

    cache_root = _cache_root()
    cache_root.mkdir(parents=True, exist_ok=True)
    snapshot_path = _require_cached_snapshot(snapshot_download, MODEL_ID, MODEL_REVISION)
    free_bytes = shutil.disk_usage(cache_root).free
    policy = ModelCachePolicy(minimum_free_gib=args.minimum_free_gib)
    qualification = policy.evaluate(
        model_id=MODEL_ID,
        cached_snapshot_path=snapshot_path,
        free_bytes=free_bytes,
    )
    policy.assert_eligible(qualification)

    snapshot = Path(snapshot_path)
    _assert_snapshot_complete(snapshot)
    resolved_revision = assert_snapshot_revision(snapshot, MODEL_REVISION)
    files = [p for p in snapshot.rglob("*") if p.is_file()]
    apparent_bytes = sum(p.stat().st_size for p in files)
    receipt = {
        "schema": "pul7sar-phase18-qwen-model-cache-v2",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "provider_id": "huggingface-local-cache",
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "resolved_snapshot_revision": resolved_revision,
        "revision_pinned": True,
        "cost_mode": "$0-local",
        "snapshot_path": str(snapshot),
        "cache_root": str(cache_root),
        "downloaded_now": False,
        "network_download_authorized": False,
        "local_files_only": True,
        "file_count": len(files),
        "apparent_snapshot_gib": round(apparent_bytes / (1024 ** 3), 3),
        "qualification_before_download": asdict(qualification),
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
