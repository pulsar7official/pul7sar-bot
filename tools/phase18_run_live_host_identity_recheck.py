#!/usr/bin/env python3
"""Collect a no-weight live CUDA/software observation and run Change Set 259.

This command intentionally imports the QwenImagePipeline class but never instantiates
it and never loads model weights.  It therefore cannot authorize or execute canonical
generation.  A compatible CUDA host is required for a successful observation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


def _collect_observation() -> dict:
    try:
        import torch
        import diffusers
        from diffusers import QwenImagePipeline
    except Exception as exc:  # pragma: no cover - runtime-host dependent
        raise RuntimeError(f"QWEN_LIVE_HOST_RECHECK_SOFTWARE_IMPORT_FAILED:{type(exc).__name__}") from exc

    if QwenImagePipeline.__name__ != "QwenImagePipeline":
        raise RuntimeError("QWEN_LIVE_HOST_RECHECK_PIPELINE_CLASS_UNAVAILABLE")
    if not torch.cuda.is_available():
        raise RuntimeError("QWEN_LIVE_HOST_RECHECK_CUDA_UNAVAILABLE")
    if not hasattr(torch.cuda, "is_bf16_supported") or not torch.cuda.is_bf16_supported():
        raise RuntimeError("QWEN_LIVE_HOST_RECHECK_NATIVE_BF16_UNAVAILABLE")

    device = torch.cuda.current_device()
    props = torch.cuda.get_device_properties(device)
    total_gib = float(props.total_memory) / float(1024 ** 3)
    return {
        "gpu_name": torch.cuda.get_device_name(device),
        "gpu_total_vram_gb": total_gib,
        "torch_version": str(torch.__version__),
        "cuda_version": str(torch.version.cuda),
        "diffusers_version": str(diffusers.__version__),
        "native_bf16": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--observation-json",
        type=Path,
        help="Test/forensic override. Production live-host runs should omit this and collect locally.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from engine.intelligence.qwen_image_live_host_identity_recheck import (
        build_live_host_identity_recheck,
    )

    if args.observation_json is None:
        observation = _collect_observation()
    else:
        path = args.observation_json
        if path.is_symlink() or not path.is_file():
            raise ValueError("QWEN_LIVE_HOST_RECHECK_OBSERVATION_FILE_INVALID")
        observation = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(observation, dict):
            raise ValueError("QWEN_LIVE_HOST_RECHECK_OBSERVATION_FILE_INVALID")

    result = build_live_host_identity_recheck(
        args.request,
        observation,
        args.output_dir,
        repo_root=repo_root,
    )
    print(result.receipt_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
