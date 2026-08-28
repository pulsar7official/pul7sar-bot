#!/usr/bin/env python3
"""Measure whether a host is worth spending a Qwen Image 2512 local trial on.

This command never downloads or loads model weights and never authorizes image
generation. It only proves observable host/runtime/cache prerequisites for a
future measured $0-local runtime-floor experiment against the exact pinned
Qwen Image 2512 revision.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.approved_model_revisions import QWEN_IMAGE_2512_MODEL_ID, QWEN_IMAGE_2512_REVISION
from engine.intelligence.host_memory_qualification import HostMemoryQualificationProbe
from engine.intelligence.local_runtime import LocalRuntimeProbe
from engine.intelligence.qwen_image_measurement_admission import (
    evaluate_measurement_admission,
    verify_declaration,
)


def _repo_path(path: str) -> Path:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = ROOT / resolved
    resolved = resolved.resolve()
    if not resolved.is_relative_to(ROOT.resolve()):
        raise RuntimeError(f"QWEN_IMAGE_MEASUREMENT_PATH_ESCAPE: {resolved}")
    return resolved


def _cache_root() -> Path:
    hf_home = os.environ.get("HF_HOME")
    if hf_home:
        return Path(hf_home).expanduser().resolve()
    return (Path.home() / ".cache" / "huggingface").resolve()


def _find_exact_cached_snapshot() -> str | None:
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        return None
    try:
        return str(snapshot_download(repo_id=QWEN_IMAGE_2512_MODEL_ID, revision=QWEN_IMAGE_2512_REVISION, local_files_only=True))
    except Exception:
        return None


def _diffusers_probe() -> tuple[str | None, bool]:
    try:
        import diffusers
    except ImportError:
        return None, False
    version = str(getattr(diffusers, "__version__", "") or "") or None
    pipeline_available = getattr(diffusers, "QwenImagePipeline", None) is not None
    return version, pipeline_available


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight a host for a future measured Qwen Image 2512 local trial")
    parser.add_argument("--declaration", required=True, help="Pinned explicit-local-candidate declaration JSON")
    parser.add_argument("--receipt", default="output/phase18_gpu_smoke/qwen-image-2512-measurement-admission.json")
    args = parser.parse_args()

    declaration_path = _repo_path(args.declaration)
    declaration = json.loads(declaration_path.read_text(encoding="utf-8"))
    declaration_sha = verify_declaration(declaration)

    runtime = LocalRuntimeProbe().detect()
    host_memory = HostMemoryQualificationProbe().inspect()
    diffusers_version, pipeline_available = _diffusers_probe()
    cache_root = _cache_root()
    cache_root.mkdir(parents=True, exist_ok=True)
    cache_free_gib = shutil.disk_usage(cache_root).free / (1024 ** 3)
    cached_snapshot = _find_exact_cached_snapshot()

    admission = evaluate_measurement_admission(
        runtime=runtime,
        host_memory=host_memory,
        diffusers_version=diffusers_version,
        qwen_image_pipeline_available=pipeline_available,
        exact_snapshot_path=cached_snapshot,
        cache_free_gib=cache_free_gib,
        repository_gib=float(declaration.get("local_repository_size_gb") or 57.7),
    )
    receipt = admission.as_receipt(declaration_sha256=declaration_sha)
    receipt["declaration_path"] = str(declaration_path)
    receipt["cache_root"] = str(cache_root)

    receipt_path = _repo_path(args.receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if admission.measurement_ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
