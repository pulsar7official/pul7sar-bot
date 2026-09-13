#!/usr/bin/env python3
"""Load the exact pinned Qwen Image 2512 pipeline and run Change Set 260.

This command is intentionally generation-free: it instantiates the pinned
QwenImagePipeline in bfloat16, enables sequential CPU offload, emits the live
pipeline observation, and stops before any prompt is sent to the model.
"""
from __future__ import annotations

import argparse
import gc
from pathlib import Path
import sys


def _collect_pipeline_load_observation() -> dict:
    try:
        import torch
        import diffusers
        from diffusers import QwenImagePipeline
    except Exception as exc:  # pragma: no cover - runtime-host dependent
        raise RuntimeError(f"QWEN_PIPELINE_RECHECK_SOFTWARE_IMPORT_FAILED:{type(exc).__name__}") from exc

    from engine.intelligence.approved_model_revisions import (
        QWEN_IMAGE_2512_MODEL_ID,
        QWEN_IMAGE_2512_REVISION,
    )
    from engine.intelligence.qwen_image_runtime_envelope_plan import DTYPE, OFFLOAD_MODE

    if not torch.cuda.is_available():
        raise RuntimeError("QWEN_PIPELINE_RECHECK_CUDA_UNAVAILABLE")
    if not hasattr(torch.cuda, "is_bf16_supported") or not torch.cuda.is_bf16_supported():
        raise RuntimeError("QWEN_PIPELINE_RECHECK_NATIVE_BF16_UNAVAILABLE")

    device = torch.cuda.current_device()
    props = torch.cuda.get_device_properties(device)
    total_gib = float(props.total_memory) / float(1024 ** 3)

    pipeline = None
    try:
        pipeline = QwenImagePipeline.from_pretrained(
            QWEN_IMAGE_2512_MODEL_ID,
            revision=QWEN_IMAGE_2512_REVISION,
            torch_dtype=torch.bfloat16,
        )
        if pipeline.__class__.__name__ != "QwenImagePipeline":
            raise RuntimeError("QWEN_PIPELINE_RECHECK_PIPELINE_CLASS_INVALID")
        pipeline.enable_sequential_cpu_offload()
        return {
            "gpu_name": torch.cuda.get_device_name(device),
            "gpu_total_vram_gb": total_gib,
            "torch_version": str(torch.__version__),
            "cuda_version": str(torch.version.cuda),
            "diffusers_version": str(diffusers.__version__),
            "pipeline_class": pipeline.__class__.__name__,
            "dtype": DTYPE,
            "offload_mode": OFFLOAD_MODE,
            "native_bf16": True,
            "model_id": QWEN_IMAGE_2512_MODEL_ID,
            "model_revision": QWEN_IMAGE_2512_REVISION,
            "weights_loaded": True,
            "sequential_cpu_offload_enabled": True,
        }
    except Exception as exc:  # pragma: no cover - runtime-host dependent
        raise RuntimeError(f"QWEN_PIPELINE_RECHECK_LOAD_OR_OFFLOAD_FAILED:{type(exc).__name__}") from exc
    finally:
        if pipeline is not None:
            del pipeline
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live-host-recheck", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from engine.intelligence.qwen_image_live_pipeline_load_recheck import (
        build_live_pipeline_load_recheck,
    )

    observation = _collect_pipeline_load_observation()
    result = build_live_pipeline_load_recheck(
        args.live_host_recheck,
        observation,
        args.output_dir,
        repo_root=repo_root,
    )
    print(result.receipt_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
