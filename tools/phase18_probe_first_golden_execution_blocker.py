#!/usr/bin/env python3
"""Non-authoritative, zero-cost probe for the first genuine Golden v6 execution blocker.

This command performs no downloads, model loading, generation, queue mutation, or
publication. It only reports whether the current host exposes the minimum runtime,
live GPU/host-memory/filesystem headroom, and exact local-cache prerequisites needed
before the authoritative Golden gates can be attempted.
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
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.approved_model_revisions import (
    FLUX2_KLEIN_4B_MODEL_ID,
    FLUX2_KLEIN_4B_REVISION,
    QWEN25_VL_3B_MODEL_ID,
    QWEN25_VL_3B_REVISION,
    assert_snapshot_revision,
)
from engine.intelligence.gpu_host_qualification import GpuHostQualificationPolicy
from engine.intelligence.host_memory_qualification import HostMemoryQualificationProbe
from engine.intelligence.local_runtime import LocalRuntimeProbe
from engine.intelligence.model_cache_headroom import ModelCacheHeadroomPolicy
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL

EXPECTED_BRANCH = "phase18/story-intelligence"
SnapshotResolver = Callable[[Path, str, str], Path | None]


def _cache_root(env: dict[str, str] | None = None, home: Path | None = None) -> Path:
    values = os.environ if env is None else env
    if values.get("HF_HUB_CACHE"):
        return Path(values["HF_HUB_CACHE"]).expanduser().resolve()
    if values.get("HF_HOME"):
        return (Path(values["HF_HOME"]).expanduser() / "hub").resolve()
    base = Path.home() if home is None else home
    return (base / ".cache" / "huggingface" / "hub").resolve()


def _snapshot_path(cache_root: Path, model_id: str, revision: str) -> Path:
    owner, repo = model_id.split("/", 1)
    return cache_root / f"models--{owner}--{repo}" / "snapshots" / revision


def _resolve_local_snapshot(cache_root: Path, model_id: str, revision: str) -> Path | None:
    """Resolve an exact immutable snapshot using Hugging Face local-only semantics.

    Directory presence alone is intentionally insufficient: ``snapshot_download``
    must be able to resolve the approved revision without network access, matching
    the authoritative model-cache preflights used later in the Golden path.
    """
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        return None

    try:
        snapshot = Path(
            snapshot_download(
                repo_id=model_id,
                revision=revision,
                cache_dir=str(cache_root),
                local_files_only=True,
            )
        ).resolve()
        assert_snapshot_revision(snapshot, revision)
    except Exception:
        return None
    return snapshot


def _gpu_qualification() -> dict[str, object]:
    """Reuse the authoritative live-VRAM/BF16 GPU policy without mutating the host."""
    try:
        runtime = LocalRuntimeProbe().detect()
        return GpuHostQualificationPolicy().evaluate(
            runtime=runtime,
            model=FLUX2_KLEIN_4B_LOCAL,
        ).as_dict()
    except Exception as exc:
        return {
            "eligible": False,
            "reasons": [f"gpu_qualification_probe_failed:{type(exc).__name__}"],
            "cost_mode": "$0-local",
        }


def _host_memory_qualification() -> dict[str, object]:
    """Reuse the authoritative available-system-RAM policy without model loading."""
    try:
        return asdict(HostMemoryQualificationProbe().inspect())
    except Exception as exc:
        return {
            "ready": False,
            "reasons": [f"host_memory_probe_failed:{type(exc).__name__}"],
            "cost_mode": "$0-local",
        }


def _cache_headroom_qualification(cache_root: Path) -> dict[str, object]:
    """Reuse the approved post-cache working-space floor before heavy execution."""
    try:
        anchor = cache_root if cache_root.exists() else cache_root.parent
        while not anchor.exists() and anchor != anchor.parent:
            anchor = anchor.parent
        free_bytes = shutil.disk_usage(anchor).free
        return asdict(ModelCacheHeadroomPolicy().evaluate(free_bytes=free_bytes))
    except Exception as exc:
        return {
            "eligible": False,
            "reason": f"cache_headroom_probe_failed:{type(exc).__name__}",
            "free_bytes": None,
            "free_gib": None,
            "minimum_working_free_gib": 8.0,
        }


def inspect(
    *,
    env: dict[str, str] | None = None,
    home: Path | None = None,
    torch_module=None,
    snapshot_resolver: SnapshotResolver | None = None,
    gpu_qualification_report: dict[str, object] | None = None,
    host_memory_report: dict[str, object] | None = None,
    cache_headroom_report: dict[str, object] | None = None,
) -> dict[str, object]:
    values = dict(os.environ if env is None else env)
    blockers: list[str] = []

    if values.get("HF_HUB_OFFLINE") != "1":
        blockers.append("HF_HUB_OFFLINE_NOT_1")
    if values.get("TRANSFORMERS_OFFLINE") != "1":
        blockers.append("TRANSFORMERS_OFFLINE_NOT_1")
    if values.get("PUL7SAR_PHASE18_COST_MODE") != "$0-local":
        blockers.append("ZERO_COST_MODE_NOT_ASSERTED")

    torch_obj = torch_module
    if torch_obj is None:
        try:
            import torch as torch_obj  # type: ignore
        except Exception:
            torch_obj = None
    cuda_available = bool(torch_obj is not None and torch_obj.cuda.is_available())
    cuda_runtime = getattr(getattr(torch_obj, "version", None), "cuda", None) if torch_obj is not None else None
    device_count = int(torch_obj.cuda.device_count()) if cuda_available else 0
    bf16_fn = getattr(torch_obj.cuda, "is_bf16_supported", None) if torch_obj is not None else None
    bf16_supported = bool(cuda_available and callable(bf16_fn) and bf16_fn())
    if not cuda_available:
        blockers.append("CUDA_UNAVAILABLE")
    if cuda_runtime is None:
        blockers.append("CUDA_RUNTIME_UNAVAILABLE")
    if device_count < 1:
        blockers.append("CUDA_DEVICE_MISSING")
    if not bf16_supported:
        blockers.append("NATIVE_BF16_UNAVAILABLE")

    gpu_qualification = dict(
        _gpu_qualification() if gpu_qualification_report is None else gpu_qualification_report
    )
    if gpu_qualification.get("eligible") is not True:
        blockers.append("GPU_HOST_NOT_GOLDEN_QUALIFIED")
    if gpu_qualification.get("cost_mode") != "$0-local":
        blockers.append("GPU_QUALIFICATION_ZERO_COST_DRIFT")

    host_memory = dict(
        _host_memory_qualification() if host_memory_report is None else host_memory_report
    )
    if host_memory.get("ready") is not True:
        blockers.append("HOST_MEMORY_NOT_READY")
    if host_memory.get("cost_mode") != "$0-local":
        blockers.append("HOST_MEMORY_ZERO_COST_DRIFT")

    cache_root = _cache_root(values, home)
    qwen_snapshot_expected = _snapshot_path(cache_root, QWEN25_VL_3B_MODEL_ID, QWEN25_VL_3B_REVISION)
    flux_snapshot_expected = _snapshot_path(cache_root, FLUX2_KLEIN_4B_MODEL_ID, FLUX2_KLEIN_4B_REVISION)
    resolver = _resolve_local_snapshot if snapshot_resolver is None else snapshot_resolver
    qwen_snapshot_resolved = resolver(cache_root, QWEN25_VL_3B_MODEL_ID, QWEN25_VL_3B_REVISION)
    flux_snapshot_resolved = resolver(cache_root, FLUX2_KLEIN_4B_MODEL_ID, FLUX2_KLEIN_4B_REVISION)
    qwen_cached = qwen_snapshot_resolved is not None
    flux_cached = flux_snapshot_resolved is not None
    if not qwen_cached:
        blockers.append("QWEN_APPROVED_SNAPSHOT_MISSING")
    if not flux_cached:
        blockers.append("FLUX_APPROVED_SNAPSHOT_MISSING")

    cache_headroom = dict(
        _cache_headroom_qualification(cache_root)
        if cache_headroom_report is None
        else cache_headroom_report
    )
    if cache_headroom.get("eligible") is not True:
        blockers.append("CACHE_WORKING_HEADROOM_NOT_READY")

    disk_free_gib = cache_headroom.get("free_gib")
    if isinstance(disk_free_gib, bool) or not isinstance(disk_free_gib, (int, float)):
        disk_free_gib = None
        if "CACHE_WORKING_HEADROOM_NOT_READY" not in blockers:
            blockers.append("CACHE_FILESYSTEM_UNREADABLE")

    return {
        "schema": "pul7sar-phase18-first-golden-execution-blocker-probe-v4",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "branch_required": EXPECTED_BRANCH,
        "cost_mode_required": "$0-local",
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
        "offline": {
            "hf_hub_offline": values.get("HF_HUB_OFFLINE") == "1",
            "transformers_offline": values.get("TRANSFORMERS_OFFLINE") == "1",
        },
        "runtime": {
            "cuda_available": cuda_available,
            "cuda_runtime": cuda_runtime,
            "cuda_device_count": device_count,
            "native_bf16": bf16_supported,
        },
        "gpu_qualification": gpu_qualification,
        "host_memory": host_memory,
        "cache_headroom": cache_headroom,
        "cache": {
            "root": str(cache_root),
            "disk_free_gib": disk_free_gib,
            "resolution_mode": "huggingface-local-files-only",
            "qwen_model_id": QWEN25_VL_3B_MODEL_ID,
            "qwen_model_revision": QWEN25_VL_3B_REVISION,
            "qwen_snapshot_path": str(qwen_snapshot_expected),
            "qwen_snapshot_directory_present": qwen_snapshot_expected.is_dir(),
            "qwen_resolved_snapshot_path": str(qwen_snapshot_resolved) if qwen_snapshot_resolved is not None else None,
            "qwen_cached": qwen_cached,
            "flux_model_id": FLUX2_KLEIN_4B_MODEL_ID,
            "flux_model_revision": FLUX2_KLEIN_4B_REVISION,
            "flux_snapshot_path": str(flux_snapshot_expected),
            "flux_snapshot_directory_present": flux_snapshot_expected.is_dir(),
            "flux_resolved_snapshot_path": str(flux_snapshot_resolved) if flux_snapshot_resolved is not None else None,
            "flux_cached": flux_cached,
        },
        "ready_for_authoritative_golden_preflight": not blockers,
        "blockers": blockers,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Report the exact local blocker before first genuine Golden v6 execution")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = inspect()
    rendered = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        target = args.output if args.output.is_absolute() else ROOT / args.output
        target = target.resolve()
        root = ROOT.resolve()
        if target != root and root not in target.parents:
            raise RuntimeError("FIRST_GOLDEN_BLOCKER_PROBE_OUTPUT_ESCAPES_REPOSITORY")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if payload["ready_for_authoritative_golden_preflight"] else 2


if __name__ == "__main__":
    raise SystemExit(main())