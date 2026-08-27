#!/usr/bin/env python3
"""Preflight and cache the approved FLUX.2 Klein snapshot before GPU generation.

The command never generates an image and never selects a paid inference provider.
It proves that the exact approved immutable model revision is already cached or
that the cache filesystem has enough free space, then uses Hugging Face Hub only
to download that pinned open-weight revision. After the approved snapshot exists,
it also rechecks live filesystem headroom so Candidate 1 never begins with a
model cache that has consumed nearly all remaining local storage. A machine-
readable receipt is written for later GPU-smoke evidence.
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
    FLUX2_KLEIN_4B_MODEL_ID,
    FLUX2_KLEIN_4B_REVISION,
    assert_snapshot_revision,
)
from engine.intelligence.model_cache import ModelCachePolicy
from engine.intelligence.model_cache_headroom import ModelCacheHeadroomPolicy
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


def _cache_root() -> Path:
    hf_home = os.environ.get("HF_HOME")
    if hf_home:
        return Path(hf_home).expanduser().resolve()
    return (Path.home() / ".cache" / "huggingface").resolve()


def _cached_snapshot(snapshot_download, model_id: str, revision: str) -> str | None:
    try:
        return str(
            snapshot_download(
                repo_id=model_id,
                revision=revision,
                local_files_only=True,
            )
        )
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Prefetch the approved Phase 18 FLUX.2 Klein model snapshot")
    parser.add_argument("--receipt", default="output/phase18_gpu_smoke/model-cache.json")
    parser.add_argument("--minimum-free-gib", type=float, default=30.0)
    parser.add_argument(
        "--minimum-working-free-gib",
        type=float,
        default=8.0,
        help="Minimum live cache-filesystem headroom that must remain after the pinned snapshot is ready",
    )
    args = parser.parse_args()

    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise RuntimeError("huggingface_hub is required for Phase 18 model prefetch") from exc

    if FLUX2_KLEIN_4B_LOCAL.model_id != FLUX2_KLEIN_4B_MODEL_ID:
        raise RuntimeError("approved FLUX model identity drift between model profile and revision lock")

    cache_root = _cache_root()
    cache_root.mkdir(parents=True, exist_ok=True)
    cached = _cached_snapshot(
        snapshot_download,
        FLUX2_KLEIN_4B_LOCAL.model_id,
        FLUX2_KLEIN_4B_REVISION,
    )
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
        snapshot_path = str(
            snapshot_download(
                repo_id=FLUX2_KLEIN_4B_LOCAL.model_id,
                revision=FLUX2_KLEIN_4B_REVISION,
            )
        )
        downloaded = True

    snapshot = Path(snapshot_path)
    if not snapshot.is_dir():
        raise RuntimeError("Hugging Face snapshot download did not return an existing directory")
    resolved_revision = assert_snapshot_revision(snapshot, FLUX2_KLEIN_4B_REVISION)
    if not (snapshot / "model_index.json").is_file():
        raise RuntimeError("cached FLUX.2 snapshot is incomplete: model_index.json is missing")

    # The pre-download budget is not a reservation. Re-check the actual live
    # filesystem after the exact pinned snapshot exists so concurrent disk use,
    # cache expansion, or an unexpectedly large snapshot cannot leave Candidate
    # 1 without a conservative local working-space floor.
    post_cache_free_bytes = shutil.disk_usage(cache_root).free
    headroom_policy = ModelCacheHeadroomPolicy(minimum_working_free_gib=args.minimum_working_free_gib)
    after = headroom_policy.evaluate(free_bytes=post_cache_free_bytes)
    headroom_policy.assert_eligible(after)

    files = [p for p in snapshot.rglob("*") if p.is_file()]
    apparent_bytes = sum(p.stat().st_size for p in files)
    receipt = {
        "schema": "pul7sar-phase18-model-cache-v2",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "provider_id": FLUX2_KLEIN_4B_LOCAL.provider_id,
        "model_id": FLUX2_KLEIN_4B_LOCAL.model_id,
        "model_revision": FLUX2_KLEIN_4B_REVISION,
        "resolved_snapshot_revision": resolved_revision,
        "license_id": FLUX2_KLEIN_4B_LOCAL.license_id,
        "cost_mode": "$0-local",
        "snapshot_path": str(snapshot),
        "cache_root": str(cache_root),
        "downloaded_now": downloaded,
        "file_count": len(files),
        "apparent_snapshot_gib": round(apparent_bytes / (1024 ** 3), 3),
        "qualification_before_download": asdict(before),
        "working_headroom_after_cache": asdict(after),
        "working_headroom_ready": True,
        "revision_pinned": True,
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
